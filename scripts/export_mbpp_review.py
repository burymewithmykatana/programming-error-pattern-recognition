"""Export controlled pilot evidence into offline synthetic teacher-review records."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from error_pattern_recognition.grading.pilot_review import pilot_records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--jobs", type=Path, default=Path("data/processed/mbpp_label_jobs/jobs.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/synthetic_grading/container_reviews.jsonl"))
    args = parser.parse_args()
    pilot = json.loads(args.pilot.read_text(encoding="utf-8"))
    jobs = [json.loads(line) for line in args.jobs.read_text(encoding="utf-8").splitlines() if line.strip()]
    library = json.loads(Path("data/exercise_library/mbpp-sanitized.json").read_text(encoding="utf-8"))
    source = next(r for r in library if f"mbpp-{r['task_id']}" == pilot["exercise_id"])
    rows = pilot_records(pilot, jobs, source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    print(f"Exported {len(rows)} synthetic research review records to {args.output}")


if __name__ == "__main__":
    main()
