# Local CodeBERT Runbook

Use this when Colab is unreliable. The project venv is expected at `.venv`.

## Current local environment

- Python: project `.venv`
- PyTorch: installed
- Transformers / Accelerate / Datasets: installed
- CUDA status observed locally: `False`
- Practical implication: CodeBERT runs on CPU unless a CUDA-enabled PyTorch build is installed later.

## Prepared datasets

- Synthetic full train/test:
  - `data/processed/synthetic/train.csv`
  - `data/processed/synthetic/test.csv`
- CodeContests reduced local train:
  - `data/processed/code_contests_local/train_1000_per_label.csv`
- CodeContests official test remains unchanged:
  - `data/processed/code_contests/test.csv`

The reduced CodeContests train file contains 1,000 `correct_solution` and
1,000 `syntax_error` rows. The official test file is intentionally not reduced.

## Commands

Smoke test, not reportable:

```powershell
.\.venv\Scripts\python.exe scripts\run_local_codebert.py smoke
```

Synthetic CodeBERT, reportable:

```powershell
.\.venv\Scripts\python.exe scripts\run_local_codebert.py synthetic
```

Reduced CodeContests CodeBERT, reportable with a clear limitation:

```powershell
.\.venv\Scripts\python.exe scripts\run_local_codebert.py codecontests-reduced
```

Run both reportable local experiments:

```powershell
.\.venv\Scripts\python.exe scripts\run_local_codebert.py all
```

## Expected time

On CPU:

- smoke: under a few minutes
- synthetic: likely tens of minutes to a few hours
- CodeContests reduced: likely several hours

On a working CUDA GPU, times should be much lower. The current installed PyTorch
build reported CPU-only, so do not assume GPU acceleration.

## Output directories

- `reports/experiments/synthetic_codebert`
- `reports/experiments/codecontests_codebert_reduced`

Each experiment writes:

- `metrics.json`
- `classification_report.txt`
- `confusion_matrix.csv`
- `predictions.csv` ignored by Git
- `run_config.json`
- `model/` ignored by Git

## Reporting language

If using the reduced CodeContests result, describe it as:

> CodeBERT was trained locally on a balanced reduced CodeContests training subset
> of 2,000 rows and evaluated on the unchanged official CodeContests test split.

Do not present it as a full CodeContests CodeBERT training run.
