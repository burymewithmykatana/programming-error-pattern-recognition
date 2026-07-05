# Data

Datasets should use CSV format with the required columns `code` and `label`.

Raw datasets belong in `data/raw/`. Processed outputs can be written to `data/processed/`.

## DeepMind CodeContests

Prepare a balanced Python subset while keeping the Hugging Face cache on drive D:

```bash
pip install -e .[datasets]
python scripts/prepare_code_contests.py --cache-dir D:\huggingface\code_contests --examples-per-label 10000
```

The generated CSV files are written to `data/processed/code_contests/{train,valid,test}.csv`.
Each row contains `code`, `label`, `problem_id`, and `source_split`. The official Hugging Face
splits preserve problem separation. The files contain `correct_solution` and `syntax_error`;
parseable incorrect submissions are excluded because CodeContests does not identify their
semantic error category.

Normalize fingerprints and remove any duplicate code before experiments:

```bash
python scripts/sanitize_splits.py --train data/processed/code_contests/train.csv --validation data/processed/code_contests/valid.csv --test data/processed/code_contests/test.csv --output-dir data/processed/code_contests
```

Pass `--download` only when a complete local copy of the train split is required.
