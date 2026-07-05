# Final Report

## Project Overview

This project studies automatic recognition of programming error patterns in Python student submissions. The task is formulated as supervised multi-class classification: each code snippet is assigned exactly one error-pattern label.

The implemented pipeline covers dataset validation, preprocessing, TF-IDF feature extraction, baseline model training, evaluation, prediction, and an optional transformer extension path.

## Labels

The project supports eight labels:

- `correct_solution`
- `syntax_error`
- `variable_misuse`
- `loop_logic_error`
- `conditional_logic_error`
- `function_definition_error`
- `data_structure_misuse`
- `algorithmic_inefficiency`

## Dataset

The training dataset is `data/raw/curated_python_errors.csv`. It contains 1,000 generated Python examples, balanced across the eight labels with 125 examples per class.

This dataset is useful for reproducible experimentation and validating the full pattern-recognition pipeline. Because it is generated rather than collected from real course submissions, the reported metrics should be interpreted as prototype results, not as evidence of real classroom performance.

## Method

The primary implemented model is a classical text baseline:

1. Normalize Python code with the preprocessing pipeline.
2. Convert normalized code tokens into TF-IDF features.
3. Train a linear SVM classifier.
4. Evaluate on the held-out split defined by `configs/baseline.yaml`.

The baseline configuration uses:

- Train/test split: 75% / 25%
- Random seed: 42
- Identifier normalization: enabled
- Number normalization: enabled
- TF-IDF n-grams: 1 to 2
- Classifier: LinearSVC

## Results

The trained baseline model was evaluated on the held-out 250-example split.

| Metric | Value |
|---|---:|
| Accuracy | 0.892 |
| Macro precision | 0.905 |
| Macro recall | 0.891 |
| Macro F1 | 0.895 |
| Weighted F1 | 0.896 |

Per-class performance was strongest for `syntax_error`, `conditional_logic_error`, `function_definition_error`, `data_structure_misuse`, and `algorithmic_inefficiency`, each reaching perfect held-out F1 on this generated dataset.

The main confusion occurred among:

- `correct_solution`
- `variable_misuse`
- `loop_logic_error`

This is expected because the generated examples for these classes share similar token patterns and differ more by semantic behavior than by obvious lexical structure.

## Reproducibility

Generate the dataset:

```bash
python scripts/generate_curated_dataset.py --output data/raw/curated_python_errors.csv --examples-per-label 125
```

Train the baseline:

```bash
python scripts/train_baseline.py --data data/raw/curated_python_errors.csv --config configs/baseline.yaml --output models/baseline_svm.joblib
```

Evaluate on the held-out split:

```bash
python scripts/evaluate.py --data data/raw/curated_python_errors.csv --model models/baseline_svm.joblib --output reports/baseline_holdout_eval --config configs/baseline.yaml --holdout
```

## Transformer Extension

The project includes an optional Hugging Face transformer path for CodeBERT-style sequence classification. It supports configuration parsing, label mapping, model training, artifact saving, artifact loading, and inference. Transformer dependencies are optional and can be installed with:

```bash
pip install -e .[transformer]
```

The transformer path is prepared for deeper experimentation, but the baseline SVM remains the primary reproducible result for this report.

## Limitations

- The dataset is generated, not collected from real student submissions.
- Each snippet has exactly one label, while real submissions may contain multiple errors.
- Some labels require semantic reasoning that TF-IDF features only approximate.
- Evaluation on real course data may be substantially lower than the generated-dataset result.
- The current dashboard and multi-user workflow are not implemented yet.

## Conclusion

The project now provides a complete pattern-recognition pipeline for Python programming error classification. The TF-IDF plus LinearSVC baseline reaches 0.895 macro F1 on the held-out generated dataset, demonstrating that the implemented pipeline is functional and reproducible. The next major step is validating the approach on real anonymized student submissions and adding a dashboard for instructor-facing analysis.
