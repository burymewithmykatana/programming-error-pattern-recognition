"""Tests for the generated curated training dataset."""

from pathlib import Path

from error_pattern_recognition.constants import SUPPORTED_LABELS
from error_pattern_recognition.data.loader import load_dataset


def test_curated_python_errors_dataset_is_balanced() -> None:
    dataset_path = Path("data/raw/curated_python_errors.csv")

    frame = load_dataset(dataset_path)
    label_counts = frame["label"].value_counts().to_dict()

    assert len(frame) == 1000
    assert set(label_counts) == set(SUPPORTED_LABELS)
    assert set(label_counts.values()) == {125}
