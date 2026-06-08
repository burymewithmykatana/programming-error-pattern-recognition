"""Dataset loading utilities."""

from pathlib import Path

import pandas as pd

from error_pattern_recognition.data.schema import DatasetSchema


def load_dataset(path: str | Path, *, strict_labels: bool = True) -> pd.DataFrame:
    """Load and validate a labeled code dataset from CSV."""
    schema = DatasetSchema(strict_labels=strict_labels)
    dataset_path = schema.validate_path(path)
    frame = pd.read_csv(dataset_path)
    return schema.validate_frame(frame)

