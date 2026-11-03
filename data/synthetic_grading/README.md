# Synthetic grading examples

`submissions.jsonl` is a toy dataset of six hand-authored Python function
exercises and 24 synthetic submissions. Generate it from the project root:

```powershell
python scripts/generate_synthetic_grading.py
```

Each row includes the exercise, reference solution, weighted test cases, a
synthetic submission, observed test outcomes and points calculated by the
project's scoring function. The generator calls only its own fixed Python
functions; it does not execute code read from the dataset or from students.
The cases and scores were authored and computed for this demonstration, not
provided or reviewed by teachers. They are not human grading labels.

Splits are by exercise: four train, one validation and one test. The entire
benchmark is tiny and templated. It is suitable for testing the data pipeline,
not for estimating real-world grading performance or training a credible grading
model. Multiple wrong answers may accidentally pass an incomplete test suite.
Only deterministic test points are represented; style and partial reasoning are
not assessed.

The rows include both outcomes and scores for auditability. A model predicting
scores from code must not receive the target score, the `variant` label, or the
test outcomes as input: those directly reveal the target. A test-based grader,
by contrast, may consume outcomes because calculating points from them is its
defined task. Avoid tuning on the single validation/test exercises and avoid
publishing claims of generalization from these examples.

`scripts/prepare_grading_training_data.py` builds exercise-disjoint score
prediction inputs and recalculates the target from recorded outcomes. A small
TF-IDF/ridge development baseline is described in
`Reports/research_start/SYNTHETIC_GRADING_BASELINE.md`; it is not a substitute
for a CodeBERT grading model or teacher evaluation.

`mbpp_candidates.jsonl` is a separate collection of normalized reference copies
and single-operator mutations generated from MBPP exercises. Generate it with
`python scripts/generate_mbpp_candidates.py`. The generator statically parses
and compiles source for syntax checks but never executes it. Candidates have
**no correctness or score labels**; mutations can be equivalent, incorrect, or
unsafe. Each row retains attribution, original assertions, and the original
MBPP task-ID split. It is preparation for isolated test execution, not a graded
training set. The current run contains 620 candidates across 229 exercises
(169 train, 69 validation, 376 test, and 6 prompt examples). Do not include the
`candidate_kind` or `mutation` metadata as model inputs when evaluating grading;
they reveal how each example was constructed. All inherited MBPP source and
assertions are untrusted input.

`python scripts/prepare_mbpp_label_jobs.py --output-dir data/processed/mbpp_label_jobs`
prepares **unexecuted** research jobs for train and validation candidates only.
Each job records hashes for its code, tests and contents. It excludes exercises
with unsupported assertions or test imports, and flags reference validation as
required. The current output has 238 jobs from 87 exercises; it does not contain
scores or indicate teacher approval. Test and prompt splits are omitted by
default. Recreate rather than treating generated files under `data/processed/`
as the source of truth.
