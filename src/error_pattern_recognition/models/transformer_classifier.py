"""Placeholder for future transformer-based classifiers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TransformerClassifierConfig:
    """Configuration for a future Hugging Face sequence classifier."""

    model_name: str = "microsoft/codebert-base"
    max_length: int = 256
    num_labels: int = 8


class TransformerCodeClassifier:
    """Future CodeBERT-style classifier interface."""

    def __init__(self, config: TransformerClassifierConfig) -> None:
        self.config = config

    def fit(self) -> None:
        """Placeholder for future Hugging Face Trainer integration."""
        raise NotImplementedError("Transformer training is planned for a future iteration.")

    def predict(self, code_snippets: list[str]) -> list[str]:
        """Placeholder for future transformer inference."""
        raise NotImplementedError("Transformer inference is planned for a future iteration.")

