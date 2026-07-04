"""Transformer training workflow."""

from pathlib import Path
from typing import Any

from error_pattern_recognition.data.loader import load_dataset
from error_pattern_recognition.models.transformer_classifier import (
    TransformerClassifierConfig,
    TransformerCodeClassifier,
)


def train_transformer(
    data_path: str | Path,
    config: dict[str, Any],
    output_path: str | Path,
) -> TransformerCodeClassifier:
    """Validate data/configuration and start transformer training."""
    frame = load_dataset(data_path, strict_labels=bool(config.get("strict_labels", True)))
    classifier_config = TransformerClassifierConfig.from_config(config)
    model = TransformerCodeClassifier(classifier_config)
    return model.fit(
        frame["code"].astype(str).tolist(),
        frame["label"].astype(str).tolist(),
        output_path,
    )
