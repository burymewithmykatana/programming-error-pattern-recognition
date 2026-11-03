"""Prepare exercise-disjoint score-prediction files from recorded outcomes."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from error_pattern_recognition.grading.training_data import prepare_examples


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/synthetic_grading/submissions.jsonl"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.input.read_bytes()
    rows = [json.loads(line) for line in source.decode("utf-8").splitlines() if line.strip()]
    splits = prepare_examples(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"source": str(args.input), "source_sha256": hashlib.sha256(source).hexdigest(),
                "label_provenance": "Scores recomputed from supplied test outcomes; not teacher grades.",
                "model_input_fields": ["exercise_prompt", "reference_solution", "rubric_tests", "student_code"],
                "target": "target_fraction", "splits": {}}
    for name, examples in splits.items():
        payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in examples).encode("utf-8")
        (args.output_dir / f"{name}.jsonl").write_bytes(payload)
        manifest["splits"][name] = {"rows": len(examples), "exercises": len({row['exercise_id'] for row in examples}),
                                    "sha256": hashlib.sha256(payload).hexdigest()}
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
