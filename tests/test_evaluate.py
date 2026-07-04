"""Tests for model evaluation workflows."""

from pathlib import Path

import pandas as pd

from error_pattern_recognition.evaluation.evaluate import evaluate_model_holdout
from error_pattern_recognition.models.baseline_svm import BaselineTextClassifier


def test_evaluate_model_holdout_writes_reports(tmp_path: Path) -> None:
    frame = pd.DataFrame(
        {
            "code": [f"print({index})" for index in range(12)]
            + [f"for i in range({index} print(i)" for index in range(12)],
            "label": ["correct_solution"] * 12 + ["syntax_error"] * 12,
        }
    )
    data_path = tmp_path / "dataset.csv"
    frame.to_csv(data_path, index=False)
    config = {
        "test_size": 0.25,
        "random_seed": 7,
        "preprocessing": {"normalize_identifiers": False, "normalize_numbers": False},
        "tfidf": {"lowercase": False, "ngram_range": [1, 1], "min_df": 1},
        "classifier": {"name": "linear_svc", "C": 1.0},
    }
    model = BaselineTextClassifier.from_config(config)
    model.fit(frame["code"].astype(str).tolist(), frame["label"].astype(str).tolist())
    model_path = tmp_path / "model.joblib"
    model.save(model_path)
    output_dir = tmp_path / "eval"

    metrics = evaluate_model_holdout(data_path, model_path, output_dir, config)

    assert set(metrics) == {
        "accuracy",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "weighted_f1",
    }
    assert (output_dir / "metrics.json").exists()
    assert (output_dir / "classification_report.txt").exists()
    assert (output_dir / "confusion_matrix.csv").exists()
