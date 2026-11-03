# Research plan: programming-error detection

> Historical direction. The user's current goal is a Python teaching assistant
> that suggests exercise-specific grades for teacher review. See
> [TEACHING_ASSISTANT_PLAN.md](TEACHING_ASSISTANT_PLAN.md). The investigations
> below remain useful background and are not evidence of grading performance.

## Question and scope

How do TF-IDF/linear SVM and fine-tuned CodeBERT compare on a held-out,
imbalanced CodeContests subset containing accepted Python solutions and
parser-failing incorrect submissions? This is a binary, parser-derived task,
not a test of general semantic error recognition or introductory students.
Report the synthetic eight-class experiment separately.

## Work and acceptance criteria

1. **Data audit (started):** record file hashes, sizes, class counts, exact-code
   and problem-ID overlap, missing IDs, and parser/label disagreements. A token
   normalization audit found no cross-split matches, but excluded 614 training
   rows and does not detect all near duplicates. Inspect broader near duplicates
   and dataset version/provenance separately. Check the reduced
   training subset against all splits and document its selection procedure.
   Historical data mixed Python 2 and Python 3 without preserving language IDs;
   regenerate Python-3-only splits from a pinned upstream revision before drawing
   a final conclusion. Preserve interpreter version and extraction metadata.
2. **Reference baselines (started):** run majority class and Python parser on the
   same test set as learned models. The parser tests the labeling mechanism;
   parseability does not establish semantic correctness.
3. **Comparable model experiments:** train SVM and CodeBERT on the same reduced
   training file, choose settings using training/validation data only, and
   evaluate the frozen choices once on the held-out test set. CodeBERT holds out
   10% internally by default; use `--validation-data` to supply a separate split
   and fit on the same training rows as SVM. The runner checks exact-code overlap
   among all three files. Report the larger
   SVM training run separately. Record dataset hashes, versions, seed, hardware,
   training time, checkpoints, predictions, reports and configurations.
4. **Robustness and analysis:** repeat stochastic training across seeds when
   resources permit; report uncertainty and manually inspect representative
   false positives and false negatives. Audit near duplicates and problem
   separation; do not claim a clean split solely from exact-code checks.
5. **Research report:** describe question, related work, provenance, labels,
   methods, results, failure analysis and limitations. Historical metrics and
   configurations have been recovered from `codex/presentation-ready`; matching
   reduced-run predictions, checkpoint, data hashes and precise model revision
   remain unavailable. A separate three-epoch Colab CodeBERT model and checkpoints
   exist in Google Drive and need separate evaluation and provenance checks.
6. **Portfolio release:** reconcile local and remote histories, document setup,
   data and artifact access and licensing, run tests from a fresh environment,
   and publish the verified report and results.

## Reproduction started locally

```powershell
python scripts/audit_research_data.py --train data/processed/code_contests/train.csv --validation data/processed/code_contests/valid.csv --test data/processed/code_contests/test.csv --output Reports/research_start/data_audit.json
python scripts/run_experiment.py --train-data data/processed/code_contests_local/train_1000_per_label.csv --test-data data/processed/code_contests/test.csv --model-type parser --config configs/baseline.yaml --output Reports/research_start/parser
python scripts/run_experiment.py --train-data data/processed/code_contests_local/train_1000_per_label.csv --test-data data/processed/code_contests/test.csv --model-type majority --config configs/baseline.yaml --output Reports/research_start/majority
python scripts/run_experiment.py --train-data data/processed/code_contests_local/train_1000_per_label.csv --test-data data/processed/code_contests/test.csv --model-type svm --config configs/baseline.yaml --output Reports/research_start/svm_reduced
```

These are initial diagnostic runs, not a finalized test protocol. The reduced
training file and test split are historical artifacts; their provenance and
previous use for model selection need verification before a final claim.

The system Python lacks `transformers` and `accelerate`; another local Python
environment contains them. The alternate environment passed the local random-model
training, save, reload, and inference smoke test in
`Reports/research_start/offline_transformer_smoke/smoke_result.json`. It reported
CPU-only PyTorch. The user supplied the pinned CodeBERT checkpoint; its weights
match SHA-256 `28b61fd8fa069f6bc966f4cb9572a4026ab2a784fca8fb224020d91b744e32d6`.
It was loaded offline and produced an output with the expected shape. The
classification head is newly initialized, so this is a loading check, not a
trained result. Python 3-only dataset extraction has not yet completed; it now
requests only the three source columns used in the experiment.
Avoid using the historical test set for further selection: it has already been
examined during these diagnostics.

## Next reproducible run

**Design decision pending:** the Python 3-only validation and test shards each
yielded no parser-failing incorrect examples. The first-encounter training sample
also separates the classes entirely by problem ID. See
`Reports/research_start/PYTHON3_DATA_AUDIT.md`. Do not train or evaluate the
planned syntax-error comparison on these files as if they formed a valid split.
Consider an accepted-versus-rejected question or a different syntax-error
dataset, then specify problem-aware sampling and evaluation before training.

The pinned model is available offline. The first train shard plus validation and
test shards total 295,134,179 bytes; their pinned filenames, sizes and SHA-256
digests are in `configs/codecontests-source-manifest.json`. Preparation supports
`--local-parquet <path> --split <train|valid|test>`, recording source file hashes.
The first train shard may not contain enough examples in both classes. Verify
file hashes against the manifest and inspect counts before requesting more shards.

Once source files or working downloads are available, regenerate to a new directory using
`scripts/prepare_code_contests.py --revision 802411c3010cb00d1b05bad57ca77365a3c699d6
--output-dir data/processed/code_contests_python3`. This is the [upstream dataset
revision](https://huggingface.co/api/datasets/deepmind/code_contests) observed
during planning, not evidence of the historical dataset revision. Preserve the resulting CSVs
and `.metadata.json` files. Choose a validation and test protocol before looking
at the regenerated test results, and audit the files. Keep the historical files
and results labeled as exploratory.

For a matched CodeBERT run, pass the same training CSV used by the SVM plus a
disjoint `--validation-data` CSV to `scripts/run_experiment.py`; use a new output
directory. The explicit validation split is used by CodeBERT for early stopping;
it is not consumed by the SVM training implementation. Record model revision,
hardware, and environment independently until automated capture is complete.
`configs/codebert_research.yaml` pins the [upstream CodeBERT revision](https://huggingface.co/api/models/microsoft/codebert-base)
observed during planning. Its settings are a candidate, not a validated result.
