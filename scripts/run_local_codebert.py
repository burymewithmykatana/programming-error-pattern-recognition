"""Run local CodeBERT workflows with conservative CPU-safe defaults.

This script does not replace the generic experiment runner. It is a convenience
wrapper for local execution on machines where Colab is unreliable and GPU
availability is uncertain.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
DEFAULT_HF_HOME = PROJECT_ROOT / ".hf_cache"


EXPERIMENTS = {
    "smoke": {
        "train_data": PROJECT_ROOT / "data/processed/synthetic/train_smoke_4_per_label.csv",
        "test_data": PROJECT_ROOT / "data/processed/synthetic/test.csv",
        "config": PROJECT_ROOT / "configs/codebert_local_smoke.yaml",
        "output": PROJECT_ROOT / "reports/experiments/codebert_smoke",
    },
    "synthetic": {
        "train_data": PROJECT_ROOT / "data/processed/synthetic/train.csv",
        "test_data": PROJECT_ROOT / "data/processed/synthetic/test.csv",
        "config": PROJECT_ROOT / "configs/codebert_local_cpu.yaml",
        "output": PROJECT_ROOT / "reports/experiments/synthetic_codebert",
    },
    "codecontests-reduced": {
        "train_data": PROJECT_ROOT
        / "data/processed/code_contests_local/train_1000_per_label.csv",
        "test_data": PROJECT_ROOT / "data/processed/code_contests/test.csv",
        "config": PROJECT_ROOT / "configs/codebert_local_cpu.yaml",
        "output": PROJECT_ROOT / "reports/experiments/codecontests_codebert_reduced",
    },
}


def ensure_venv_python() -> None:
    if not PYTHON.exists():
        raise FileNotFoundError(
            f"Expected project venv Python at {PYTHON}. Create/activate .venv first."
        )


def ensure_reduced_inputs() -> None:
    synthetic_smoke = PROJECT_ROOT / "data/processed/synthetic/train_smoke_4_per_label.csv"
    codecontests_reduced = (
        PROJECT_ROOT / "data/processed/code_contests_local/train_1000_per_label.csv"
    )
    if not synthetic_smoke.exists():
        run(
            [
                str(PYTHON),
                "scripts/sample_dataset.py",
                "--input",
                "data/processed/synthetic/train.csv",
                "--output",
                str(synthetic_smoke),
                "--max-per-label",
                "4",
                "--seed",
                "42",
            ]
        )
    if not codecontests_reduced.exists():
        run(
            [
                str(PYTHON),
                "scripts/sample_dataset.py",
                "--input",
                "data/processed/code_contests/train.csv",
                "--output",
                str(codecontests_reduced),
                "--max-per-label",
                "1000",
                "--seed",
                "42",
            ]
        )


def build_env(hf_home: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HF_HOME"] = str(hf_home)
    env["HF_HUB_DISABLE_XET"] = "1"
    env["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    return env


def run(command: list[str], *, env: dict[str, str] | None = None, dry_run: bool = False) -> None:
    print(" ".join(command))
    if dry_run:
        return
    subprocess.run(command, cwd=PROJECT_ROOT, env=env, check=True)


def run_experiment(name: str, *, env: dict[str, str], dry_run: bool = False) -> None:
    spec = EXPERIMENTS[name]
    for key in ("train_data", "test_data", "config"):
        if not spec[key].exists():
            raise FileNotFoundError(f"Missing {key} for {name}: {spec[key]}")
    run(
        [
            str(PYTHON),
            "scripts/run_experiment.py",
            "--train-data",
            str(spec["train_data"]),
            "--test-data",
            str(spec["test_data"]),
            "--model-type",
            "codebert",
            "--config",
            str(spec["config"]),
            "--output",
            str(spec["output"]),
        ],
        env=env,
        dry_run=dry_run,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "experiment",
        choices=(*EXPERIMENTS.keys(), "all"),
        help="Local CodeBERT workflow to run.",
    )
    parser.add_argument(
        "--hf-home",
        type=Path,
        default=DEFAULT_HF_HOME,
        help="Hugging Face cache directory. Defaults to .hf_cache in the project.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without running training.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_venv_python()
    env = build_env(args.hf_home.resolve())
    ensure_reduced_inputs()
    names = ["smoke", "synthetic", "codecontests-reduced"] if args.experiment == "all" else [args.experiment]
    for name in names:
        run_experiment(name, env=env, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
