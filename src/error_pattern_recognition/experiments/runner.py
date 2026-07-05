"""Leakage-safe training and evaluation for supported model families."""

from __future__ import annotations

import hashlib
import json
import platform
import time
from pathlib import Path
from typing import Any

import pandas as pd

from error_pattern_recognition.data.loader import load_dataset
from error_pattern_recognition.evaluation.metrics import (
    build_classification_report,
    build_confusion_matrix,
    compute_metrics,
)
from error_pattern_recognition.models.baseline_svm import BaselineTextClassifier
from error_pattern_recognition.models.transformer_classifier import (
    TransformerClassifierConfig,
    TransformerCodeClassifier,
)
from error_pattern_recognition.utils.io import write_json, write_text


def code_fingerprint(code: str) -> str:
    """Create a stable exact-code fingerprint."""
    normalized = code.replace("\r\n", "\n").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_no_leakage(train_frame: pd.DataFrame, test_frame: pd.DataFrame) -> None:
    """Reject duplicate code within or across experiment splits."""
    for name, frame in (("train", train_frame), ("test", test_frame)):
        fingerprints = frame["code"].astype(str).map(code_fingerprint)
        if fingerprints.duplicated().any():
            raise ValueError(f"{name} data contains duplicate code submissions.")
    overlap = set(train_frame["code"].astype(str).map(code_fingerprint)) & set(
        test_frame["code"].astype(str).map(code_fingerprint)
    )
    if overlap:
        raise ValueError(f"Train/test leakage detected: {len(overlap)} duplicate submissions.")


def run_experiment(
    *,
    train_data: str | Path,
    test_data: str | Path,
    model_type: str,
    config: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Train, evaluate, and persist one reproducible experiment."""
    train_frame = load_dataset(train_data)
    test_frame = load_dataset(test_data)
    validate_no_leakage(train_frame, test_frame)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    train_code = train_frame["code"].astype(str).tolist()
    train_labels = train_frame["label"].astype(str).tolist()
    test_code = test_frame["code"].astype(str).tolist()
    y_true = test_frame["label"].astype(str).tolist()

    started = time.perf_counter()
    if model_type == "svm":
        model = BaselineTextClassifier.from_config(config).fit(train_code, train_labels)
        model_path = output_path / "model.joblib"
        model.save(model_path)
    elif model_type == "codebert":
        transformer_config = TransformerClassifierConfig.from_config(config)
        model_path = output_path / "model"
        model = TransformerCodeClassifier(transformer_config).fit(
            train_code,
            train_labels,
            model_path,
        )
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    training_seconds = time.perf_counter() - started

    prediction_started = time.perf_counter()
    y_pred = model.predict(test_code)
    prediction_seconds = time.perf_counter() - prediction_started
    metrics = compute_metrics(y_true, y_pred)
    metrics.update(
        {
            "training_seconds": training_seconds,
            "prediction_seconds": prediction_seconds,
            "train_rows": len(train_frame),
            "test_rows": len(test_frame),
        }
    )

    predictions = test_frame.copy()
    predictions["predicted_label"] = y_pred
    predictions["correct"] = predictions["label"] == predictions["predicted_label"]
    predictions.to_csv(output_path / "predictions.csv", index=False)
    write_json(output_path / "metrics.json", metrics)
    write_text(
        output_path / "classification_report.txt",
        build_classification_report(y_true, y_pred),
    )
    build_confusion_matrix(y_true, y_pred).to_csv(output_path / "confusion_matrix.csv")
    write_json(
        output_path / "run_config.json",
        {
            "model_type": model_type,
            "train_data": str(Path(train_data).resolve()),
            "test_data": str(Path(test_data).resolve()),
            "model_path": str(model_path.resolve()),
            "labels": sorted(set(train_labels)),
            "config": config,
            "python": platform.python_version(),
            "dataset_stats": {
                "train_labels": train_frame["label"].value_counts().to_dict(),
                "test_labels": test_frame["label"].value_counts().to_dict(),
            },
        },
    )
    return metrics
