"""Prepare score-prediction examples without exposing labels in model inputs."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

from error_pattern_recognition.grading.scoring import score_test_results

SPLITS = {"train", "validation", "test"}


def prepare_examples(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Recompute synthetic targets and enforce exercise-disjoint splits.

    Features are restricted to the statement, reference, rubric, and submission.
    Scores, outcomes, and mutation names are never included in those features.
    """
    groups: dict[str, list[dict[str, Any]]] = {name: [] for name in sorted(SPLITS)}
    exercise_splits: dict[str, str] = {}
    exercise_versions: dict[str, str] = {}
    submissions = set()
    for record in records:
        if not isinstance(record, dict) or record.get("split") not in SPLITS:
            raise ValueError("Each record must specify train, validation, or test split.")
        split = record["split"]
        exercise = record.get("exercise")
        if not isinstance(exercise, dict):
            raise ValueError("Each record must contain an exercise object.")
        exercise_id, submission_id = exercise.get("exercise_id"), record.get("submission_id")
        for value, name in ((exercise_id, "exercise_id"), (submission_id, "submission_id"),
                            (exercise.get("prompt"), "prompt"),
                            (exercise.get("reference_solution"), "reference_solution"),
                            (record.get("student_code"), "student_code")):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be nonempty text.")
        if submission_id in submissions:
            raise ValueError(f"Duplicate submission_id: {submission_id}")
        submissions.add(submission_id)
        if exercise_id in exercise_splits and exercise_splits[exercise_id] != split:
            raise ValueError(f"Exercise appears in multiple splits: {exercise_id}")
        exercise_splits[exercise_id] = split
        version = hashlib.sha256(json.dumps(exercise, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()
        if exercise_id in exercise_versions and exercise_versions[exercise_id] != version:
            raise ValueError(f"Exercise differs between records: {exercise_id}")
        exercise_versions[exercise_id] = version
        scoring = score_test_results(exercise, record.get("outcomes"))
        if scoring["suggested_points"] is None:
            raise ValueError(f"Incomplete evidence for submission: {submission_id}")
        points, maximum = Decimal(scoring["suggested_points"]), Decimal(scoring["maximum_points"])
        groups[split].append({
            "submission_id": submission_id, "exercise_id": exercise_id,
            "exercise_prompt": exercise["prompt"], "reference_solution": exercise["reference_solution"],
            "rubric_tests": [{key: test[key] for key in ("test_id", "input", "keyword_input", "expected", "comparison", "points") if key in test}
                             for test in exercise["tests"]],
            "student_code": record["student_code"], "target_fraction": float(points / maximum),
            "points": str(points), "maximum_points": str(maximum),
        })
    if not groups["train"] or not groups["validation"]:
        raise ValueError("At least one train and validation example are required.")
    return groups
