"""Dataset schema validation."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from error_pattern_recognition.constants import SUPPORTED_LABELS


@dataclass(frozen=True)
class DatasetSchema:
    """Validation settings for a labeled code dataset."""

    code_column: str = "code"
    label_column: str = "label"
    strict_labels: bool = True

    def validate_path(self, path: str | Path) -> Path:
        """Validate that a dataset path exists."""
        dataset_path = Path(path)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset CSV not found: {dataset_path}")
        if not dataset_path.is_file():
            raise ValueError(f"Dataset path is not a file: {dataset_path}")
        return dataset_path

    def validate_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Validate dataset columns, code values, and labels."""
        missing = {self.code_column, self.label_column} - set(frame.columns)
        if missing:
            raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

        if frame[self.code_column].isna().any():
            raise ValueError("Dataset contains missing code values.")
        if not frame[self.code_column].map(lambda value: isinstance(value, str)).all():
            raise ValueError("All code values must be strings.")

        labels = frame[self.label_column]
        if labels.isna().any() or labels.map(lambda value: not str(value).strip()).any():
            raise ValueError("Labels must be non-empty.")

        if self.strict_labels:
            invalid = sorted(set(labels.astype(str)) - set(SUPPORTED_LABELS))
            if invalid:
                raise ValueError(f"Unsupported labels found: {invalid}")

        return frame

