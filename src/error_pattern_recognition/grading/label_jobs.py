"""Prepare unexecuted research labeling jobs from MBPP and static candidates."""
from __future__ import annotations

import ast
import hashlib
import json
from typing import Any

from error_pattern_recognition.grading.mbpp_drafts import mbpp_to_draft
from error_pattern_recognition.grading.independent_cases import independent_cases


def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def expected_split(task_id: int) -> str:
    if 1 <= task_id <= 10:
        return "prompt"
    if 11 <= task_id <= 510:
        return "test"
    if 511 <= task_id <= 600:
        return "validation"
    if 601 <= task_id <= 974:
        return "train"
    raise ValueError(f"Invalid MBPP task ID: {task_id}")


def build_label_job(candidate: dict[str, Any], source: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Build a research job or return a reason for excluding an unsupported task.

    This routine never executes code and does not assert reference correctness,
    teacher approval, or student-grade validity.
    """
    task_id = source.get("task_id")
    if not isinstance(task_id, int) or isinstance(task_id, bool):
        raise ValueError("Source task ID must be an integer.")
    expected = expected_split(task_id)
    required = {"task_id": task_id, "exercise_id": f"mbpp-{task_id}", "split": expected,
                "prompt": source.get("prompt"), "reference_solution": source.get("code"),
                "source_assertions": source.get("test_list"), "source_test_imports": source.get("test_imports")}
    if (not isinstance(candidate, dict) or not isinstance(candidate.get("task_id"), int)
            or isinstance(candidate.get("task_id"), bool)
            or any(candidate.get(key) != value for key, value in required.items())):
        raise ValueError(f"Candidate/source provenance mismatch for task {task_id}.")
    candidate_id, code = candidate.get("candidate_id"), candidate.get("student_code")
    if not isinstance(candidate_id, str) or not candidate_id.strip() or not isinstance(code, str) or not code.strip():
        raise ValueError("Candidate must have an ID and nonempty source code.")
    if len(code.encode("utf-8")) > 128 * 1024:
        return None, "candidate_code_too_large"
    if candidate.get("candidate_kind") not in {"reference_copy", "single_operator_mutation"}:
        raise ValueError("Candidate kind must identify the synthetic generation method.")
    if candidate["candidate_kind"] == "reference_copy":
        try:
            reference_ast = ast.dump(ast.parse(source["code"]), include_attributes=False)
            candidate_ast = ast.dump(ast.parse(code), include_attributes=False)
        except (SyntaxError, ValueError, RecursionError) as exc:
            raise ValueError("Reference copy must parse as Python source.") from exc
        if reference_ast != candidate_ast:
            raise ValueError("Reference copy does not match the source reference.")
    draft = mbpp_to_draft(source)
    if not draft["function_name"] or candidate.get("function_name") != draft["function_name"]:
        return None, "ambiguous_or_mismatched_entry_point"
    conversion = draft["conversion"]
    if not conversion["original_count"] or conversion["converted_count"] != conversion["original_count"]:
        return None, "unsupported_assertions"
    if source["test_imports"]:
        return None, "test_imports_not_supported"
    supplemental = independent_cases(source)
    tests = draft["tests"] + supplemental
    if len(tests) > 64:
        return None, "too_many_tests"
    job = {
        "schema_version": 1, "job_id": candidate_id, "exercise_id": draft["exercise_id"],
        "task_id": task_id, "split": expected, "function_name": draft["function_name"],
        "candidate_code": code, "candidate_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
        "candidate_kind": candidate["candidate_kind"],
        "tests": tests, "tests_sha256": stable_hash(tests),
        "test_provenance": {"source_assertions": len(draft["tests"]),
                            "independently_authored": len(supplemental)},
        "label_status": "unscored", "research_only": True, "teacher_approved": False,
        "reference_validation_required": True,
        "source_url": draft["source"]["url"], "attribution": draft["source"]["attribution"],
    }
    job["job_sha256"] = stable_hash(job)
    return job, None
