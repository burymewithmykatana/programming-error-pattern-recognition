# Deep Learning-Based Recognition of Programming Error Patterns in Student Code Submissions

This repository contains a modular Pattern Recognition course project for classifying student programming submissions into common programming error categories. The project targets Python code and provides a classical TF-IDF/SVM baseline, CodeBERT training and inference, leakage-safe experiments, and a Streamlit demonstration dashboard.

**Current direction:** build a teaching assistant that suggests scores for Python
function submissions using exercise-specific rubrics and test evidence, with
teacher review. See [TEACHING_ASSISTANT_PLAN.md](TEACHING_ASSISTANT_PLAN.md).
The existing classifier and dashboard are historical research components; they
do not grade exercises. The review app accepts recorded test outcomes, including a controlled Docker
pilot. See [the reproducible demo](TEACHING_ASSISTANT_DEMO.md) for setup,
exercise selection, evidence export, and current limitations. Synthetic grading examples and
their limitations are described in `data/synthetic_grading/README.md`.

## Research Motivation

Introductory programming courses produce many submissions with recurring error patterns. Automatically recognizing these patterns can help instructors triage feedback, identify misconceptions, and build adaptive tutoring tools. This project treats programming error recognition as a supervised multi-class pattern recognition problem over source code.

The current real-data experiment is narrower: it compares accepted CodeContests
solutions with incorrect submissions that fail Python parsing. It does not measure
real-world multi-class semantic error recognition. See [RESEARCH_PLAN.md](RESEARCH_PLAN.md)
for the study protocol, current limitations, and diagnostic baseline commands.

## Problem Formulation

Given a code submission, predict exactly one label:

- `correct_solution`: code appears to solve the task correctly
- `syntax_error`: code cannot be parsed or contains malformed syntax
- `variable_misuse`: variables are undefined, confused, overwritten, or used inconsistently
- `loop_logic_error`: iteration bounds, updates, or loop termination are incorrect
- `conditional_logic_error`: branch conditions or boolean logic are incorrect
- `function_definition_error`: function signature, return behavior, or call structure is wrong
- `data_structure_misuse`: lists, dictionaries, sets, indexing, or mutation are used incorrectly
- `algorithmic_inefficiency`: code is functionally plausible but unnecessarily inefficient

## Installation

Use Python 3.10 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

Prepare Python training data from DeepMind CodeContests with its cache on drive D:

```bash
pip install -e .[datasets]
python scripts/prepare_code_contests.py --cache-dir D:\huggingface\code_contests
python scripts/sanitize_splits.py --train data/processed/code_contests/train.csv --validation data/processed/code_contests/valid.csv --test data/processed/code_contests/test.csv --output-dir data/processed/code_contests
```

Package the prepared CSV splits into the layout expected by the Colab notebook:

```bash
python scripts/package_colab_data.py --destination-root D:\error-pattern-data
python scripts/package_colab_project.py --output D:\error-pattern-project.zip
```

Upload or sync both files to Google Drive:

- `D:\error-pattern-data.zip` as `MyDrive/error-pattern-data.zip`
- `D:\error-pattern-project.zip` as `MyDrive/error-pattern-project.zip`

The project zip is useful when the local branch has not been pushed to GitHub.
The Colab notebook writes trained CodeBERT models and metrics to
`MyDrive/error-pattern-results`.

Transformer training is optional and requires additional dependencies:

```bash
pip install -e .[transformer]
```

Local full CodeBERT training can be demanding on low-memory GPUs. The Colab
notebook provides an alternative GPU workflow.

If Colab is unreliable, local reduced CodeBERT runs are documented in
`reports/local_codebert_runbook.md`:

```bash
.\.venv\Scripts\python.exe scripts\run_local_codebert.py synthetic
.\.venv\Scripts\python.exe scripts\run_local_codebert.py codecontests-reduced
```

## Dataset Format

Training and evaluation datasets are CSV files with two columns:

```csv
code,label
"def add(a,b): return a+b","correct_solution"
"for i in range(10 print(i)","syntax_error"
```

A small demo sample is provided at `data/raw/sample.csv`. A larger generated training dataset
with 1,000 balanced examples is available at `data/raw/curated_python_errors.csv`.

## Training

