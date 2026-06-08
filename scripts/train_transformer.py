"""CLI placeholder for future transformer training."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from error_pattern_recognition.config import load_config
from error_pattern_recognition.training.train_transformer import train_transformer


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Train a future transformer classifier.")
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    """Run transformer training placeholder."""
    args = parse_args()
    train_transformer(args.data, load_config(args.config), args.output)


if __name__ == "__main__":
    main()
