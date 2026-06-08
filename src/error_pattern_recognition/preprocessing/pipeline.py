"""Composable preprocessing pipeline for source code."""

from dataclasses import dataclass

from error_pattern_recognition.preprocessing.code_cleaner import (
    remove_full_line_comments,
    remove_inline_comments,
)
from error_pattern_recognition.preprocessing.tokenizer import tokenize_code


@dataclass(frozen=True)
class PreprocessingResult:
    """Preprocessed code represented as tokens and joined text."""

    tokens: list[str]
    text: str


@dataclass(frozen=True)
class CodePreprocessor:
    """Configurable source-code preprocessor."""

    remove_inline_comments_enabled: bool = True
    normalize_identifiers: bool = False
    normalize_numbers: bool = False

    def transform_one(self, code: str) -> PreprocessingResult:
        """Preprocess one code snippet."""
        cleaned = remove_full_line_comments(code)
        if self.remove_inline_comments_enabled:
            cleaned = remove_inline_comments(cleaned)
        tokens = tokenize_code(
            cleaned,
            normalize_identifiers=self.normalize_identifiers,
            normalize_numbers=self.normalize_numbers,
        )
        return PreprocessingResult(tokens=tokens, text=" ".join(tokens))

    def transform_text(self, code: str) -> str:
        """Preprocess one code snippet into joined token text."""
        return self.transform_one(code).text

    def transform_many(self, snippets: list[str]) -> list[str]:
        """Preprocess many snippets into joined token text."""
        return [self.transform_text(code) for code in snippets]

