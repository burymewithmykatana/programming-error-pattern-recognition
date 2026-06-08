"""TF-IDF feature construction."""

from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer


def build_tfidf_vectorizer(config: dict[str, Any] | None = None) -> TfidfVectorizer:
    """Create a TF-IDF vectorizer from config values."""
    config = config or {}
    ngram_range = tuple(config.get("ngram_range", (1, 1)))
    return TfidfVectorizer(
        lowercase=bool(config.get("lowercase", False)),
        ngram_range=ngram_range,
        min_df=config.get("min_df", 1),
    )

