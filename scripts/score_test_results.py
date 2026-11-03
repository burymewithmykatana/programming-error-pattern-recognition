"""Suggest a score from a rubric and recorded test outcomes; never execute submissions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from error_pattern_recognition.grading import score_test_results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exercise", required=True, type=Path)
    parser.add_argument("--outcomes", required=True, type=Path)
    args = parser.parse_args()
    exercise = json.loads(args.exercise.read_text(encoding="utf-8"))
    outcomes = json.loads(args.outcomes.read_text(encoding="utf-8"))
    print(json.dumps(score_test_results(exercise, outcomes), indent=2))


if __name__ == "__main__":
    main()
