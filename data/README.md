# Data

Datasets should use CSV format with the required columns `code` and `label`.

Raw datasets belong in `data/raw/`. Processed outputs can be written to `data/processed/`.

## DeepMind CodeContests

Prepare a balanced Python subset while keeping the Hugging Face cache on drive D:

```bash
pip install -e .[datasets]
python scripts/prepare_code_contests.py --cache-dir D:\huggingface\code_contests --examples-per-label 10000
```

The generated CSV is written to `data/processed/code_contests_python.csv`. It contains
`correct_solution` and `syntax_error`. Parseable incorrect submissions are excluded because
CodeContests does not identify their semantic error category.

Pass `--download` only when a complete local copy of the train split is required.