```bash
python scripts/train_baseline.py --data data/raw/curated_python_errors.csv --config configs/baseline.yaml --output models/baseline_svm.joblib
```

Run an explicit leakage-safe train/test experiment:

```bash
python scripts/run_experiment.py --train-data data/processed/synthetic/train.csv --test-data data/processed/synthetic/test.csv --model-type svm --config configs/baseline.yaml --output reports/experiments/synthetic_svm
```

To train the transformer directly (with optional dependencies installed):

```bash
python scripts/train_transformer.py --data data/processed/synthetic/train.csv --config configs/deep_model.yaml --output models/codebert
```

The experiment directory contains metrics, a classification report, a confusion matrix,
predictions, run metadata, timings, dataset statistics, and the trained artifact.

The recovered experiment reports record synthetic and reduced CodeContests
CodeBERT runs. The latter used a 2,000-row training input and the unchanged test
split; it is not a full-data run. Historical metrics and configurations are in
`reports/experiments/`, but the matching reduced-run checkpoint, predictions,
dataset hashes and model revision are unavailable, so the runs have not yet
been reproduced. A separate three-epoch CodeBERT checkpoint was found in the
Colab results folder on Google Drive; it is not the reduced-run checkpoint. The
historical CodeContests data mixed Python 2 and 3; see the research plan for the
effect on label validity.

## Evaluation

```bash
python scripts/evaluate.py --data data/raw/curated_python_errors.csv --model models/baseline_svm.joblib --output reports/baseline_holdout_eval --config configs/baseline.yaml --holdout
```

Evaluation writes:

- `metrics.json`
- `classification_report.txt`
- `confusion_matrix.csv`

## Prediction

Predict one snippet:

```bash
python scripts/predict.py --model models/baseline_svm.joblib --code "for i in range(10 print(i)"
```

Batch prediction:

```bash
python scripts/predict.py --model models/baseline_svm.joblib --input data/raw/unlabeled.csv --output reports/predictions.csv
```

Batch prediction input only needs a `code` column. If a `label` column is present, it is preserved in the output alongside `predicted_label`.

## Project Structure

```text
configs/                  Model and preprocessing configs
data/                     Raw and processed datasets
notebooks/                Exploratory analysis notebooks
src/error_pattern_recognition/
  data/                   Loading, validation, and splitting
  preprocessing/          Code cleaning and tokenization
  features/               TF-IDF feature construction
  models/                 Baseline and transformer model abstractions
  training/               Train workflows
  evaluation/             Metrics and report writers
  inference/              Prediction API
  utils/                  I/O and logging helpers
scripts/                  CLI entrypoints
tests/                    Pytest suite
```

## Relation to Pattern Recognition

The system follows a standard pattern recognition pipeline: input representation, preprocessing, feature extraction, supervised model training, evaluation, and inference. The baseline uses TF-IDF features over normalized code tokens and a linear classifier, while CodeBERT learns contextual code representations with a transformer encoder.

## Future Work

- Add larger real-world datasets from course submissions.
- Repeat and preserve CodeBERT experiment outputs, including a full-data run.
- Add task-aware evaluation using hidden unit tests.
- Support multi-label classification when submissions contain multiple errors.
- Extend the dashboard with instructor feedback generation.

## Dashboard and presentation

Run the teaching-assistant review demo with its synthetic submissions:

```bash
pip install -e .[presentation]
streamlit run grading_app.py
```

The demo displays pre-recorded outcomes, recalculates suggested scores, and lets
the teacher prepare and download a review. It also includes a searchable,
teacher-only preview of 427 sanitized MBPP exercises; see
`data/exercise_library/README.md` for attribution and limitations. MBPP tests
are displayed as text; simple literal assertions can be exported as unapproved
drafts, but they are not yet connected to grading. The app does not
yet call an LLM, run student submissions, or provide a secure execution service.
An isolated-container **research prototype** has been exercised on controlled synthetic
MBPP examples; it is not security-reviewed or suitable for real student code. See
`reports/research_start/CONTAINER_PILOT.md`.

The original classifier dashboard and presentation can be run with:

```bash
pip install -e .[presentation]
streamlit run app.py
python scripts/generate_presentation.py
```

The presentation generator uses the recovered historical metrics under
`reports/experiments/`. Review the research plan and limitations before presenting
those results as research evidence.
