"""Test unexecuted labeling jobs, provenance checks, and split preservation."""
import copy
import hashlib

import pytest

from error_pattern_recognition.grading.label_jobs import build_label_job, stable_hash


def _sample(tmp_path):
    marker = tmp_path / "must_not_execute"
    code = f"open({str(marker)!r}, 'w').write('bad')\ndef f(x):\n    return x + 1\n"
    source = {"task_id": 601, "prompt": "Add one", "code": code,
              "test_list": ["assert f(1) == 2", "assert f(-1) == 0"], "test_imports": []}
    candidate = {"candidate_id": "mbpp-601-mutant-1", "task_id": 601, "exercise_id": "mbpp-601",
                 "split": "train", "prompt": source["prompt"], "reference_solution": code,
                 "source_assertions": source["test_list"], "source_test_imports": [],
                 "function_name": "f", "student_code": code, "candidate_kind": "single_operator_mutation"}
    return source, candidate, marker


def test_job_is_reproducible_unexecuted_and_unscored(tmp_path):
    source, candidate, marker = _sample(tmp_path)
    job, reason = build_label_job(candidate, source)
    assert not marker.exists() and reason is None
    assert job["label_status"] == "unscored" and job["teacher_approved"] is False
    assert job["reference_validation_required"] is True
    assert len(job["tests"]) == 2 and job["split"] == "train"
    assert job["candidate_sha256"] == hashlib.sha256(candidate["student_code"].encode()).hexdigest()
    assert job["tests_sha256"] == stable_hash(job["tests"])
    body = {key: value for key, value in job.items() if key != "job_sha256"}
    assert job["job_sha256"] == stable_hash(body)
    assert build_label_job(candidate, source)[0] == job


def test_complex_and_imported_tests_are_excluded(tmp_path):
    source, candidate, _ = _sample(tmp_path)
    source["test_list"] = ["assert set(f([1])) == {2}"]
    candidate["source_assertions"] = source["test_list"]
    assert build_label_job(candidate, source) == (None, "ambiguous_or_mismatched_entry_point")
    source, candidate, _ = _sample(tmp_path)
    source["test_imports"] = ["import math"]
    candidate["source_test_imports"] = source["test_imports"]
    assert build_label_job(candidate, source) == (None, "test_imports_not_supported")


def test_provenance_and_split_tampering_is_rejected(tmp_path):
    source, candidate, _ = _sample(tmp_path)
    candidate = copy.deepcopy(candidate)
    candidate["split"] = "test"
    with pytest.raises(ValueError, match="provenance mismatch"):
        build_label_job(candidate, source)


def test_reference_copy_must_match_source_even_if_candidate_is_rehashed(tmp_path):
    source, candidate, _ = _sample(tmp_path)
    candidate["candidate_kind"] = "reference_copy"
    candidate["student_code"] = "def f(x): return 42"
    with pytest.raises(ValueError, match="does not match"):
        build_label_job(candidate, source)
