# Python 3-only source audit

The three supplied CodeContests Parquet files match the pinned revision's
published SHA-256 digests in `configs/codecontests-source-manifest.json`.
The extraction used Python 3.14.7 and the first unique examples encountered,
with a limit of 1,000 per class. The source split labels and problem identifiers
come from the dataset; they do not identify individual students.

The first training shard produced 1,000 accepted and 1,000 parser-failing
rejected Python 3 examples. However, accepted examples came from just three
problem IDs, syntax-error examples from seven other IDs, and the two sets had
no problem IDs in common. This is a severe sampling confound: a classifier could
learn problem or source cues correlated with the class. Do not use this training
sample for a final comparison.

The full validation and test shards each produced 1,000 accepted Python 3
examples and **zero** parser-failing rejected Python 3 examples. Extraction
therefore raised an error rather than producing a single-class evaluation file.
These files cannot support the originally proposed Python 3 syntax-error
comparison under the present labeling rule. Python parser version and source
data limitations still apply.

The source shards nevertheless contain substantial numbers of rejected Python
3 submissions: 6,908 across 96 validation problem rows and 7,273 across 114
test problem rows. The corresponding accepted counts are 8,396 and 8,248.
Counting all rejected submissions would define a different task: distinguishing
accepted from rejected contest solutions, without identifying the error type.
That option would also need problem-aware sampling and careful interpretation.
See `source_languages_train.json`, `source_languages_valid.json`, and
`source_languages_test.json` for per-language counts and source hashes.

An exact problem-name check found no shared names across the first train shard,
the validation shard and the test shard. This does not rule out renamed,
aliased or related problems; see `source_problem_overlap.json`.

The historical CodeContests test problems were already inspected in earlier
experiments, even though the new extraction differs. Future reporting should
disclose that prior exposure and avoid describing it as an entirely untouched
test set. No CodeBERT model was trained on this new data.
