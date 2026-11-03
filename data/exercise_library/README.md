# MBPP exercise library

This folder contains the sanitized Mostly Basic Python Problems (MBPP) dataset:
427 hand-verified task records from Google Research, with task descriptions,
reference Python code, imports, and test assertions. It was created by Google
Research for the paper [Program Synthesis with Large Language Models](https://arxiv.org/abs/2108.07732).

- Original file: [sanitized-mbpp.json](https://github.com/google-research/google-research/blob/83f1e7b59e762648c953de751d31f75720683622/mbpp/sanitized-mbpp.json)
- Source commit: `83f1e7b59e762648c953de751d31f75720683622`
- File SHA-256: `ca95deaa9a01ef0a6f439f88bcf0dd3db3563d22f22aad6cae04ebb9a8d8c8e9`
- Attribution: Austin et al., Google Research, 2021. The [dataset card](https://huggingface.co/datasets/google-research-datasets/mbpp) identifies the dataset license as CC BY 4.0; the [source repository](https://github.com/google-research/google-research/blob/master/LICENSE) has an Apache 2.0 license. Preserve source, attribution and applicable terms when redistributing.

The library is for **teacher-side browsing**. It is an English-language code
generation benchmark rather than a curriculum or a set of teacher-awarded
grades. The original [dataset documentation](https://github.com/google-research/google-research/blob/master/mbpp/README.md)
describes exercise-level benchmark splits; preserve those distinctions if using
the tasks for model evaluation. The sample assertions are Python source code,
not trusted input/output records. The app displays them as text and never runs
them. A teacher must review the problem, tests, and point allocations before
assignment; reference answers and hidden tests must not be exposed to students.

Known findings are recorded in `mbpp-review-findings.json`, tied to the exact
library hash. The browser displays them, and the research queue and pilot exclude
those tasks. An unlisted task has not necessarily been checked or approved. Task
605 has a confirmed incorrect prime-number reference; task 603 needs its
terminology clarified. See `Reports/research_start/CONTAINER_PILOT.md`.

The demo can export an unapproved JSON draft. A conservative static converter
recognizes only direct function calls compared with JSON-compatible literals;
it preserves every original assertion as text and records any unsupported cases.
All points default to one and must be reviewed. No test or reference code is
executed, and drafts explicitly marked unapproved cannot be scored.
For the pinned 427-record library, static conversion found a unique entry point
and converted all original assertions for 313 exercises. Another six had only
some assertions converted, and 108 had none. These counts describe syntax
conversion, not test quality or teacher approval. Converted tests explicitly
record Python equality as the intended comparison; unsupported assertions,
including those using wrappers or non-JSON literals, remain text for review.

Do not train or evaluate a grading model solely on correct reference solutions:
they contain no student submissions or teacher scores. For a research evaluation,
keep held-out exercises separate from those used for training and selection.

The research job builder supplements training task 602 with six independently
reasoned cases in `grading/independent_cases.py`: empty and singleton strings,
adjacent and late repetition, Unicode code points, and case sensitivity. They
are bound to the exact source record and shared by reference and mutant jobs.
They avoid multiple competing repeated characters, for which the prompt needs
clarification. Test counts and origins are recorded in each job. These cases
are research drafts and do not constitute teacher approval or complete coverage.
