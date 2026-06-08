"""Classification metrics."""

from typing import Any

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

from error_pattern_recognition.constants import SUPPORTED_LABELS


def compute_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    """Compute standard classification metrics."""
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="macro",
        zero_division=0,
    )
    _weighted_precision, _weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0,
    )
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
    }


def build_classification_report(y_true: list[str], y_pred: list[str]) -> str:
    """Build a text classification report."""
    labels = [label for label in SUPPORTED_LABELS if label in set(y_true) | set(y_pred)]
    return classification_report(y_true, y_pred, labels=labels, zero_division=0)


def build_confusion_matrix(y_true: list[str], y_pred: list[str]) -> pd.DataFrame:
    """Build a labeled confusion matrix."""
    labels = [label for label in SUPPORTED_LABELS if label in set(y_true) | set(y_pred)]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    return pd.DataFrame(matrix, index=labels, columns=labels)

