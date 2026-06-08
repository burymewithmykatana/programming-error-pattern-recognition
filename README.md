# Deep Learning-Based Recognition of Programming Error Patterns in Student Code Submissions

This repository contains a modular Pattern Recognition course project for classifying student programming submissions into common programming error categories. The first MVP targets Python code and provides a fully working classical machine learning baseline, with a clean extension point for future CodeBERT-style transformer fine-tuning.

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

## Dataset Format

The expected dataset is a CSV file with two columns:

```csv
code,label
"def add(a,b): return a+b","correct_solution"
"for i in range(10 print(i)","syntax_error"
```

A small synthetic sample is provided at `data/raw/sample.csv`.

## Training

```bash
python scripts/train_baseline.py --data data/raw/sample.csv --config configs/baseline.yaml --output models/baseline_svm.joblib
```

## Evaluation

```bash
python scripts/evaluate.py --data data/raw/sample.csv --model models/baseline_svm.joblib --output reports/baseline_eval
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
python scripts/predict.py --model models/baseline_svm.joblib --input data/raw/sample.csv --output reports/predictions.csv
```

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

The system follows a standard pattern recognition pipeline: input representation, preprocessing, feature extraction, supervised model training, evaluation, and inference. The baseline uses TF-IDF features over normalized code tokens and a linear classifier, while the future deep learning path will learn contextual code representations with transformer encoders.

## Future Work

- Add larger real-world datasets from course submissions.
- Fine-tune `microsoft/codebert-base` for sequence classification.
- Add task-aware evaluation using hidden unit tests.
- Support multi-label classification when submissions contain multiple errors.
- Build instructor dashboards and feedback generation.
