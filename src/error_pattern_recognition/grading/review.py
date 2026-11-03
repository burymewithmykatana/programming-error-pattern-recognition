"""Build teacher review records from grading evidence; never execute code."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from typing import Any

from error_pattern_recognition.grading.scoring import score_test_results


def _hash_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_review(record: dict[str, Any]) -> dict[str, Any]:
    """Recalculate points and join recorded outcomes to the exercise tests."""
    if not isinstance(record, dict) or not isinstance(record.get("submission_id"), str) or not record["submission_id"].strip():
        raise ValueError("Record must contain a nonempty submission_id.")
    if not isinstance(record.get("student_code"), str):
        raise ValueError("Record must contain student_code text.")
    exercise = record.get("exercise")
    outcomes = record.get("outcomes")
    score = score_test_results(exercise, outcomes)
    by_id = {item["test_id"].strip(): item for item in outcomes}
    evidence = []
    for test, detail in zip(exercise["tests"], score["tests"], strict=True):
        outcome = by_id.get(detail["test_id"], {})
        evidence.append({**detail, "input": test.get("input"), "expected": test.get("expected"),
                         "actual": outcome.get("actual"), "error_type": outcome.get("error_type")})
    return {"submission_id": record["submission_id"], "exercise_id": exercise.get("exercise_id"),
            "exercise_sha256": _hash_json(exercise),
            "student_code_sha256": hashlib.sha256(record["student_code"].encode("utf-8")).hexdigest(),
            "provenance": record.get("provenance", "unspecified"),
            "maximum_points": score["maximum_points"], "suggested_points": score["suggested_points"],
            "incomplete_test_ids": score["incomplete_test_ids"], "teacher_review_required": True,
            "evidence": evidence}


def finalize_review(report: dict[str, Any], teacher_points: Any, feedback: str) -> dict[str, Any]:
    """Record a teacher decision; a changed or manual score needs an explanation."""
    if isinstance(teacher_points, bool):
        raise ValueError("Teacher points must be a finite number within the rubric range.")
    try:
        points = Decimal(str(teacher_points))
        maximum = Decimal(report["maximum_points"])
    except (InvalidOperation, KeyError, TypeError) as exc:
        raise ValueError("Teacher points must be a finite number within the rubric range.") from exc
    if not points.is_finite() or points < 0 or points > maximum:
        raise ValueError("Teacher points must be a finite number within the rubric range.")
    if not isinstance(feedback, str):
        raise ValueError("Feedback must be text.")
    suggested = report.get("suggested_points")
    changed = suggested is None or points != Decimal(suggested)
    if changed and not feedback.strip():
        raise ValueError("Explain a changed or manually assigned score.")
    return {**report, "teacher_review_required": False, "teacher_points": str(points),
            "teacher_changed_score": changed, "teacher_feedback": feedback.strip()}
