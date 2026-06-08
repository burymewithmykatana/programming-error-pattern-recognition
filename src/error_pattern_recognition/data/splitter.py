"""Train/test splitting utilities."""

import math

import pandas as pd
from sklearn.model_selection import train_test_split


def split_dataset(
    frame: pd.DataFrame,
    *,
    test_size: float = 0.2,
    random_seed: int = 42,
    stratify: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a dataset into train and test frames."""
    stratify_values = frame["label"] if _can_stratify(frame, test_size, stratify) else None
    train_frame, test_frame = train_test_split(
        frame,
        test_size=test_size,
        random_state=random_seed,
        stratify=stratify_values,
    )
    return train_frame.reset_index(drop=True), test_frame.reset_index(drop=True)


def _can_stratify(frame: pd.DataFrame, test_size: float, requested: bool) -> bool:
    if not requested or frame["label"].nunique() <= 1:
        return False
    class_counts = frame["label"].value_counts()
    if class_counts.min() < 2:
        return False
    class_count = len(class_counts)
    row_count = len(frame)
    test_count = math.ceil(row_count * test_size) if isinstance(test_size, float) else int(test_size)
    train_count = row_count - test_count
    return test_count >= class_count and train_count >= class_count
