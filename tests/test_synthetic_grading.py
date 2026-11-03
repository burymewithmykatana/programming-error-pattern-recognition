"""Validate synthetic benchmark structure and its stated constraints."""
import ast
import importlib.util
from pathlib import Path


def _load_generator():
    path = Path(__file__).resolve().parents[1] / "scripts/generate_synthetic_grading.py"
    spec = importlib.util.spec_from_file_location("synthetic_grading_generator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exercise_splits_and_expected_outcomes():
    rows = _load_generator().build_dataset()
    assert len(rows) == 24
    splits = {split: {r["exercise"]["exercise_id"] for r in rows if r["split"] == split}
              for split in ("train", "validation", "test")}
    assert not (splits["train"] & splits["validation"] or splits["train"] & splits["test"] or splits["validation"] & splits["test"])
    assert all(r["score"]["suggested_points"] == r["score"]["maximum_points"] for r in rows if r["variant"] == "correct")
    assert all(r["score"]["suggested_points"] != r["score"]["maximum_points"] for r in rows if r["variant"] != "correct")
    assert any(outcome["status"] == "student_error" for r in rows for outcome in r["outcomes"])
    for row in rows:
        parsed = ast.parse(row["student_code"])
        assert parsed.body[0].name == row["exercise"]["function_name"]
        assert row["score"]["teacher_review_required"]


def test_dataset_is_deterministic():
    generator = _load_generator()
    assert generator.build_dataset() == generator.build_dataset()
