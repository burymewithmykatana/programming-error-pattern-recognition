"""Prepare a Python training CSV from DeepMind CodeContests."""

from __future__ import annotations

import argparse
import ast
import csv
import os
import warnings
from pathlib import Path
from typing import Any, Iterable

PYTHON_LANGUAGE_IDS = {1, 3}


def classify_incorrect(code: str) -> str | None:
    """Return a defensible project label for an incorrect submission."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            ast.parse(code)
    except (SyntaxError, ValueError):
        return "syntax_error"
    return None


def iter_labeled_rows(
    records: Iterable[dict[str, Any]],
    *,
    max_correct: int,
    max_syntax_errors: int,
) -> Iterable[dict[str, str]]:
    """Yield balanced, deduplicated Python rows."""
    counts = {"correct_solution": 0, "syntax_error": 0}
    seen: set[str] = set()

    for record in records:
        solutions = record.get("solutions") or {}
        for language, code in zip(
            solutions.get("language", []),
            solutions.get("solution", []),
            strict=False,
        ):
            if (
                language in PYTHON_LANGUAGE_IDS
                and code
                and code not in seen
                and counts["correct_solution"] < max_correct
            ):
                seen.add(code)
                counts["correct_solution"] += 1
                yield {"code": code, "label": "correct_solution"}

        incorrect = record.get("incorrect_solutions") or {}
        for language, code in zip(
            incorrect.get("language", []),
            incorrect.get("solution", []),
            strict=False,
        ):
            if (
                language not in PYTHON_LANGUAGE_IDS
                or not code
                or code in seen
                or counts["syntax_error"] >= max_syntax_errors
            ):
                continue
            label = classify_incorrect(code)
            if label is not None:
                seen.add(code)
                counts[label] += 1
                yield {"code": code, "label": label}

        if counts["correct_solution"] >= max_correct and counts["syntax_error"] >= max_syntax_errors:
            return


def prepare_dataset(
    *,
    output_path: Path,
    cache_dir: Path,
    split: str,
    examples_per_label: int,
    streaming: bool,
) -> dict[str, int]:
    """Load CodeContests and write a project-compatible CSV."""
    from datasets import load_dataset

    cache_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache_dir))
    os.environ.setdefault("HF_DATASETS_CACHE", str(cache_dir / "datasets"))
    os.environ.setdefault("HF_HUB_CACHE", str(cache_dir / "hub"))

    records = load_dataset(
        "deepmind/code_contests",
        split=split,
        streaming=streaming,
        cache_dir=str(cache_dir / "datasets"),
    )
    rows = iter_labeled_rows(
        records,
        max_correct=examples_per_label,
        max_syntax_errors=examples_per_label,
    )
    counts = {"correct_solution": 0, "syntax_error": 0}
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["code", "label"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            counts[row["label"]] += 1

    if min(counts.values()) == 0:
        raise RuntimeError(f"CodeContests extraction produced an empty class: {counts}")
    return counts


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/code_contests_python.csv"),
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(r"D:\huggingface\code_contests"),
    )
    parser.add_argument("--split", default="train")
    parser.add_argument("--examples-per-label", type=int, default=10_000)
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download the split instead of reading it in streaming mode.",
    )
    return parser.parse_args()


def main() -> None:
    """Prepare the dataset."""
    args = parse_args()
    counts = prepare_dataset(
        output_path=args.output,
        cache_dir=args.cache_dir,
        split=args.split,
        examples_per_label=args.examples_per_label,
        streaming=not args.download,
    )
    print(f"Wrote {sum(counts.values())} rows to {args.output}: {counts}")


if __name__ == "__main__":
    main()
