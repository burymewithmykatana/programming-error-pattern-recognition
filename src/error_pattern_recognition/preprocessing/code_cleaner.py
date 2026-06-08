"""Source-code cleaning helpers."""

import io
import tokenize


def remove_full_line_comments(code: str) -> str:
    """Remove lines whose first non-whitespace character is a comment marker."""
    lines = [line for line in code.splitlines() if not line.lstrip().startswith("#")]
    return "\n".join(lines)


def remove_inline_comments(code: str) -> str:
    """Remove inline comments without treating comment markers in strings as comments."""
    try:
        tokens = [
            token
            for token in tokenize.generate_tokens(io.StringIO(code).readline)
            if token.type != tokenize.COMMENT
        ]
        return tokenize.untokenize(tokens).rstrip()
    except (IndentationError, SyntaxError, tokenize.TokenError):
        cleaned_lines: list[str] = []
        for line in code.splitlines():
            prefix, separator, _suffix = line.partition("#")
            cleaned_lines.append(prefix.rstrip() if separator else line)
        return "\n".join(cleaned_lines)
