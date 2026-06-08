"""Tests for code preprocessing."""

from error_pattern_recognition.preprocessing.code_cleaner import (
    remove_full_line_comments,
    remove_inline_comments,
)
from error_pattern_recognition.preprocessing.pipeline import CodePreprocessor
from error_pattern_recognition.preprocessing.tokenizer import tokenize_code


def test_remove_full_line_comments() -> None:
    code = "# comment\nx = 1\n    # indented comment\ny = 2"
    assert remove_full_line_comments(code) == "x = 1\ny = 2"


def test_remove_inline_comments() -> None:
    assert remove_inline_comments("x = 1  # value") == "x = 1"


def test_remove_inline_comments_keeps_hash_in_strings() -> None:
    assert remove_inline_comments('text = "# not a comment"  # real comment') == (
        'text = "# not a comment"'
    )


def test_tokenization_fallback() -> None:
    tokens = tokenize_code("for i in range(10 print(i)")
    assert tokens == ["for", "i", "in", "range(10", "print(i)"]


def test_preprocessing_pipeline_normalizes_tokens() -> None:
    preprocessor = CodePreprocessor(normalize_identifiers=True, normalize_numbers=True)
    result = preprocessor.transform_one("count = 12\nprint(count)")
    assert "VAR" in result.tokens
    assert "NUM" in result.tokens
    assert result.text
