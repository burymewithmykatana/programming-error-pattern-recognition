"""Tests for scoring recorded outcomes, without running submissions."""
import pytest

from error_pattern_recognition.grading import score_test_results


def test_weighted_score_and_review():
    exercise = {"tests": [{"test_id": "a", "points": "2.5"}, {"test_id": "b", "points": 3}]}
    result = score_test_results(exercise, [{"test_id": "a", "status": "passed"}, {"test_id": "b", "status": "failed"}])
    assert result["suggested_points"] == "2.5"
    assert result["maximum_points"] == "5.5"
    assert result["teacher_review_required"] is True


@pytest.mark.parametrize("outcomes", [[], [{"test_id": "a", "status": "infrastructure_error"}]])
def test_incomplete_evidence_never_produces_suggestion(outcomes):
    result = score_test_results({"tests": [{"test_id": "a", "points": 1}]}, outcomes)
    assert result["suggested_points"] is None
    assert result["incomplete_test_ids"] == ["a"]


@pytest.mark.parametrize("points", [0, -1, "NaN", True, "no"])
def test_invalid_points_rejected(points):
    with pytest.raises(ValueError, match="positive finite"):
        score_test_results({"tests": [{"test_id": "a", "points": points}]}, [])


def test_duplicate_and_unknown_results_rejected():
    exercise = {"tests": [{"test_id": "a", "points": 1}]}
    with pytest.raises(ValueError, match="Duplicate outcome"):
        score_test_results(exercise, [{"test_id": "a", "status": "passed"}] * 2)
    with pytest.raises(ValueError, match="Unknown test_id"):
        score_test_results(exercise, [{"test_id": "b", "status": "passed"}])
