"""Tests for dataset loading and validation."""

import pandas as pd
import pytest

from error_pattern_recognition.data.schema import DatasetSchema
from error_pattern_recognition.data.splitter import split_dataset


def test_dataset_schema_validation_success() -> None:
    frame = pd.DataFrame({"code": ["print(1)"], "label": ["correct_solution"]})
    validated = DatasetSchema().validate_frame(frame)
    assert validated.equals(frame)


def test_dataset_schema_requires_columns() -> None:
    frame = pd.DataFrame({"source": ["print(1)"], "label": ["correct_solution"]})
    with pytest.raises(ValueError, match="missing required columns"):
        DatasetSchema().validate_frame(frame)


def test_dataset_schema_rejects_invalid_label_in_strict_mode() -> None:
    frame = pd.DataFrame({"code": ["print(1)"], "label": ["unknown"]})
    with pytest.raises(ValueError, match="Unsupported labels"):
        DatasetSchema(strict_labels=True).validate_frame(frame)


def test_train_test_split() -> None:
    frame = pd.DataFrame(
        {
            "code": [f"print({index})" for index in range(10)],
            "label": ["correct_solution"] * 5 + ["syntax_error"] * 5,
        }
    )
    train_frame, test_frame = split_dataset(frame, test_size=0.2, random_seed=7)
    assert len(train_frame) == 8
    assert len(test_frame) == 2


def test_train_test_split_handles_tiny_multiclass_dataset() -> None:
    frame = pd.DataFrame(
        {
            "code": [f"print({index})" for index in range(16)],
            "label": [f"label_{index // 2}" for index in range(16)],
        }
    )
    train_frame, test_frame = split_dataset(frame, test_size=0.25, random_seed=7)
    assert len(train_frame) == 12
    assert len(test_frame) == 4
