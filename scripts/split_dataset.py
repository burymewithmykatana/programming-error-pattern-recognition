"""Create deterministic, deduplicated train and test CSV files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from error_pattern_recognition.data.loader import load_dataset
from error_pattern_recognition.data.splitter import split_dataset
from error_pattern_recognition.experiments.runner import code_fingerprint


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--train-output", required=True, type=Path)
    parser.add_argument("--test-output", required=True, type=Path)
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = load_dataset(args.data)
    frame = frame.assign(_fingerprint=frame["code"].astype(str).map(code_fingerprint))
    frame = frame.drop_duplicates("_fingerprint").drop(columns="_fingerprint")
    train, test = split_dataset(
        frame,
        test_size=args.test_size,
        random_seed=args.seed,
        stratify=True,
    )
    args.train_output.parent.mkdir(parents=True, exist_ok=True)
    args.test_output.parent.mkdir(parents=True, exist_ok=True)
    train.to_csv(args.train_output, index=False)
    test.to_csv(args.test_output, index=False)
    print(f"Wrote {len(train)} train rows and {len(test)} test rows.")


if __name__ == "__main__":
    main()
