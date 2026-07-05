"""Tests for the CodeContests preparation script."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "prepare_code_contests.py"
SPEC = importlib.util.spec_from_file_location("prepare_code_contests", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_classify_incorrect_only_accepts_real_syntax_errors() -> None:
    assert MODULE.classify_incorrect("def broken(:\n    pass") == "syntax_error"
    assert MODULE.classify_incorrect("print('valid but wrong')") is None


def test_iter_labeled_rows_filters_languages_and_deduplicates() -> None:
    records = [
        {
            "solutions": {
                "language": [3, 2],
                "solution": ["print('ok')", "int main() {}"],
            },
            "incorrect_solutions": {
                "language": [1, 3, 2],
                "solution": ["if True print('x')", "print('ok')", "broken cpp"],
            },
        }
    ]
    assert list(
        MODULE.iter_labeled_rows(records, max_correct=1, max_syntax_errors=1)
    ) == [
        {"code": "print('ok')", "label": "correct_solution"},
        {"code": "if True print('x')", "label": "syntax_error"},
    ]
