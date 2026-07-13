# Deep Learning-Based Recognition of Programming Error Patterns in Student Code Submissions

## Introduction

Programming courses often require instructors to inspect many student submissions that contain recurring mistakes. These mistakes include syntax problems, incorrect loop logic, variable misuse, and inefficient algorithms. Manual review is useful but time-consuming, and it can be difficult to identify course-wide error patterns quickly.

This project proposes a modular machine learning system for recognizing programming error patterns in student code submissions. The initial target language is Python, and the project is designed as a research-oriented MVP rather than a single notebook.

## Problem Statement

Given a student code submission, the system predicts one error-pattern category from a fixed label set. The classification problem is supervised, multi-class, and text/code based. The first version assumes each submission has one dominant label.

## Objectives

- Build a clean Python package for programming error pattern recognition.
- Implement robust preprocessing for Python code.
- Train a functional baseline model using TF-IDF and a linear classifier.
- Evaluate the model using standard classification metrics.
- Provide CLI commands for training, evaluation, and prediction.
- Prepare a modular transformer path for future CodeBERT fine-tuning.

## Dataset

The dataset is assumed to be a CSV file with two columns: `code` and `label`. Labels must belong to the supported error categories unless strict validation is disabled. The MVP includes a small synthetic dataset for smoke testing and demonstration.

## Methodology

The system follows a pattern recognition workflow:

1. Load and validate the dataset.
2. Clean and tokenize Python code submissions.
3. Convert code tokens into numerical features.
4. Train a supervised classifier.
5. Evaluate predictions on a held-out test split.
6. Save artifacts and reports for reproducibility.

## Baseline Models

The primary baseline uses TF-IDF vectorization over tokenized code and a linear classifier. LinearSVC is the default because it performs well for sparse high-dimensional text features. LogisticRegression is also supported through configuration.

## Deep Learning Approach

The project includes a transformer classifier based on `microsoft/codebert-base`, using a tokenizer, sequence classification head, and Hugging Face Trainer. The full target dataset is expensive to train on limited local resources, so the project reports a reduced CodeBERT run and compares it with the classical baseline.

## Related Successful Model: BIFI

To place the project results beside a successful research system, the plan includes Break-It-Fix-It (BIFI) by Yasunaga and Liang. BIFI is not a classifier; it is a program-repair method that learns to convert broken code into valid code using parser or compiler feedback as a critic. It reports strong repair accuracy on Python AST parse errors and DeepFix C compilation errors.

BIFI is useful for this project because it shows what a successful real-world error model needs: large unlabeled code corpora, a reliable critic, iterative adaptation from synthetic to realistic errors, and enough compute for transformer-style training. Its limitation is that parser/compiler feedback mainly supports syntax and compilation failures; semantic categories such as wrong loop logic still require expert labels or test-case feedback.

## Evaluation Metrics

The system reports accuracy, macro precision, macro recall, macro F1, weighted F1, a classification report, and a confusion matrix. Macro metrics are important because the error classes may be imbalanced.

## Expected Results

The baseline is expected to provide a measurable starting point on synthetic and small curated datasets. With larger real-world datasets, contextual transformer models are expected to improve performance on subtle logic and algorithmic error categories.

## Future MVP Direction

Future work should include real student submissions, task-specific context, hidden test outcomes, multi-label classification, instructor-facing feedback tools, and a BIFI-inspired training path that uses parser or unit-test feedback to reduce the gap between generated labels and real student mistakes.

## Conclusion

This project provides a practical and extensible foundation for recognizing programming error patterns in student submissions. It connects classical pattern recognition methods with modern deep learning approaches for source-code understanding.
