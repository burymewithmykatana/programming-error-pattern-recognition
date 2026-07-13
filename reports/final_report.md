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
The full CodeContests training target could not be completed locally, so the project reports
a reduced CodeBERT validation run with 2,000 training rows and the same 2,059-row official
test split.

## Measured Results

| Model | Dataset | Classes | Train | Test | Accuracy | Macro F1 | Weighted F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| TF-IDF + Linear SVM | Synthetic prototype | 8 | 732 | 244 | 0.8975 | 0.9031 | 0.9005 |
| CodeBERT | Synthetic prototype | 8 | 732 | 244 | 0.5492 | 0.4390 | 0.4480 |
| TF-IDF + Linear SVM | CodeContests external validation | 2 | 19,999 | 2,059 | 0.7047 | 0.4404 | 0.8029 |
| CodeBERT reduced | CodeContests external validation | 2 | 2,000 | 2,059 | 0.6605 | 0.4583 | 0.7703 |

The synthetic experiment performs strongly on categories with visually distinct templates.
Most errors occur between correct code, variable misuse, and loop-logic mistakes.

The CodeContests test split is naturally imbalanced: 2,000 correct submissions and 59 syntax
errors. The SVM correctly identifies 1,433 correct submissions and 18 syntax errors. Its
syntax-error precision is 0.03 and recall is 0.31, so the 0.70 accuracy must not be interpreted
as strong minority-class performance.

The reduced CodeBERT run identifies 51 of 59 syntax errors, giving much higher syntax-error
recall. However, it also marks 691 correct submissions as syntax errors, so syntax-error
precision remains low at 0.07. This makes CodeBERT more useful as a high-recall triage signal
than as a final automatic judgment. Macro F1 remains the most informative summary because it
penalizes this minority-class precision problem.

## Successful External Model Study: BIFI

Because the intended full-scale CodeBERT training could not be completed, the project also
studies a successful related model: Break-It-Fix-It (BIFI) by Yasunaga and Liang. BIFI targets
program repair rather than classification. Given a parser or compiler-style critic, it learns
to convert broken code into valid code. On GitHub-Python, where the target is repairing Python
AST parse errors, BIFI reports 90.5% repair accuracy. On DeepFix C student programs, it reports
71.7% repair accuracy.

BIFI is relevant to this project because it addresses the same data problem exposed by the
CodeContests experiment: synthetic errors often do not match the distribution of real human
errors. BIFI begins with synthetic corrupted code, but then uses a critic to verify successful
fixes and to train a "breaker" that generates more realistic bad examples. This iterative
process adapts the model toward real error distributions.

Compared with this project, BIFI requires more data, more compute, a repair architecture, and
a reliable critic such as a parser or compiler. Its advantage is that it moves beyond labeling:
it can produce corrected code for parser-detectable errors. Its limitation is that parser or
compiler feedback does not automatically cover semantic errors such as wrong loop logic,
wrong conditions, or algorithmic inefficiency. For those categories, a successful future model
would need expert annotations, unit-test feedback, or another behavioral signal.

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
