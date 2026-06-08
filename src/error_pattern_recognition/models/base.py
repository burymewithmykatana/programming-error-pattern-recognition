"""Shared model protocol definitions."""

from typing import Protocol


class CodeClassifier(Protocol):
    """Protocol for code classifiers."""

    def predict(self, code_snippets: list[str]) -> list[str]:
        """Predict labels for code snippets."""

