"""Run one synthetic MBPP exercise in the research container prototype.

This is not approved for real student submissions or classroom grading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from error_pattern_recognition.grading.container_runner import ContainerRunner
from error_pattern_recognition.grading.label_jobs import expected_split, stable_hash
from error_pattern_recognition.grading.mbpp_review import load_findings


def check_job(job: dict) -> None:
    expected = job.get("job_sha256")
    body = {key: value for key, value in job.items() if key != "job_sha256"}
    if expected != stable_hash(body):
        raise ValueError("Job contents do not match their recorded hash.")
    if job.get("candidate_sha256") != hashlib.sha256(job["candidate_code"].encode("utf-8")).hexdigest():
        raise ValueError("Candidate hash mismatch.")
    if job.get("tests_sha256") != stable_hash(job["tests"]):
        raise ValueError("Test hash mismatch.")
    task_id = job.get("task_id")
    if (type(task_id) is not int or job.get("exercise_id") != f"mbpp-{task_id}"
            or expected_split(task_id) != "train" or job.get("split") != "train"
            or job.get("research_only") is not True or job.get("teacher_approved") is not False):
        raise ValueError("Only explicitly unapproved training-split research jobs are allowed in this pilot.")
    if job.get("label_status") != "unscored" or job.get("reference_validation_required") is not True:
        raise ValueError("Unexpected job state.")


def run_pilot(jobs: list[dict], exercise_id: str, runner: ContainerRunner) -> dict:
    selected = [job for job in jobs if job.get("exercise_id") == exercise_id]
    if not selected:
        raise ValueError("No jobs for the selected exercise.")
    for job in selected:
        check_job(job)
    findings = load_findings()
    if selected[0]["task_id"] in findings:
        raise ValueError(f"Exercise excluded by known review finding: {findings[selected[0]['task_id']]['reason']}")
    if len({job["job_id"] for job in selected}) != len(selected):
        raise ValueError("Duplicate job IDs.")
    if len({job["tests_sha256"] for job in selected}) != 1 or len({job["function_name"] for job in selected}) != 1:
        raise ValueError("Jobs disagree about their tests or function name.")
    references = [job for job in selected if job["candidate_kind"] == "reference_copy"]
    mutants = [job for job in selected if job["candidate_kind"] == "single_operator_mutation"]
    if len(references) != 1 or not mutants:
        raise ValueError("Pilot requires one reference and at least one mutant.")
    reference, mutant = references[0], mutants[0]
    if not 1 <= len(reference["tests"]) <= 10:
        raise ValueError("Pilot requires between one and ten tests.")

    def execute(job):
        outcomes = []
        for test in job["tests"]:
            if test.get("comparison") != "python_equality" or test.get("function_name") != job["function_name"]:
                raise ValueError("Unsupported test comparison or mismatched function name.")
            result = runner.run_case(job["candidate_code"], job["function_name"], test["input"],
                                     test["keyword_input"], test["expected"])
            outcomes.append({"test_id": test["test_id"], **result})
            if result.get("status") not in {"passed", "failed", "student_error", "timeout"}:
                if result.get("status") != "infrastructure_error":
                    outcomes[-1] = {"test_id": test["test_id"], "status": "infrastructure_error",
                                    "reason": "Unexpected runner status."}
                break
        return outcomes

    reference_results = execute(reference)
    reference_passed = len(reference_results) == len(reference["tests"]) and all(x["status"] == "passed" for x in reference_results)
    result = {"exercise_id": exercise_id, "split": "train", "research_only": True, "teacher_approved": False,
              "runner_image_id": runner.image_id, "reference_job_sha256": reference["job_sha256"],
              "reference_outcomes": reference_results, "reference_passed": reference_passed,
              "candidate_job_sha256": mutant["job_sha256"], "candidate_id": mutant["job_id"],
              "candidate_outcomes": [], "provisional_passed_tests": None, "total_tests": len(reference["tests"]),
              "limitations": "Synthetic test-derived evidence only; not teacher grades or classroom-ready execution."}
    if reference_passed:
        outcomes = execute(mutant)
        result["candidate_outcomes"] = outcomes
        if len(outcomes) == len(mutant["tests"]) and all(x["status"] != "infrastructure_error" for x in outcomes):
            result["provisional_passed_tests"] = sum(x["status"] == "passed" for x in outcomes)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=Path, default=Path("data/processed/mbpp_label_jobs/jobs.jsonl"))
    parser.add_argument("--exercise-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image", default="python:3.14.3")
    args = parser.parse_args()
    jobs = [json.loads(line) for line in args.jobs.read_text(encoding="utf-8").splitlines() if line.strip()]
    result = run_pilot(jobs, args.exercise_id, ContainerRunner(args.image))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
