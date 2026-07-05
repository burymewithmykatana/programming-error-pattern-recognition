"""Tests for leakage-safe experiments."""

from __future__ import annotations

import pandas as pd
import pytest

from error_pattern_recognition.experiments.runner import run_experiment, validate_no_leakage


def _frame(codes: list[str], labels: list[str]) -> pd.DataFrame:
    return pd.DataFrame({"code": codes, "label": labels})


def test_validate_no_leakage_rejects_overlap() -> None:
    with pytest.raises(ValueError, match="leakage"):
        validate_no_leakage(
            _frame(["print(1)", "print(2)"], ["correct_solution", "correct_solution"]),
            _frame(["print(1)", "if True print(2)"], ["correct_solution", "syntax_error"]),
        )


def test_svm_experiment_writes_standard_outputs(tmp_path) -> None:
    train = _frame(
        ["print(1)", "print(2)", "if True print(1)", "def broken(:"],
        ["correct_solution", "correct_solution", "syntax_error", "syntax_error"],
    )
    test = _frame(
        ["print(3)", "if False print(3)"],
        ["correct_solution", "syntax_error"],
    )
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)
    output = tmp_path / "experiment"

    metrics = run_experiment(
        train_data=train_path,
        test_data=test_path,
        model_type="svm",
        config={
            "preprocessing": {},
            "tfidf": {"ngram_range": [1, 2]},
            "classifier": {"name": "linear_svc"},
        },
        output_dir=output,
    )

    assert metrics["test_rows"] == 2
    for name in (
        "metrics.json",
        "classification_report.txt",
        "confusion_matrix.csv",
        "predictions.csv",
        "run_config.json",
        "model.joblib",
    ):
        assert (output / name).exists()
