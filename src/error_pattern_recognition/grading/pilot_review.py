"""Join controlled research evidence to its exact jobs for offline review."""
from __future__ import annotations

from error_pattern_recognition.grading.label_jobs import build_label_job, stable_hash
from error_pattern_recognition.grading.mbpp_review import load_findings


def pilot_records(pilot: dict, jobs: list[dict], source: dict) -> list[dict]:
    """Reject stale, incomplete or contradictory evidence; never execute code."""
    task_id = source["task_id"]
    if task_id in load_findings():
        raise ValueError("Exercise has an open review finding.")
    if (pilot.get("exercise_id") != f"mbpp-{task_id}" or pilot.get("split") != "train"
            or pilot.get("research_only") is not True or pilot.get("teacher_approved") is not False):
        raise ValueError("Only training-split synthetic research evidence is supported.")
    records = []
    for kind, hash_key, outcomes_key in [("reference_copy", "reference_job_sha256", "reference_outcomes"),
                                         ("single_operator_mutation", "candidate_job_sha256", "candidate_outcomes")]:
        matches = [j for j in jobs if j.get("job_sha256") == pilot.get(hash_key)]
        if len(matches) != 1:
            raise ValueError("Evidence must match exactly one current job.")
        job = matches[0]
        candidate = {"task_id": task_id, "exercise_id": job["exercise_id"], "split": job["split"],
                     "prompt": source["prompt"], "reference_solution": source["code"],
                     "source_assertions": source["test_list"], "source_test_imports": source["test_imports"],
                     "function_name": job["function_name"], "candidate_id": job["job_id"],
                     "candidate_kind": job["candidate_kind"], "student_code": job["candidate_code"]}
        if build_label_job(candidate, source)[0] != job:
            raise ValueError("Job differs from current source or test definitions.")
        if (stable_hash({k: v for k, v in job.items() if k != "job_sha256"}) != job["job_sha256"]
                or job["candidate_kind"] != kind or job["task_id"] != task_id):
            raise ValueError("Job identity or hash mismatch.")
        outcomes = pilot.get(outcomes_key)
        if (not isinstance(outcomes, list) or len(outcomes) != len(job["tests"])
                or len({o["test_id"] for o in outcomes}) != len(outcomes)):
            raise ValueError("Incomplete or duplicate test evidence.")
        by_id = {o["test_id"]: o for o in outcomes}
        for test in job["tests"]:
            outcome = by_id.get(test["test_id"], {})
            status = outcome.get("status")
            if status not in {"passed", "failed", "student_error", "timeout"}:
                raise ValueError("Evidence unavailable or infrastructure failed.")
            if status in {"passed", "failed"} and ("actual" not in outcome or
                    (outcome["actual"] == test["expected"]) != (status == "passed")):
                raise ValueError("Recorded status contradicts the actual output.")
            if kind == "reference_copy" and status != "passed":
                raise ValueError("Reference did not pass all tests.")
        exercise = {"exercise_id": job["exercise_id"], "prompt": source["prompt"],
                    "function_name": job["function_name"], "reference_solution": source["code"],
                    "tests": job["tests"], "research_demo_only": True}
        records.append({"submission_id": job["job_id"], "split": "train", "exercise": exercise,
                        "student_code": job["candidate_code"], "outcomes": outcomes,
                        "provenance": {"kind": "controlled_synthetic_container_pilot", "teacher_approved": False,
                                       "job_sha256": job["job_sha256"], "pilot_sha256": stable_hash(pilot),
                                       "runner_image_id": pilot["runner_image_id"]}})
    return records
