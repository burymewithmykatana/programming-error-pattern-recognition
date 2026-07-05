"""CLI wrapper for model evaluation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from error_pattern_recognition.config import load_config
from error_pattern_recognition.evaluation.evaluate import evaluate_model, evaluate_model_holdout


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Evaluate a saved classifier.")
    parser.add_argument("--data", required=True, type=Path, help="Path to labeled CSV data.")
    parser.add_argument("--model", required=True, type=Path, help="Path to model artifact.")
    parser.add_argument("--output", required=True, type=Path, help="Output report directory.")
    parser.add_argument("--config", type=Path, help="Path to YAML config for holdout evaluation.")
    parser.add_argument(
        "--holdout",
        action="store_true",
        help="Evaluate only the config-defined held-out split.",
    )
    return parser.parse_args()


def main() -> None:
    """Run evaluation."""
    args = parse_args()
    if args.holdout:
        if args.config is None:
            raise SystemExit("--config is required when using --holdout.")
        metrics = evaluate_model_holdout(args.data, args.model, args.output, load_config(args.config))
    else:
        metrics = evaluate_model(args.data, args.model, args.output)
    print(metrics)


if __name__ == "__main__":
    main()
