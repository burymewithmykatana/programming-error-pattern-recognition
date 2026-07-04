"""CLI smoke tests for project scripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_training_prediction_and_evaluation_clis(tmp_path: Path) -> None:
    data_path = tmp_path / "dataset.csv"
    data_path.write_text(
        "code,label\n"
        "\"print(1)\",correct_solution\n"
        "\"print(2)\",correct_solution\n"
        "\"x = 1\\nprint(x)\",correct_solution\n"
        "\"total = 0\\nprint(total)\",correct_solution\n"
        "\"for i in range(10 print(i)\",syntax_error\n"
        "\"def bad(x)\\n    return x\",syntax_error\n"
        "\"if True\\n    print(1)\",syntax_error\n"
        "\"items = [1, 2, 3\\nprint(items)\",syntax_error\n",
        encoding="utf-8",
    )
    config_path = tmp_path / "baseline.yaml"
    config_path.write_text(
        "random_seed: 7\n"
        "test_size: 0.25\n"
        "strict_labels: true\n"
        "preprocessing:\n"
        "  remove_inline_comments: true\n"
        "  normalize_identifiers: false\n"
        "  normalize_numbers: false\n"
        "tfidf:\n"
        "  lowercase: false\n"
        "  ngram_range: [1, 1]\n"
        "  min_df: 1\n"
        "classifier:\n"
        "  name: linear_svc\n"
        "  C: 1.0\n",
        encoding="utf-8",
    )
    model_path = tmp_path / "model.joblib"
    report_dir = tmp_path / "reports"

    _run_cli(
        "scripts/train_baseline.py",
        "--data",
        str(data_path),
        "--config",
        str(config_path),
        "--output",
        str(model_path),
    )
    assert model_path.exists()

    prediction = _run_cli(
        "scripts/predict.py",
        "--model",
        str(model_path),
        "--code",
        "print(3)",
    )
    assert prediction.stdout.strip() in {"correct_solution", "syntax_error"}

    _run_cli(
        "scripts/evaluate.py",
        "--data",
        str(data_path),
        "--model",
        str(model_path),
        "--output",
        str(report_dir),
        "--config",
        str(config_path),
        "--holdout",
    )
    assert (report_dir / "metrics.json").exists()
    assert (report_dir / "classification_report.txt").exists()
    assert (report_dir / "confusion_matrix.csv").exists()


def test_predict_cli_requires_input_or_code(tmp_path: Path) -> None:
    data_path = tmp_path / "dataset.csv"
    data_path.write_text(
        "code,label\n"
        "\"print(1)\",correct_solution\n"
        "\"print(2)\",correct_solution\n"
        "\"x = 1\\nprint(x)\",correct_solution\n"
        "\"total = 0\\nprint(total)\",correct_solution\n"
        "\"for i in range(10 print(i)\",syntax_error\n"
        "\"def bad(x)\\n    return x\",syntax_error\n"
        "\"if True\\n    print(1)\",syntax_error\n"
        "\"items = [1, 2, 3\\nprint(items)\",syntax_error\n",
        encoding="utf-8",
    )
    config_path = tmp_path / "baseline.yaml"
    config_path.write_text(
        "preprocessing: {}\n"
        "tfidf:\n"
        "  lowercase: false\n"
        "  ngram_range: [1, 1]\n"
        "  min_df: 1\n"
        "classifier:\n"
        "  name: linear_svc\n"
        "  C: 1.0\n",
        encoding="utf-8",
    )
    model_path = tmp_path / "model.joblib"
    _run_cli(
        "scripts/train_baseline.py",
        "--data",
        str(data_path),
        "--config",
        str(config_path),
        "--output",
        str(model_path),
    )

    result = subprocess.run(
        [sys.executable, "scripts/predict.py", "--model", str(model_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Provide either --code or --input" in result.stderr


def _run_cli(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, script, *args],
        check=True,
        capture_output=True,
        text=True,
    )
