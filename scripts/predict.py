"""CLI wrapper for prediction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from error_pattern_recognition.inference.predictor import Predictor


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Predict programming error labels.")
    parser.add_argument("--model", required=True, type=Path, help="Path to model artifact.")
    parser.add_argument("--code", help="Single code snippet to classify.")
    parser.add_argument("--input", type=Path, help="Input CSV for batch prediction.")
    parser.add_argument("--output", type=Path, help="Output CSV for batch prediction.")
    return parser.parse_args()


def main() -> None:
    """Run one-off or batch prediction."""
    args = parse_args()
    predictor = Predictor.from_model_path(args.model)
    if args.code:
        print(predictor.predict_one(args.code))
        return
    if args.input:
        result = predictor.predict_csv(args.input, args.output)
        if args.output is None:
            print(result.to_csv(index=False))
        return
    raise SystemExit("Provide either --code or --input.")


if __name__ == "__main__":
    main()
