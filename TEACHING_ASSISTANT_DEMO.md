# Exercise-to-review research milestone

This demonstration connects exercises, synthetic submissions, recorded container
test results, suggested points, and a teacher decision. It requires no model
download or Docker to browse the committed evidence. CodeBERT grading and LLM
exercise generation remain future milestones.

## Run the offline demonstration

From the repository root, with Python 3.10 or newer:

```sh
python -m pip install -e ".[presentation,dev]"
python -m streamlit run grading_app.py
```

Select `mbpp-602`, then `mbpp-602-mutant-1`. The suggestion is 5/9 points;
expand the test evidence, adjust points with a reason, and download the teacher
review JSON. It retains exercise/code hashes, the original pilot/job hashes,
and the container image ID. Six additional toy exercises supply 24 deterministic
examples with correct, partially correct, and failing behavior.

## Rebuild the records without running submissions

```sh
python scripts/generate_synthetic_grading.py
python scripts/generate_mbpp_candidates.py
python scripts/prepare_mbpp_label_jobs.py --output-dir data/processed/mbpp_label_jobs
python scripts/export_mbpp_review.py --pilot reports/research_start/mbpp_602_independent_cases_pilot.json
```

The exporter reconstructs the current jobs and requires the evidence to match
their hashes and test definitions. It rejects incomplete, contradictory, stale,
or infrastructure-failed evidence and requires the reference to pass every case.
Hashes identify versions; they do not authenticate maliciously forged evidence.

## Optional controlled research execution

Only use the existing prototype for controlled synthetic research. It is not a
security-reviewed service for student submissions: submission code shares an
interpreter with its output protocol, and Docker shares the host kernel.
After ensuring a local Linux Docker engine is responsive and a local
`python:3.14.3` image is present:

```sh
python scripts/run_mbpp_label_pilot.py --exercise-id mbpp-602 --output data/processed/reproduced_602.json
python scripts/export_mbpp_review.py --pilot data/processed/reproduced_602.json
```

The committed run used immutable image ID
`sha256:da444b90434d0aaeb3420cfcc1fda68c5672e14d69a548d218c0c81834aba288`.
A tag can resolve differently later; compare image IDs before comparing results.
The reference passed 9/9 cases, and its selected mutation passed 5/9. These are
test-derived synthetic observations. They establish neither classroom grading
accuracy nor general program correctness. The reviewed rubric is still a draft.

Known defects in tasks 603 and 605 are excluded by a source-hash-bound findings
file. An unlisted exercise has not necessarily been reviewed. The 232-job queue
contains unscored train/validation candidates and preserves benchmark splits.
See [pilot evidence](reports/research_start/CONTAINER_PILOT.md) and
[dataset attribution](data/exercise_library/README.md).

## Validation

```sh
python -m pytest tests/test_pilot_review.py tests/test_grading_app.py tests/test_mbpp_review.py tests/test_independent_cases.py tests/test_container_runner.py
```

Docker integration is opt-in (`RUN_CONTAINER_TESTS=1`); normal checks consume
committed evidence and never run submissions. Model weights, raw downloads,
processed queues, training checkpoints, and local caches are excluded from Git.
