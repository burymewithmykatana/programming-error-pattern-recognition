"""Check grading targets, disjoint exercise splits and feature leakage."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

from error_pattern_recognition.grading.training_data import prepare_examples


def _rows():
    path = Path(__file__).resolve().parents[1] / "data/synthetic_grading/submissions.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_targets_recomputed_and_only_allowed_features_exported():
    rows = _rows()
    rows[0]["score"] = {"suggested_points": "0"}
    rows[0]["variant"] = "DO_NOT_LEAK_THIS"
    result = prepare_examples(rows)
    example = result["train"][0]
    assert example["target_fraction"] == 1.0
    assert "variant" not in example and "outcomes" not in example and "score" not in example
    assert example["rubric_tests"][0]["expected"] == 5
    assert {k: len(v) for k, v in result.items()} == {"test": 4, "train": 16, "validation": 4}


def test_rejects_cross_split_exercises_and_changed_rubrics():
    rows = _rows()
    invalid = copy.deepcopy(rows)
    invalid[0]["split"] = "validation"
    with pytest.raises(ValueError, match="multiple splits"):
        prepare_examples(invalid)
    invalid = copy.deepcopy(rows)
    invalid[1]["exercise"]["tests"][0]["points"] = 999
    with pytest.raises(ValueError, match="differs"):
        prepare_examples(invalid)


def test_missing_evidence_and_duplicate_submission_rejected():
    rows = _rows()
    invalid = copy.deepcopy(rows)
    invalid[0]["outcomes"] = []
    with pytest.raises(ValueError, match="Incomplete evidence"):
        prepare_examples(invalid)
    with pytest.raises(ValueError, match="Duplicate submission"):
        prepare_examples(rows + [copy.deepcopy(rows[0])])


def test_baseline_uses_validation_only_and_excludes_label_fields(tmp_path):
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("grading_baseline", root / "scripts/train_grading_baseline.py")
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    splits = prepare_examples(_rows())
    for name, rows in splits.items():
        (tmp_path / f"{name}.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    sample = dict(splits["train"][0], variant="DO_NOT_LEAK_THIS", outcomes="DO_NOT_LEAK_THIS", score="DO_NOT_LEAK_THIS")
    assert "DO_NOT_LEAK_THIS" not in baseline.features(sample)
    metrics = baseline.run(tmp_path, tmp_path / "out")
    assert metrics["train_rows"] == 16 and metrics["validation_rows"] == 4
    assert metrics["validation_exercises"] == 1 and metrics["test_split_used"] is False
    assert 0 <= metrics["validation_mae_fraction"] <= 1
    assert 0 <= metrics["constant_mean_validation_mae_fraction"] <= 1
    duplicate = copy.deepcopy(splits["validation"])
    duplicate[0]["submission_id"] = splits["train"][0]["submission_id"]
    (tmp_path / "validation.jsonl").write_text("".join(json.dumps(row) + "\n" for row in duplicate), encoding="utf-8")
    with pytest.raises(ValueError, match="submission IDs must be disjoint"):
        baseline.run(tmp_path, tmp_path / "out2")
