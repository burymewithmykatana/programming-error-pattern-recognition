"""Generate a deterministic synthetic Python error-pattern dataset."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

LABELS = (
    "correct_solution",
    "syntax_error",
    "variable_misuse",
    "loop_logic_error",
    "conditional_logic_error",
    "function_definition_error",
    "data_structure_misuse",
    "algorithmic_inefficiency",
)


def _correct_solution(index: int) -> str:
    templates = (
        "def solve_{i}(values):\n    total = 0\n    for value in values:\n        total += value\n    return total",
        "def solve_{i}(text):\n    return text.strip().lower()",
        "def solve_{i}(numbers):\n    return [number * 2 for number in numbers]",
        "def solve_{i}(n):\n    if n <= 1:\n        return n\n    return solve_{i}(n - 1) + solve_{i}(n - 2)",
        "def solve_{i}(items):\n    counts = {{}}\n    for item in items:\n        counts[item] = counts.get(item, 0) + 1\n    return counts",
    )
    return templates[index % len(templates)].format(i=index)


def _syntax_error(index: int) -> str:
    templates = (
        "def solve_{i}(values)\n    return sum(values)",
        "for value in range({n})\n    print(value)",
        "if {n} > 3:\nprint('large')",
        "def solve_{i}(x):\n    return (x + {n}",
        "items = [1, 2, 3\nprint(items)",
    )
    return templates[index % len(templates)].format(i=index, n=index + 3)


def _variable_misuse(index: int) -> str:
    templates = (
        "def solve_{i}(values):\n    total = 0\n    for value in values:\n        total += item\n    return total",
        "def solve_{i}(text):\n    cleaned = text.strip()\n    return clean.lower()",
        "def solve_{i}(numbers):\n    maximum = numbers[0]\n    for number in numbers:\n        if value > maximum:\n            maximum = value\n    return maximum",
        "def solve_{i}(name):\n    greeting = 'Hello ' + user\n    return greeting",
        "def solve_{i}(x, y):\n    result = x + y\n    return total",
    )
    return templates[index % len(templates)].format(i=index)


def _loop_logic_error(index: int) -> str:
    templates = (
        "def solve_{i}(values):\n    total = 0\n    for index in range(len(values) - 1):\n        total += values[index]\n    return total",
        "def solve_{i}(n):\n    count = 0\n    while count < n:\n        print(count)\n    return count",
        "def solve_{i}(values):\n    result = []\n    for index in range(1, len(values)):\n        result.append(values[index])\n    return result",
        "def solve_{i}(numbers):\n    total = 0\n    for number in numbers:\n        total = number\n    return total",
        "def solve_{i}(limit):\n    items = []\n    for value in range(limit + 1):\n        items.append(value)\n    return items",
    )
    return templates[index % len(templates)].format(i=index)


def _conditional_logic_error(index: int) -> str:
    templates = (
        "def solve_{i}(score):\n    if score < 50:\n        return 'pass'\n    return 'fail'",
        "def solve_{i}(number):\n    if number % 2 == 1:\n        return 'even'\n    return 'odd'",
        "def solve_{i}(age):\n    if age <= 18:\n        return 'adult'\n    return 'minor'",
        "def solve_{i}(values):\n    if len(values) == 0:\n        return values[0]\n    return None",
        "def solve_{i}(x, y):\n    if x > 0 or y > 0:\n        return 'both positive'\n    return 'not both positive'",
    )
    return templates[index % len(templates)].format(i=index)


def _function_definition_error(index: int) -> str:
    templates = (
        "def solve_{i}():\n    return value + 1",
        "def solve_{i}(x, y):\n    result = x + y",
        "def solve_{i}(values):\n    print(sum(values))",
        "def solve_{i}(x):\n    return helper(x)\n\ndef helper(x, y):\n    return x + y",
        "def solve_{i}(items, target):\n    return items.index(target)\n\nanswer = solve_{i}([1, 2, 3])",
    )
    return templates[index % len(templates)].format(i=index)


def _data_structure_misuse(index: int) -> str:
    templates = (
        "def solve_{i}(items):\n    return items['first']",
        "def solve_{i}(scores):\n    scores.add(10)\n    return scores",
        "def solve_{i}(mapping):\n    return mapping[0]",
        "def solve_{i}(items):\n    seen = []\n    seen['count'] = len(items)\n    return seen",
        "def solve_{i}(text):\n    chars = set(text)\n    return chars[0]",
    )
    return templates[index % len(templates)].format(i=index)


def _algorithmic_inefficiency(index: int) -> str:
    templates = (
        "def solve_{i}(values):\n    unique = []\n    for value in values:\n        if values.count(value) == 1:\n            unique.append(value)\n    return unique",
        "def solve_{i}(numbers):\n    result = []\n    for number in numbers:\n        if number in sorted(numbers):\n            result.append(number)\n    return result",
        "def solve_{i}(items):\n    pairs = []\n    for left in items:\n        for right in items:\n            if left == right:\n                pairs.append(left)\n    return pairs",
        "def solve_{i}(n):\n    values = []\n    for number in range(n):\n        values = values + [number]\n    return values",
        "def solve_{i}(text):\n    result = ''\n    for char in text:\n        result = result + char\n    return result",
    )
    return templates[index % len(templates)].format(i=index)


GENERATORS = {
    "correct_solution": _correct_solution,
    "syntax_error": _syntax_error,
    "variable_misuse": _variable_misuse,
    "loop_logic_error": _loop_logic_error,
    "conditional_logic_error": _conditional_logic_error,
    "function_definition_error": _function_definition_error,
    "data_structure_misuse": _data_structure_misuse,
    "algorithmic_inefficiency": _algorithmic_inefficiency,
}


def build_rows(examples_per_label: int = 125) -> list[dict[str, str]]:
    """Build balanced dataset rows."""
    rows = []
    for label in LABELS:
        generator = GENERATORS[label]
        for index in range(examples_per_label):
            rows.append({"code": generator(index), "label": label})
    return rows


def write_dataset(output_path: Path, examples_per_label: int) -> None:
    """Write generated rows to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = build_rows(examples_per_label=examples_per_label)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["code", "label"])
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate a synthetic curated training dataset.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/curated_python_errors.csv"),
        help="Output CSV path.",
    )
    parser.add_argument(
        "--examples-per-label",
        type=int,
        default=125,
        help="Number of examples to generate for each label.",
    )
    return parser.parse_args()


def main() -> None:
    """Generate the dataset."""
    args = parse_args()
    write_dataset(args.output, args.examples_per_label)
    print(f"Wrote {args.examples_per_label * len(LABELS)} rows to {args.output}")


if __name__ == "__main__":
    main()
