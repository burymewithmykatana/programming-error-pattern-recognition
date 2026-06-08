"""CLI wrapper for baseline training."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from error_pattern_recognition.config import load_config
from error_pattern_recognition.training.train_baseline import train_baseline


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Train the baseline classifier.")
    parser.add_argument("--data", required=True, type=Path, help="Path to labeled CSV data.")
    parser.add_argument("--config", required=True, type=Path, help="Path to YAML config.")
    parser.add_argument("--output", required=True, type=Path, help="Output model artifact path.")
    return parser.parse_args()


def main() -> None:
    """Run baseline training."""
    args = parse_args()
    config = load_config(args.config)
    train_baseline(args.data, config, args.output)


if __name__ == "__main__":
    main()
