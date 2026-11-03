"""Train a tiny synthetic score baseline and evaluate only on validation data."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline


def read_examples(path: Path) -> tuple[list[dict], str]:
    data = path.read_bytes()
    rows = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError(f"No examples in {path}")
    for row in rows:
        for name in ("exercise_id", "submission_id", "exercise_prompt", "reference_solution", "student_code"):
            if not isinstance(row.get(name), str) or not row[name].strip():
                raise ValueError(f"Invalid {name} in {path}")
        if not isinstance(row.get("rubric_tests"), list) or not row["rubric_tests"]:
            raise ValueError(f"Invalid rubric_tests in {path}")
        target = row.get("target_fraction")
        if isinstance(target, bool) or not isinstance(target, (int, float)) or not np.isfinite(target) or not 0 <= target <= 1:
            raise ValueError(f"Invalid target_fraction in {path}")
    return rows, hashlib.sha256(data).hexdigest()


def features(row: dict) -> str:
    """Only these four fields are supplied to the estimator."""
    rubric = json.dumps(row["rubric_tests"], ensure_ascii=False, sort_keys=True)
    return f"EXERCISE\n{row['exercise_prompt']}\nREFERENCE\n{row['reference_solution']}\nRUBRIC\n{rubric}\nSUBMISSION\n{row['student_code']}"


def run(data_dir: Path, output_dir: Path) -> dict:
    train, train_hash = read_examples(data_dir / "train.jsonl")
    valid, valid_hash = read_examples(data_dir / "validation.jsonl")
    if {r["exercise_id"] for r in train} & {r["exercise_id"] for r in valid}:
        raise ValueError("Training and validation exercises must be disjoint.")
    if {r["submission_id"] for r in train} & {r["submission_id"] for r in valid}:
        raise ValueError("Training and validation submission IDs must be disjoint.")
    pipeline = make_pipeline(TfidfVectorizer(analyzer="char", ngram_range=(2, 4), max_features=10000, dtype=np.float32),
                             Ridge(alpha=1.0, solver="lsqr"))
    pipeline.fit([features(row) for row in train], [row["target_fraction"] for row in train])
    predictions = np.clip(pipeline.predict([features(row) for row in valid]), 0, 1)
    targets = np.array([row["target_fraction"] for row in valid])
    train_mean = float(np.mean([row["target_fraction"] for row in train]))
    metrics = {"validation_mae_fraction": float(np.mean(np.abs(predictions - targets))),
               "constant_mean_prediction": train_mean,
               "constant_mean_validation_mae_fraction": float(np.mean(np.abs(train_mean - targets))),
               "validation_rows": len(valid), "validation_exercises": len({row['exercise_id'] for row in valid}),
               "train_rows": len(train), "train_exercises": len({row['exercise_id'] for row in train}),
               "warning": "Toy synthetic data; outcomes are test-derived, not teacher grades. Not classroom accuracy.",
               "test_split_used": False, "train_sha256": train_hash, "validation_sha256": valid_hash,
               "python": platform.python_version(), "scikit_learn": sklearn.__version__}
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_dir / "model.joblib")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    predictions_out = [{"submission_id": row["submission_id"], "exercise_id": row["exercise_id"],
                        "target_fraction": float(target), "predicted_fraction": float(prediction)}
                       for row, target, prediction in zip(valid, targets, predictions, strict=True)]
    (output_dir / "validation_predictions.json").write_text(json.dumps(predictions_out, indent=2) + "\n", encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.data_dir, args.output), indent=2))


if __name__ == "__main__":
    main()
