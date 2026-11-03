"""Calculate suggested points from recorded test outcomes; never run code."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

STATUSES = {"passed", "failed", "student_error", "timeout", "infrastructure_error"}


def _points(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError("Test points must be a positive finite number.")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Test points must be a positive finite number.") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError("Test points must be a positive finite number.")
    return result


def _identifier(item: Any, name: str) -> str:
    if not isinstance(item, dict) or not isinstance(item.get("test_id"), str) or not item["test_id"].strip():
        raise ValueError(f"Each {name} must have a nonempty test_id.")
    return item["test_id"].strip()


def score_test_results(exercise: dict[str, Any], outcomes: list[dict[str, Any]]) -> dict[str, Any]:
    """Score defined tests from outcomes, withholding a suggestion when evidence is incomplete.

    This function trusts neither the correctness of the tests nor the origin of
    outcomes. The teacher must review the rubric, evidence, and suggested grade.
    """
    if not isinstance(exercise, dict) or not isinstance(exercise.get("tests"), list) or not exercise["tests"]:
        raise ValueError("Exercise must contain at least one test.")
    if exercise.get("approved_for_grading") is False:
        raise ValueError("Exercise is an unapproved draft; review it before scoring.")
    if not isinstance(outcomes, list):
        raise ValueError("Outcomes must be a list.")
    tests: dict[str, Decimal] = {}
    for test in exercise["tests"]:
        test_id = _identifier(test, "test")
        if test_id in tests:
            raise ValueError(f"Duplicate test_id in exercise: {test_id}")
        tests[test_id] = _points(test.get("points"))
    recorded: dict[str, str] = {}
    for outcome in outcomes:
        test_id = _identifier(outcome, "outcome")
        if test_id not in tests:
            raise ValueError(f"Unknown test_id in outcomes: {test_id}")
        if test_id in recorded:
            raise ValueError(f"Duplicate outcome for test_id: {test_id}")
        status = outcome.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            raise ValueError(f"Invalid status for test_id: {test_id}")
        recorded[test_id] = status

    total = sum(tests.values(), Decimal(0))
    earned = sum((weight for test_id, weight in tests.items() if recorded.get(test_id) == "passed"), Decimal(0))
    incomplete = [test_id for test_id in tests if test_id not in recorded or recorded[test_id] == "infrastructure_error"]
    details = [{"test_id": test_id, "points": str(weight), "status": recorded.get(test_id, "missing"),
                "earned_points": str(weight if recorded.get(test_id) == "passed" else Decimal(0))}
               for test_id, weight in tests.items()]
    return {"maximum_points": str(total), "observed_passed_points": str(earned),
            "suggested_points": None if incomplete else str(earned), "incomplete_test_ids": incomplete,
            "teacher_review_required": True, "tests": details}
