"""Test that synthetic labels are withheld unless reference and run are complete."""
import copy
import importlib.util
from pathlib import Path

import pytest

from error_pattern_recognition.grading.label_jobs import build_label_job, stable_hash


def _module():
    path = Path(__file__).resolve().parents[1] / "scripts/run_mbpp_label_pilot.py"
    spec = importlib.util.spec_from_file_location("mbpp_pilot", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _jobs():
    source = {"task_id": 601, "prompt": "Add one", "code": "def f(x): return x + 1",
              "test_list": ["assert f(1) == 2", "assert f(2) == 3"], "test_imports": []}
    common = {"task_id": 601, "exercise_id": "mbpp-601", "split": "train", "prompt": source["prompt"],
              "reference_solution": source["code"], "source_assertions": source["test_list"],
              "source_test_imports": [], "function_name": "f"}
    ref = {**common, "candidate_id": "ref", "candidate_kind": "reference_copy", "student_code": source["code"]}
    mutant = {**common, "candidate_id": "mutant", "candidate_kind": "single_operator_mutation", "student_code": "def f(x): return x - 1"}
    return [build_label_job(ref, source)[0], build_label_job(mutant, source)[0]]


class Runner:
    image_id = "sha256:test"
    def __init__(self, reference_status="passed", mutant_status="failed"):
        self.reference_status, self.mutant_status, self.calls = reference_status, mutant_status, []
    def run_case(self, code, function, args, kwargs, expected):
        self.calls.append(code)
        return {"status": self.reference_status if "+ 1" in code else self.mutant_status}


def test_reference_gate_and_research_label():
    runner = Runner()
    result = _module().run_pilot(_jobs(), "mbpp-601", runner)
    assert result["reference_passed"] and result["provisional_passed_tests"] == 0
    assert len(runner.calls) == 4 and result["teacher_approved"] is False
    runner = Runner(reference_status="failed")
    result = _module().run_pilot(_jobs(), "mbpp-601", runner)
    assert not result["reference_passed"] and result["provisional_passed_tests"] is None
    assert len(runner.calls) == 2


def test_infrastructure_failure_withholds_score_and_tampering_rejected():
    result = _module().run_pilot(_jobs(), "mbpp-601", Runner(mutant_status="infrastructure_error"))
    assert result["provisional_passed_tests"] is None
    jobs = copy.deepcopy(_jobs())
    jobs[1]["candidate_code"] += "\n# changed"
    with pytest.raises(ValueError, match="recorded hash"):
        _module().run_pilot(jobs, "mbpp-601", Runner())


def test_unknown_runner_status_withholds_count():
    result = _module().run_pilot(_jobs(), "mbpp-601", Runner(mutant_status="unexpected"))
    assert result["candidate_outcomes"][0]["status"] == "infrastructure_error"
    assert result["provisional_passed_tests"] is None


def test_rehashed_held_out_task_cannot_claim_training_split():
    jobs = _jobs()
    for job in jobs:
        job.update(task_id=511, exercise_id="mbpp-511")
        job["job_sha256"] = stable_hash({k: v for k, v in job.items() if k != "job_sha256"})
    with pytest.raises(ValueError, match="training-split"):
        _module().run_pilot(jobs, "mbpp-511", Runner())


def test_known_defective_exercise_is_blocked_even_in_old_queue():
    jobs = _jobs()
    for job in jobs:
        job.update(task_id=605, exercise_id="mbpp-605")
        job["job_sha256"] = stable_hash({k: v for k, v in job.items() if k != "job_sha256"})
    runner = Runner()
    with pytest.raises(ValueError, match="known review finding"):
        _module().run_pilot(jobs, "mbpp-605", runner)
    assert not runner.calls
