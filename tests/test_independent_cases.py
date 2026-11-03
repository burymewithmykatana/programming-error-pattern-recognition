"""Supplemental cases must enter both reference and mutant jobs unchanged."""
import copy
import json
from pathlib import Path

import pytest

from error_pattern_recognition.grading.independent_cases import independent_cases
from error_pattern_recognition.grading.label_jobs import build_label_job

ROOT = Path(__file__).resolve().parents[1]


def test_supplemental_cases_are_bound_to_source_and_shared_by_candidates():
    source = next(r for r in json.loads((ROOT / "data/exercise_library/mbpp-sanitized.json").read_text(encoding="utf-8")) if r["task_id"] == 602)
    candidates = [json.loads(line) for line in (ROOT / "data/synthetic_grading/mbpp_candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    jobs = [build_label_job(c, source)[0] for c in candidates if c["task_id"] == 602]
    assert len(jobs) > 1
    assert all(j["tests"] == jobs[0]["tests"] for j in jobs)
    assert len(jobs[0]["tests"]) == 9
    assert len({t["test_id"] for t in jobs[0]["tests"]}) == 9
    assert jobs[0]["test_provenance"] == {"source_assertions": 3, "independently_authored": 6}
    changed = copy.deepcopy(source)
    changed["prompt"] += " changed"
    with pytest.raises(ValueError, match="require review"):
        independent_cases(changed)
