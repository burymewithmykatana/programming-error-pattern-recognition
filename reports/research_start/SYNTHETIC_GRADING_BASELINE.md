# Toy synthetic grading baseline

This is a pipeline check, **not a classroom performance result**. The labels
are point totals recomputed from authored synthetic tests, not human grades. The
dataset has only 16 training submissions across four exercises and four
validation submissions from one unseen exercise. The test split was not read by
the baseline script.

The baseline is character TF-IDF and ridge regression. It takes the exercise
prompt, reference solution, test inputs/expected values/point weights, and
submission text. It does not receive test outcomes, the target score, variant
names, or mutation metadata as features. Including the rubric means the model
is permitted to see expected outputs; it is not evidence that it can run tests or
reason correctly about them. Drafts and tests remain subject to teacher review.

On the single validation exercise, mean absolute error was **0.320 of the score
range** (about 3.20 points on a 10-point rubric). Predicting the training-set
mean for every submission gave 0.325. Four examples and one exercise cannot
support a meaningful comparison, and this result must not be described as
generalization to real students or used for grades. The targets and code are
templated and therefore have strong synthetic biases.

To reproduce:

```powershell
python scripts/prepare_grading_training_data.py --output-dir data/processed/synthetic_grading_baseline
python scripts/train_grading_baseline.py --data-dir data/processed/synthetic_grading_baseline --output reports/research_start/synthetic_grading_baseline
```

The preprocessing manifest records file hashes and feature names; the baseline
outputs validation predictions and configuration details. `model.joblib` is
local and ignored by Git. Do not load untrusted joblib files. The separate MBPP
candidate variants have no score labels and were not used in this run.
