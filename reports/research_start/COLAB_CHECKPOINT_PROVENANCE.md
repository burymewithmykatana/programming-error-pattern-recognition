# Colab checkpoint provenance

The `error-pattern-results/codecontests_codebert/model` folder in the user's
Google Drive contains a binary CodeBERT classifier and checkpoints. Its saved
configuration reports `microsoft/codebert-base`, max length 256, three epochs,
batch size 8, gradient accumulation 2, learning rate 2e-5, and seed 42. Its
label mapping is `correct_solution` and `syntax_error`.

The trainer state for checkpoint 3375 records three completed epochs, with the
best validation loss 0.1839567 at checkpoint 2250. This is validation loss,
not a test accuracy or F1 score. The record alone does not establish the exact
input file hashes, source dataset revision, or an independent test result.

This model is distinct from the local reduced CodeContests run recovered from
the Git branch: the latter recorded max length 128, one epoch, and batch size 2.
Do not attribute the reduced run's test metrics to the Colab model. The Drive
checkpoint was discovered through metadata; it has not been downloaded or
evaluated locally because its 498,612,824-byte weights exceed the available
Drive connector's 268,435,456-byte per-file limit.
