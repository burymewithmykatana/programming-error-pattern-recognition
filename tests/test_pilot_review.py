"""Verify the container evidence to teacher-review bridge without Docker."""
import copy
import json
from pathlib import Path

import pytest

from error_pattern_recognition.grading.pilot_review import pilot_records
from error_pattern_recognition.grading.label_jobs import build_label_job
from error_pattern_recognition.grading import build_review, finalize_review

ROOT = Path(__file__).resolve().parents[1]


def inputs():
    source = next(r for r in json.loads((ROOT / "data/exercise_library/mbpp-sanitized.json").read_text(encoding="utf-8")) if r["task_id"] == 602)
    candidates = [json.loads(line) for line in (ROOT / "data/synthetic_grading/mbpp_candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    jobs = [build_label_job(c, source)[0] for c in candidates if c["task_id"] == 602]
    pilot = json.loads((ROOT / "reports/research_start/mbpp_602_independent_cases_pilot.json").read_text(encoding="utf-8"))
    return pilot, jobs, source


def test_container_evidence_reaches_teacher_review():
    rows = pilot_records(*inputs())
    assert [build_review(r)["suggested_points"] for r in rows] == ["9", "5"]
    report = build_review(rows[1])
    decision = finalize_review(report, 6, "Teacher grants additional approach credit")
    assert decision["teacher_points"] == "6"
    assert decision["provenance"]["teacher_approved"] is False
    assert decision["provenance"]["job_sha256"]


@pytest.mark.parametrize("fault", ["stale", "missing", "contradictory", "reference_failed"])
def test_invalid_pilot_cannot_be_exported(fault):
    pilot, jobs, source = inputs()
    pilot = copy.deepcopy(pilot)
    if fault == "stale":
        pilot["candidate_job_sha256"] = "0" * 64
    elif fault == "missing":
        pilot["candidate_outcomes"].pop()
    elif fault == "contradictory":
        pilot["candidate_outcomes"][0]["actual"] = "wrong"
    else:
        pilot["reference_outcomes"][0]["status"] = "failed"
    with pytest.raises(ValueError):
        pilot_records(pilot, jobs, source)
