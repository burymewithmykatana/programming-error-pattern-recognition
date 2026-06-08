"""Tests for predictor loading and inference."""

from pathlib import Path

import pytest

from error_pattern_recognition.models.baseline_svm import BaselineTextClassifier
from error_pattern_recognition.inference.predictor import Predictor


def test_predictor_loading_missing_model(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Predictor.from_model_path(tmp_path / "missing.joblib")


def test_predictor_loading_behavior(tmp_path: Path) -> None:
    config = {
        "preprocessing": {"normalize_identifiers": False, "normalize_numbers": False},
        "tfidf": {"lowercase": False, "ngram_range": [1, 1], "min_df": 1},
        "classifier": {"name": "linear_svc", "C": 1.0},
    }
    model = BaselineTextClassifier.from_config(config)
    model.fit(
        ["print(1)", "for i in range(10 print(i)"],
        ["correct_solution", "syntax_error"],
    )
    artifact = tmp_path / "model.joblib"
    model.save(artifact)

    predictor = Predictor.from_model_path(artifact)
    assert predictor.predict_one("print(2)") in {"correct_solution", "syntax_error"}

