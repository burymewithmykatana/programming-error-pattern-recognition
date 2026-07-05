"""Deduplicate dataset splits and remove cross-split code overlap."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from error_pattern_recognition.experiments.runner import code_fingerprint


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--test", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = {
        "train": args.train,
        "valid": args.validation,
        "test": args.test,
    }
    frames = {name: pd.read_csv(path) for name, path in paths.items()}
    seen: set[str] = set()
    cleaned: dict[str, pd.DataFrame] = {}
    for name in ("train", "valid", "test"):
        frame = frames[name].copy()
        frame["_fingerprint"] = frame["code"].astype(str).map(code_fingerprint)
        before = len(frame)
        frame = frame.drop_duplicates("_fingerprint")
        frame = frame.loc[~frame["_fingerprint"].isin(seen)]
        seen.update(frame["_fingerprint"])
        cleaned[name] = frame.drop(columns="_fingerprint")
        print(f"{name}: retained {len(frame)} of {before} rows")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in cleaned.items():
        frame.to_csv(args.output_dir / f"{name}.csv", index=False)


if __name__ == "__main__":
    main()
