"""Evaluation workflow."""

from pathlib import Path
from typing import Any

import pandas as pd

from error_pattern_recognition.data.loader import load_dataset
from error_pattern_recognition.data.splitter import split_dataset
from error_pattern_recognition.evaluation.metrics import (
    build_classification_report,
    build_confusion_matrix,
    compute_metrics,
)
from error_pattern_recognition.inference.predictor import Predictor
from error_pattern_recognition.utils.io import write_json, write_text


def evaluate_model(data_path: str | Path, model_path: str | Path, output_dir: str | Path) -> dict[str, float]:
    """Evaluate a saved model against a labeled dataset and write reports."""
    frame = load_dataset(data_path)
    return evaluate_frame(frame, model_path, output_dir)


def evaluate_model_holdout(
    data_path: str | Path,
    model_path: str | Path,
    output_dir: str | Path,
    config: dict[str, Any],
) -> dict[str, float]:
    """Evaluate a saved model against the config-defined held-out split."""
    frame = load_dataset(data_path, strict_labels=bool(config.get("strict_labels", True)))
    _train_frame, test_frame = split_dataset(
        frame,
        test_size=float(config.get("test_size", 0.2)),
        random_seed=int(config.get("random_seed", 42)),
    )
    return evaluate_frame(test_frame, model_path, output_dir)


def evaluate_frame(
    frame: pd.DataFrame,
    model_path: str | Path,
    output_dir: str | Path,
) -> dict[str, float]:
    """Evaluate a saved model against a validated labeled frame and write reports."""
    predictor = Predictor.from_model_path(model_path)
    y_true = frame["label"].astype(str).tolist()
    y_pred = predictor.predict_many(frame["code"].astype(str).tolist())

    metrics = compute_metrics(y_true, y_pred)
    report = build_classification_report(y_true, y_pred)
    matrix = build_confusion_matrix(y_true, y_pred)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    write_json(output_path / "metrics.json", metrics)
    write_text(output_path / "classification_report.txt", report)
    matrix.to_csv(output_path / "confusion_matrix.csv")
    return metrics
