# Deep Learning-Based Recognition of Programming Error Patterns in Student Code Submissions

This repository contains a modular Pattern Recognition course project for classifying student programming submissions into common programming error categories. The project targets Python code and provides a classical TF-IDF/SVM baseline, CodeBERT training and inference, leakage-safe experiments, and a Streamlit demonstration dashboard.

## Research Motivation

Introductory programming courses produce many submissions with recurring error patterns. Automatically recognizing these patterns can help instructors triage feedback, identify misconceptions, and build adaptive tutoring tools. This project treats programming error recognition as a supervised multi-class pattern recognition problem over source code.

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

Local full CodeBERT training is not recommended on low-memory GPUs. Use
`notebooks/02_codebert_colab.ipynb` with a Colab GPU for the final CodeBERT
measurements.

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

The experiment directory contains metrics, a classification report, a confusion matrix,
predictions, run metadata, timings, dataset statistics, and the trained artifact.

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
- Complete and report the two Colab CodeBERT runs.
- Add task-aware evaluation using hidden unit tests.
- Support multi-label classification when submissions contain multiple errors.
- Extend the dashboard with instructor feedback generation.

## Dashboard and presentation

```bash
pip install -e .[presentation]
streamlit run app.py
python scripts/generate_presentation.py
```

Presentation deliverables are under `presentation/`. Run
`notebooks/02_codebert_colab.ipynb` on a Colab GPU to produce the two CodeBERT experiments.
