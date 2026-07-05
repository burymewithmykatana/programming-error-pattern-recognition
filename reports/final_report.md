# Final Report

## Research Question

Can source-code representations recognize recurring programming-error patterns, and how well
does a prototype trained on generated labels transfer to a real submission corpus?

## Experimental Design

The project reports two deliberately separate tasks:

1. An eight-class prototype using 976 unique generated Python snippets.
2. A binary external validation using real Python submissions from DeepMind CodeContests.

The synthetic labels are `correct_solution`, `syntax_error`, `variable_misuse`,
`loop_logic_error`, `conditional_logic_error`, `function_definition_error`,
`data_structure_misuse`, and `algorithmic_inefficiency`.

CodeContests does not identify semantic error categories. Its accepted Python solutions are
therefore labeled `correct_solution`; only incorrect submissions that fail Python AST parsing
are labeled `syntax_error`. Parseable incorrect submissions are excluded rather than assigned
unsupported semantic labels.

## Leakage Controls

- Exact code is normalized for line endings and surrounding whitespace, then SHA-256 hashed.
- Duplicates within each split are removed.
- A run fails if any fingerprint occurs in both train and test.
- CodeContests uses its official train and test problem splits.
- The synthetic dataset uses a deterministic stratified 75/25 split after deduplication.

## Models

### TF-IDF + Linear SVM

The local baseline normalizes code tokens, extracts unigram and bigram TF-IDF features, and
trains a `LinearSVC`.

### CodeBERT

The project includes a Hugging Face training path and a Colab notebook for
`microsoft/codebert-base`. It uses a maximum length of 256, batch size 8, gradient
accumulation, mixed precision when CUDA is available, early stopping, and seed 42.
CodeBERT metrics are not claimed until the Colab experiments have completed.

## Measured SVM Results

| Dataset | Classes | Train | Test | Accuracy | Macro F1 | Weighted F1 |
|---|---:|---:|---:|---:|---:|---:|
| Synthetic prototype | 8 | 732 | 244 | 0.8975 | 0.9031 | 0.9005 |
| CodeContests external validation | 2 | 19,999 | 2,059 | 0.7047 | 0.4404 | 0.8029 |

The synthetic experiment performs strongly on categories with visually distinct templates.
Most errors occur between correct code, variable misuse, and loop-logic mistakes.

The CodeContests test split is naturally imbalanced: 2,000 correct submissions and 59 syntax
errors. The model correctly identifies 1,433 correct submissions and 18 syntax errors. Its
syntax-error precision is 0.03 and recall is 0.31, so the 0.70 accuracy must not be interpreted
as strong minority-class performance. Macro F1 is the more informative summary.

## Reproduction

```powershell
python scripts/split_dataset.py --data data/raw/curated_python_errors.csv `
  --train-output data/processed/synthetic/train.csv `
  --test-output data/processed/synthetic/test.csv

python scripts/run_experiment.py `
  --train-data data/processed/synthetic/train.csv `
  --test-data data/processed/synthetic/test.csv `
  --model-type svm --config configs/baseline.yaml `
  --output reports/experiments/synthetic_svm

python scripts/run_experiment.py `
  --train-data data/processed/code_contests/train.csv `
  --test-data data/processed/code_contests/test.csv `
  --model-type svm --config configs/baseline.yaml `
  --output reports/experiments/codecontests_svm
```

Run `notebooks/02_codebert_colab.ipynb` in Google Colab for the two CodeBERT experiments.

## Limitations

- The eight-class corpus is generated and does not establish classroom generalization.
- CodeContests is competitive-programming data, not an introductory classroom dataset.
- Real semantic error labels are unavailable.
- The real binary test set is strongly imbalanced.
- A submission can contain multiple errors, while the current formulation is single-label.
- Model predictions should support instructor review, not replace it.

## Conclusion

The project now provides a reproducible end-to-end system covering data preparation, leakage
checks, training, evaluation, saved artifacts, inference, and an instructor-facing demo.
Synthetic results show that the pipeline can learn the proposed taxonomy. Real-data results
show a substantially harder and more imbalanced problem, establishing an honest boundary for
the current claims. The next research step is expert annotation of real student submissions.
