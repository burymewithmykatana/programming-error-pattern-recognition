"""Create a reproducible class-balanced sample from a labeled CSV dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from error_pattern_recognition.data.loader import load_dataset


def sample_dataset(
    *,
    input_path: str | Path,
    output_path: str | Path,
    max_per_label: int,
    seed: int = 42,
) -> pd.DataFrame:
    """Sample up to ``max_per_label`` rows from each class label."""
    if max_per_label <= 0:
        raise ValueError("max_per_label must be positive.")
    frame = load_dataset(input_path)
    sampled_groups = [
        group.sample(
            n=min(len(group), max_per_label),
            random_state=seed,
        )
        for _, group in frame.groupby("label", sort=True)
    ]
    sampled = (
        pd.concat(sampled_groups, ignore_index=True)
        .sample(frac=1.0, random_state=seed)
        .reset_index(drop=True)
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    sampled.to_csv(output, index=False)
    return sampled


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a reproducible per-label sample from a labeled CSV."
    )
    parser.add_argument("--input", required=True, help="Input labeled CSV path.")
    parser.add_argument("--output", required=True, help="Output sampled CSV path.")
    parser.add_argument(
        "--max-per-label",
        type=int,
        required=True,
        help="Maximum rows to keep for each label.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sampled = sample_dataset(
        input_path=args.input,
        output_path=args.output,
        max_per_label=args.max_per_label,
        seed=args.seed,
    )
    print(f"Wrote {len(sampled)} rows to {Path(args.output).resolve()}")
    print(sampled["label"].value_counts().to_string())


if __name__ == "__main__":
    main()
