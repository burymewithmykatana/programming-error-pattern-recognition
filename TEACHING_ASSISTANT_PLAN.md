# Research and implementation plan: Python teaching assistant

## Goal

Help a teacher grade Python **functions**. Given an exercise, an LLM can propose
a reference implementation, input/output cases, and a rubric. The teacher reviews
these before use. For each student submission, the system should eventually
execute the tests in isolation, combine their outcomes according to the rubric,
and suggest points and evidence for the teacher to review. The teacher retains
the final decision.

The existing TF-IDF/SVM and CodeBERT models classify code snippets; they do not
take exercise requirements into account or predict reliable grades. Their earlier
results remain historical research and must not be represented as grading
performance. Likewise, a single LLM-generated solution is a draft: different
implementations may be equally correct, and the reference or its tests may be
wrong or incomplete.

## Workflow

1. The teacher supplies a problem statement, function name, input/output contract,
   point allocation, and any constraints. An LLM may draft a reference solution,
   cases for ordinary inputs and edge cases, and a rubric. The teacher corrects
   and approves them; the initial version need not depend on a particular LLM.
2. Validate the reference and tests together, including independently authored
   examples. Preserve the exercise and test versions used for each grading run.
3. Run student functions against the approved tests in a properly isolated
   execution environment with time, memory, process, filesystem, network, and
   output limits. An ordinary subprocess or Python `exec` is not a security
   boundary. Record infrastructure failures separately from student failures.
4. Compute points from explicit test outcomes and rubric weights. Provide the
   teacher with per-test evidence, uncertainty, and a suggested score. The
   teacher can correct the score and record the reason. Hidden tests should not
   be exposed to students through feedback.
5. Optionally use a model for rubric-guided explanations or additional review.
   Student code and comments are untrusted data, not instructions to the model.
   Validate model output against the rubric and measured evidence; record model
   version and prompt. Teacher review remains mandatory for the first version.

## Research question and evaluation

How closely do test-based and rubric-guided grading suggestions agree with
teacher grades on **unseen exercises**, and what kinds of submissions cause
disagreement? Compare a test-only baseline, an LLM/rubric baseline if available,
and a hybrid approach. A small code classifier is a candidate only if it is
trained and evaluated on suitable exercise-and-grade examples; the existing
error-label classifier is not a grading model.

Collect exercise statements, reference solutions, versioned tests and rubrics,
student submissions, human grades, and reasons for point deductions, with
appropriate permission and anonymization. Where possible, have a second teacher
independently grade a subset to measure human disagreement. Split by exercise,
not submission, and keep a set of exercises untouched during model and prompt
selection. Report exact agreement, mean absolute point error, direction of error,
per-exercise results, failures on edge cases, cost and runtime. Review both
over-grading and under-grading, including alternative correct solutions.

For early development, use the deterministic synthetic examples in
`data/synthetic_grading/`. They provide exercise-disjoint toy splits and scores
computed from authored tests; they are not human grades or evidence of classroom
performance. Keep target scores, variant labels, and outcomes out of inputs to a
model trained to predict a score directly from code.

A small character-TF-IDF/ridge baseline now tests this data path, with a constant
mean comparator and exercise-disjoint validation. It uses test-derived toy
scores, not human grades, and its four validation examples are far too few to
support a research claim. See `reports/research_start/SYNTHETIC_GRADING_BASELINE.md`.
The model inputs contain the prompt, reference, rubric tests, and student code;
the recorded outcomes and targets are excluded from the features.

The supplied CodeContests shards may support exploratory accepted/rejected
experiments, but they do not supply teacher rubrics or partial-credit grades and
are not a substitute for this evaluation. The prior syntax-error experiment
has no Python 3 parse-failing cases in its validation and test shards; see
`reports/research_start/PYTHON3_DATA_AUDIT.md`.

The sanitized MBPP library offers 427 example Python function exercises,
reference solutions, and assertions for teacher-side browsing. It does not
include student submissions or partial-credit scores. See
`data/exercise_library/README.md` for provenance, attribution and limitations.
MBPP's assertions are source code, not the input/output test format used by the
current scoring prototype. The library can statically export unapproved drafts
for simple literal assertions and retains unsupported assertions for review; it
never executes them. It also has an unscored static mutation generator for
candidate solutions, but these are not grading labels. The current candidate
set contains 620 normalized references and operator mutants across 229 MBPP
exercises, assigned to the benchmark's original exercise-level splits. Mutants
may be equivalent to the reference or unsafe to run, so they must be evaluated
in isolation before any scores are attached.

The prepared research labeling queue contains 232 train/validation jobs with
hashes binding each candidate and its tests. It omits test and prompt tasks by
default, excludes unsupported assertions and test imports, and requires the
reference to be checked before labels are derived. These jobs are unexecuted,
not approved for teaching and have no scores.
Reference-copy syntax trees are checked against their source, and the pilot
checks task IDs against the original training partition. The hashes detect
changes but do not authenticate a queue against intentional modification.
In an exploratory pilot, MBPP task 605's reference passed its three assertions
despite returning incorrect results for 2 and 9. Exclude this exercise from
teaching use until corrected and reviewed, and do not infer reference correctness
from passing source tests. See `reports/research_start/CONTAINER_PILOT.md`.
The shared `data/exercise_library/mbpp-review-findings.json` excludes the two
known problematic exercises from the queue and research pilot and records a hash
of the source library. This is a list of known defects, not a list of approved
exercises. Corrections require review and a new versioned source; editing the
list alone does not establish correctness.

## Current implementation and next steps

The repository includes a **synthetic teacher-review demo**: it shows an
exercise and submission, recalculates points from recorded test outcomes,
displays per-test evidence, and lets the teacher adjust points, explain a change,
and download a review. It hashes the exercise and code for traceability. It does
not call an LLM, execute a reference or student code, or verify expected outputs.
Missing outcomes or infrastructure failures prevent a suggested score. Run:

```powershell
pip install -e .[presentation]
streamlit run grading_app.py
```

The underlying scoring foundation can also be invoked without the UI:

```powershell
python scripts/score_test_results.py --exercise examples/grading/add_exercise.json --outcomes examples/grading/add_outcomes.json
```

Next, use the synthetic exercises to develop the pipeline and evaluate basic
failure cases. Implement a draft-generation
adapter with explicit teacher review, then a separately isolated execution
service, before connecting execution evidence to the scoring foundation. A later
real-world evaluation still requires teacher-reviewed exercises, grades, and
appropriate data permissions. Only after an end-to-end baseline and a suitable
grading dataset exist should model training or claims about grading quality be
considered.

The research-only container prototype fails closed if its local Linux Docker
environment is unavailable. A controlled pilot on one MBPP training exercise
is documented in `reports/research_start/CONTAINER_PILOT.md`. It is not
security-reviewed or suitable for real student submissions. The future runner must send the
candidate only the function arguments for one test, never the expected value or
other hidden tests; compare bounded, validated outputs in a trusted component.
Use separate isolated executions with resource and wall-clock limits, retain
infrastructure errors separately, and verify that the reference passes the
reviewed cases before producing synthetic labels. A container alone should not
be represented as a complete security boundary against hostile submissions;
the runner and its isolation need an explicit security review and end-to-end
tests. Docker was running during the controlled pilot.

## References

- [Automated Grading and Feedback Tools for Programming Education: A Systematic Review](https://arxiv.org/abs/2306.11722)
- [Automating Autograding: Large Language Models as Test Suite Generators for Introductory Programming](https://arxiv.org/abs/2411.09261)
- [How Consistent Are Humans When Grading Programming Assignments?](https://arxiv.org/abs/2409.12967)
