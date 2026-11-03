"""Generate a small, deterministic synthetic function-grading benchmark.

Only the fixed, author-written functions in this file are called. This generator
never executes code read from a dataset or provided by a student.
"""
from __future__ import annotations

import argparse
import inspect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from error_pattern_recognition.grading import score_test_results


def add_good(a, b): return a + b
def add_subtract(a, b): return a - b
def add_positive(a, b): return abs(a) + abs(b)
def add_zero(a, b): return 0


def square_good(n): return n * n
def square_double(n): return n * 2
def square_abs(n): return abs(n)
def square_zero(n): return 0


def absolute_good(n): return abs(n)
def absolute_identity(n): return n
def absolute_negate(n): return -n
def absolute_zero(n): return 0


def total_good(values): return sum(values)
def total_length(values): return len(values)
def total_first(values): return values[0]
def total_positive(values): return sum(x for x in values if x > 0)


def count_good(values): return sum(1 for x in values if x % 2 == 0)
def count_odd(values): return sum(1 for x in values if x % 2 != 0)
def count_all(values): return len(values)
def count_positive_even(values): return sum(1 for x in values if x > 0 and x % 2 == 0)


def reverse_good(text): return text[::-1]
def reverse_identity(text): return text
def reverse_lower(text): return text[::-1].lower()
def reverse_empty(text): return ""


def source_for(function, public_name: str) -> str:
    """Render the exact trusted function body with the exercise's function name."""
    return inspect.getsource(function).replace(f"def {function.__name__}(", f"def {public_name}(", 1)


def _case(test_id: str, args: list, expected: object, points: int) -> dict:
    return {"test_id": test_id, "input": args, "expected": expected, "points": points}


EXERCISES = [
    ("add", "train", "Return the sum of two integers.", add_good,
     [_case("positive", [2, 3], 5, 2), _case("negative", [-4, 1], -3, 3),
      _case("zero", [0, 0], 0, 2), _case("mixed", [7, -7], 0, 3)],
     [("correct", add_good), ("subtracts", add_subtract), ("absolute_values", add_positive), ("always_zero", add_zero)]),
    ("square", "train", "Return the square of an integer.", square_good,
     [_case("positive", [3], 9, 3), _case("negative", [-2], 4, 3),
      _case("zero", [0], 0, 2), _case("one", [1], 1, 2)],
     [("correct", square_good), ("doubles", square_double), ("absolute_value", square_abs), ("always_zero", square_zero)]),
    ("absolute", "train", "Return the absolute value of an integer.", absolute_good,
     [_case("positive", [4], 4, 3), _case("negative", [-5], 5, 3),
      _case("zero", [0], 0, 2), _case("negative_one", [-1], 1, 2)],
     [("correct", absolute_good), ("identity", absolute_identity), ("negates", absolute_negate), ("always_zero", absolute_zero)]),
    ("total", "train", "Return the sum of a list of integers; an empty list sums to zero.", total_good,
     [_case("positive", [[1, 2, 3]], 6, 3), _case("empty", [[]], 0, 2),
      _case("mixed", [[-3, 1]], -2, 3), _case("single", [[5]], 5, 2)],
     [("correct", total_good), ("counts_items", total_length), ("first_item", total_first), ("positive_only", total_positive)]),
    ("count_even", "validation", "Count even integers in a list, including zero and negative numbers.", count_good,
     [_case("mixed", [[1, 2, 4]], 2, 3), _case("empty", [[]], 0, 2),
      _case("zero_negative", [[0, -2, 3]], 2, 3), _case("odd", [[1, 3]], 0, 2)],
     [("correct", count_good), ("counts_odd", count_odd), ("counts_all", count_all), ("positive_even_only", count_positive_even)]),
    ("reverse", "test", "Return a string with its characters in reverse order, preserving case.", reverse_good,
     [_case("word", ["cat"], "tac", 3), _case("empty", [""], "", 2),
      _case("mixed_case", ["AbC"], "CbA", 3), _case("single", ["x"], "x", 2)],
     [("correct", reverse_good), ("unchanged", reverse_identity), ("lowercases", reverse_lower), ("always_empty", reverse_empty)]),
]


def build_dataset() -> list[dict]:
    rows = []
    for name, split, prompt, reference, tests, variants in EXERCISES:
        exercise = {"exercise_id": name, "function_name": name, "prompt": prompt, "tests": tests,
                    "reference_solution": source_for(reference, name)}
        for variant, function in variants:
            outcomes = []
            for test in tests:
                try:
                    actual = function(*test["input"])
                    status = "passed" if type(actual) is type(test["expected"]) and actual == test["expected"] else "failed"
                    outcome = {"test_id": test["test_id"], "status": status, "actual": actual}
                except Exception as exc:
                    outcome = {"test_id": test["test_id"], "status": "student_error", "error_type": type(exc).__name__}
                outcomes.append(outcome)
            score = score_test_results(exercise, outcomes)
            rows.append({"submission_id": f"{name}-{variant}", "split": split, "exercise": exercise,
                         "student_code": source_for(function, name), "variant": variant,
                         "outcomes": outcomes, "score": score,
                         "provenance": "synthetic; author-written functions; scores computed from synthetic tests"})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/synthetic_grading/submissions.jsonl"))
    args = parser.parse_args()
    rows = build_dataset()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(f"Wrote {len(rows)} synthetic submissions across {len(EXERCISES)} exercises to {args.output}")


if __name__ == "__main__":
    main()
