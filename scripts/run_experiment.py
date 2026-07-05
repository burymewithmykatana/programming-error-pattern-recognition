"""Run a leakage-safe SVM or CodeBERT experiment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from error_pattern_recognition.config import load_config
from error_pattern_recognition.experiments.runner import run_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-data", required=True, type=Path)
    parser.add_argument("--test-data", required=True, type=Path)
    parser.add_argument("--model-type", required=True, choices=("svm", "codebert"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics = run_experiment(
        train_data=args.train_data,
        test_data=args.test_data,
        model_type=args.model_type,
        config=load_config(args.config),
        output_dir=args.output,
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
