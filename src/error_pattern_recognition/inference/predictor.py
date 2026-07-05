"""Prediction API for saved classifiers."""

from pathlib import Path

import pandas as pd

from error_pattern_recognition.data.loader import load_code_input
from error_pattern_recognition.models.baseline_svm import BaselineTextClassifier
from error_pattern_recognition.models.transformer_classifier import TransformerCodeClassifier


class Predictor:
    """Load a saved model and run one-off or batch predictions."""

    def __init__(self, model: BaselineTextClassifier | TransformerCodeClassifier) -> None:
        self.model = model

    @classmethod
    def from_model_path(cls, path: str | Path) -> "Predictor":
        """Create a predictor from a saved model path."""
        model_path = Path(path)
        if model_path.is_dir():
            return cls(TransformerCodeClassifier.load(model_path))
        return cls(BaselineTextClassifier.load(model_path))

    def predict_one(self, code: str) -> str:
        """Predict one code snippet."""
        return self.model.predict([code])[0]

    def predict_many(self, code_snippets: list[str]) -> list[str]:
        """Predict many code snippets."""
        return self.model.predict(code_snippets)

    def predict_csv(self, input_path: str | Path, output_path: str | Path | None = None) -> pd.DataFrame:
        """Predict labels for a CSV file containing a code column."""
        frame = load_code_input(input_path)
        predictions = self.predict_many(frame["code"].astype(str).tolist())
        result = frame.copy()
        result["predicted_label"] = predictions
        if output_path is not None:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            result.to_csv(output, index=False)
        return result
