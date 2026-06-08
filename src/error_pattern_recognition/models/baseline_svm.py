"""TF-IDF plus linear classifier baseline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from error_pattern_recognition.features.tfidf import build_tfidf_vectorizer
from error_pattern_recognition.preprocessing.pipeline import CodePreprocessor


@dataclass
class BaselineTextClassifier:
    """Train, save, load, and run a TF-IDF baseline classifier."""

    pipeline: Pipeline
    preprocessor: CodePreprocessor

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "BaselineTextClassifier":
        """Build a baseline classifier from a configuration mapping."""
        preprocessor = CodePreprocessor(
            remove_inline_comments_enabled=config.get("preprocessing", {}).get(
                "remove_inline_comments", True
            ),
            normalize_identifiers=config.get("preprocessing", {}).get(
                "normalize_identifiers", False
            ),
            normalize_numbers=config.get("preprocessing", {}).get("normalize_numbers", False),
        )
        classifier_config = config.get("classifier", {})
        classifier = _build_classifier(classifier_config)
        pipeline = Pipeline(
            [
                ("tfidf", build_tfidf_vectorizer(config.get("tfidf", {}))),
                ("classifier", classifier),
            ]
        )
        return cls(pipeline=pipeline, preprocessor=preprocessor)

    def fit(self, code_snippets: list[str], labels: list[str]) -> "BaselineTextClassifier":
        """Fit the classifier."""
        processed = self.preprocessor.transform_many(code_snippets)
        self.pipeline.fit(processed, labels)
        return self

    def predict(self, code_snippets: list[str]) -> list[str]:
        """Predict labels for code snippets."""
        processed = self.preprocessor.transform_many(code_snippets)
        return list(self.pipeline.predict(processed))

    def save(self, path: str | Path) -> None:
        """Save the classifier artifact."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, output_path)

    @staticmethod
    def load(path: str | Path) -> "BaselineTextClassifier":
        """Load a classifier artifact."""
        model_path = Path(path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model artifact not found: {model_path}")
        model = joblib.load(model_path)
        if not isinstance(model, BaselineTextClassifier):
            raise TypeError(f"Unsupported model artifact type: {type(model)!r}")
        return model


def _build_classifier(config: dict[str, Any]) -> LinearSVC | LogisticRegression:
    name = config.get("name", "linear_svc")
    c_value = float(config.get("C", 1.0))
    if name == "linear_svc":
        return LinearSVC(C=c_value)
    if name == "logistic_regression":
        return LogisticRegression(C=c_value, max_iter=int(config.get("max_iter", 1000)))
    raise ValueError(f"Unsupported baseline classifier: {name}")

