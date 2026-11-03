"""Test teacher review calculations and exported decisions."""
import pytest

from error_pattern_recognition.grading import build_review, finalize_review


def _record():
    return {"submission_id": "s-1", "student_code": "def add(a, b): return a - b",
            "exercise": {"exercise_id": "add", "tests": [
                {"test_id": "positive", "input": [2, 3], "expected": 5, "points": 2},
                {"test_id": "negative", "input": [-1, 2], "expected": 1, "points": 3}]},
            "outcomes": [{"test_id": "positive", "status": "failed", "actual": -1},
                         {"test_id": "negative", "status": "passed", "actual": 1}],
            "score": {"suggested_points": "999"}, "provenance": "synthetic"}


def test_review_recalculates_points_and_joins_evidence():
    report = build_review(_record())
    assert report["suggested_points"] == "3"
    assert report["maximum_points"] == "5"
    assert report["evidence"][0]["expected"] == 5
    assert report["evidence"][0]["actual"] == -1
    assert len(report["exercise_sha256"]) == len(report["student_code_sha256"]) == 64


def test_teacher_override_requires_reason_and_stays_in_range():
    report = build_review(_record())
    with pytest.raises(ValueError, match="Explain"):
        finalize_review(report, 4, " ")
    with pytest.raises(ValueError, match="rubric range"):
        finalize_review(report, 6, "reason")
    decision = finalize_review(report, 4, "Partial credit for the approach")
    assert decision["teacher_points"] == "4"
    assert decision["teacher_changed_score"] is True
    assert decision["teacher_review_required"] is False


def test_incomplete_results_allow_only_explained_manual_decision():
    record = _record()
    record["outcomes"] = record["outcomes"][:1]
    report = build_review(record)
    assert report["suggested_points"] is None
    with pytest.raises(ValueError, match="Explain"):
        finalize_review(report, 0, "")
    assert finalize_review(report, 0, "Reviewed submission manually")["teacher_changed_score"]
