"""Baseline training workflow."""

from pathlib import Path
from typing import Any

from error_pattern_recognition.data.loader import load_dataset
from error_pattern_recognition.data.splitter import split_dataset
from error_pattern_recognition.models.baseline_svm import BaselineTextClassifier
from error_pattern_recognition.utils.logging import get_logger

LOGGER = get_logger(__name__)


def train_baseline(data_path: str | Path, config: dict[str, Any], output_path: str | Path) -> BaselineTextClassifier:
    """Train and save the baseline classifier."""
    frame = load_dataset(data_path, strict_labels=bool(config.get("strict_labels", True)))
    train_frame, _test_frame = split_dataset(
        frame,
        test_size=float(config.get("test_size", 0.2)),
        random_seed=int(config.get("random_seed", 42)),
    )
    model = BaselineTextClassifier.from_config(config)
    model.fit(train_frame["code"].astype(str).tolist(), train_frame["label"].astype(str).tolist())
    model.save(output_path)
    LOGGER.info("Saved baseline model to %s", output_path)
    return model

