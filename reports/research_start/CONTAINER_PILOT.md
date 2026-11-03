# MBPP research container pilot

This is a controlled synthetic pilot, **not a security review, teacher grade, or
classroom-ready execution service**. Docker uses a shared host kernel and the
student code executes in the same interpreter as the worker protocol; malicious
code could interfere with that protocol. Do not use this prototype for hostile
or real student submissions. A security-reviewed isolation service and protocol
are required before deployment.

The pilot selected training-split task `mbpp-606`, its normalized reference,
and one single-operator mutation. The reference passed all three statically
converted MBPP assertions; the mutation failed all three. The provisional
result is 0/3 passed tests, not a teacher-assigned score. See
`mbpp_container_pilot.json` for the exact outcomes, job hashes, and image ID.
Passing a finite test set does not establish general correctness.

Each case was run in a fresh local Linux Docker container using the existing
Python image by immutable image ID. The prototype disables networking, uses a
read-only root filesystem, drops capabilities, sets a non-root user, enables
no-new-privileges, and limits memory, CPU, processes, output, and elapsed time.
It passes the candidate its own arguments but not the expected output; the
host compares JSON-compatible results. Docker startup failures, malformed or
unsupported output, and outer timeouts become infrastructure errors rather than
student failures. These measures reduce risk but do not establish a hardened
boundary or prevent all protocol manipulation.

The research pilot requires a reference to pass all converted tests before
running its selected mutant. Infrastructure failures prevent a provisional
count. It processes one training exercise and one mutation per invocation;
the held-out splits are not touched. The job is unapproved and no labels have
been created for the wider dataset.

The job builder checks that each reference copy has the same Python syntax
tree as the source reference. The pilot also checks the task ID against the
original training partition, and treats an unknown runner status as an
infrastructure error. Job hashes detect accidental changes; they are not
signatures and cannot authenticate a deliberately modified queue. These checks
do not address interference with the worker protocol or prove correctness.

On 2026-11-03, a follow-up run for `mbpp-602` stopped before executing cases:
Docker reported a server version, but `docker info` timed out twice during
runner preflight. No result was produced by that attempt. A subsequent retry
completed after the engine became responsive.

## Additional training-split pilots

The same research runner later processed one reference and one mutation for
each exercise below, using only the original converted MBPP assertions:

| Exercise | Reference | Mutant | Result file |
| --- | --- | --- | --- |
| mbpp-602 | 3/3 | 2/3 | `mbpp_pilot_602.json` |
| mbpp-603 | 3/3 | 0/3 | `mbpp_pilot_603.json` |
| mbpp-605 | 3/3 | 3/3 | `mbpp_pilot_605.json` |

**Do not use mbpp-605 as a grading exercise without correction and review.**
Its prompt asks for a prime-number check, but its reference returns `None` for
2 and `True` for 9. Both disagree with the intended result. Its three source
assertions omit those cases, so even the faulty reference and the selected
mutation pass them all. The separately run counterexamples and image ID are in
`mbpp_605_counterexamples.json`; those cases were manually selected, not part
of the benchmark assertions. This is direct evidence that reference-validation
against existing tests is necessary but insufficient. A test-derived full
pass cannot establish correctness, and a passing mutant may be equivalent or
simply escape inadequate tests. The pilot observations are not teacher grades.

The `mbpp-603` statement says "lucid numbers" while the function and source
refer to ludic numbers; a teacher would need to clarify the terminology before
using that exercise. None of these exercises has been teacher-approved.
The known-findings list now excludes tasks 603 and 605 from newly prepared
labeling jobs and from the research pilot, including an old queue. Their prior
pilot outputs remain as historical evidence; they cannot be reproduced with
the ordinary pilot while the findings remain open. The list is bound to the
library SHA-256, and is not a claim that unlisted tasks are correct or approved.

## Independent cases for task 602

Six manually reasoned cases were added to the three original assertions for
task 602. The reference passed 9/9; the same mutant passed 5/9 (previously
2/3). The supplemental singleton, late-repetition and case-sensitivity cases
each detected another failure. The other added cases passed. See
`mbpp_602_independent_cases_pilot.json` for individual outcomes and job hashes.
The fractional change reflects a changed test set, not a measured improvement
in a learned grader. These equally weighted cases are research drafts.

The source dataset is unchanged. Supplemental tests are bound to the exact
task record and included in both reference and mutation job hashes. They avoid
the unresolved interpretation of "first" when multiple different characters
repeat, and do not establish complete correctness or teacher approval.

Reproduce after inspecting the code and verifying a local Linux Docker engine
and `python:3.14.3` image:

```powershell
python scripts/prepare_mbpp_label_jobs.py --output-dir data/processed/mbpp_label_jobs
python scripts/run_mbpp_label_pilot.py --exercise-id mbpp-606 --output reports/research_start/mbpp_container_pilot.json
```
