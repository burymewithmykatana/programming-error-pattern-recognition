"""Python source tokenization."""

from __future__ import annotations

import io
import keyword
import tokenize


def tokenize_code(
    code: str,
    *,
    normalize_identifiers: bool = False,
    normalize_numbers: bool = False,
) -> list[str]:
    """Tokenize Python code, falling back to whitespace tokenization on failure."""
    try:
        return _tokenize_python(
            code,
            normalize_identifiers=normalize_identifiers,
            normalize_numbers=normalize_numbers,
        )
    except (SyntaxError, tokenize.TokenError, IndentationError, UnicodeDecodeError):
        return code.split()


def _tokenize_python(
    code: str,
    *,
    normalize_identifiers: bool,
    normalize_numbers: bool,
) -> list[str]:
    tokens: list[str] = []
    reader = io.BytesIO(code.encode("utf-8")).readline
    ignored = {
        tokenize.ENCODING,
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENDMARKER,
        tokenize.COMMENT,
    }
    for token in tokenize.tokenize(reader):
        if token.type in ignored:
            continue
        value = token.string
        if normalize_identifiers and token.type == tokenize.NAME and not keyword.iskeyword(value):
            value = "VAR"
        elif normalize_numbers and token.type == tokenize.NUMBER:
            value = "NUM"
        tokens.append(value)
    return tokens

