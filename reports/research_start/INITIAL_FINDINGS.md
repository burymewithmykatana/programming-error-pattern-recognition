# Initial diagnostic findings

These runs use existing prepared files and are exploratory: the history of test
set use and data provenance have not yet been established. They are not a final
research comparison. See `data_audit.json` and each run's `run_config.json`,
metrics and confusion matrix for details and file hashes.

The test set has 2,000 accepted solutions and 59 parser-failing incorrect
solutions. Each model below used the same 2,000-row reduced training file and
2,059-row test file. The parser is a rule, not a trained model. Its interpretation
of syntax is tied to the Python version recorded in its run configuration.

| Method | Accuracy | Macro F1 | Syntax recall | Accepted solutions flagged |
| --- | ---: | ---: | ---: | ---: |
| Majority class | 0.971 | 0.493 | 0/59 | 0/2,000 |
| Python parser | 0.986 | 0.901 | 59/59 | 28/2,000 |
| TF-IDF/SVM, reduced training | 0.693 | 0.452 | 31/59 | 605/2,000 |

The parser's 28 disagreements with accepted-solution labels require investigation;
they do not by themselves establish which label or Python version is appropriate.
The parser labels the incorrect class, so this is a baseline for reproducing the
labeling rule rather than proof of semantic correctness. The SVM result is one
configuration, not evidence that every SVM configuration would behave similarly.
Historical CodeBERT metrics and configurations were recovered from the GitHub
`codex/presentation-ready` branch. The CodeContests run reports accuracy 0.661,
macro F1 0.458, and 51/59 syntax errors detected. Its predictions and matching
checkpoint are absent locally, and its metadata lacks dataset hashes and an exact model revision, so
the run has not been independently reproduced. The historical SVM above used
2,000 fitting rows while CodeBERT internally held out 10% for validation.
Google Drive contains a separate Colab CodeBERT model with three epochs and a
best validation checkpoint at step 2250; its configuration differs from the
one-epoch local reduced run, so it must not be identified as that run's model.

The full prepared splits have no exact normalized-code or nonempty problem-ID
overlap and no duplicate exact-code rows within a split. This does not check near
duplicates. The audit also finds 1,573 of 10,000 accepted train submissions and
33 of 2,000 accepted validation submissions fail the current parser. Original
language versions and extraction provenance should be checked before drawing
conclusions about these discrepancies.

All 2,000 reduced-training code fingerprints occur in the full prepared train
file. Re-running `sample_dataset.py` on the full train file with 1,000 per class
and seed 42 recreated the historical reduced CSV exactly in the current pandas
environment. That is consistent with the documented procedure, though it does
not independently prove the historical command or upstream dataset revision.

## Investigation of parser disagreements

All 28 test disagreements were inspected through their parser diagnostics: 27
report a missing parenthesis in a `print` call, and one reports parenthesized
lambda parameters. These are consistent with Python 2 syntax, but the CSV did
not preserve the original language ID, so individual language versions remain
unverified. Machine-readable cases and hashes are in
`parser_disagreements_test/`. The historical extraction allowed both Python 2
and Python 3 while labeling incorrect submissions using Python 3's parser;
some syntax-error labels may therefore also reflect a language-version mismatch.
The upstream [CodeContests schema](https://github.com/google-deepmind/code_contests/blob/main/contest_problem.proto)
defines ID 1 as Python 2 and ID 3 as Python 3. New extraction selects ID 3 and
retains it, but the historical results above use the original mixed files.

The prior SVM fitted all 2,000 reduced training rows. CodeBERT's current
implementation reserves 10% of its supplied training rows for early stopping;
it would fit on only 1,800. A scientifically matched comparison should give both
methods the same fitting rows and reserve the same validation rows for selection.

## Token-normalized overlap diagnostic

A second audit compared Python token sequences after removing comments and
formatting while retaining identifiers, literals and block structure. It found
zero nonidentical-code matching groups between the prepared train, validation
and test files. It excluded 614 train rows that failed tokenization, and does not
detect renamed identifiers, rewritten expressions, or other near duplicates.
See `token_overlap.json` for hashes, counts and the exact method.

## Transformer workflow smoke test

`scripts/smoke_transformer_offline.py` successfully trained, saved, reloaded,
and performed batched inference with an explicitly local, tiny random RoBERTa
model using the alternate Python environment (PyTorch 2.9.1 CPU, Transformers
4.57.3). This checks the integration path, not CodeBERT quality or the final
research dataset. The pinned CodeBERT model itself was not available locally.
