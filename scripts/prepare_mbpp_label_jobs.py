"""Prepare unexecuted MBPP labeling jobs from eligible static candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from error_pattern_recognition.grading.exercise_library import load_mbpp
from error_pattern_recognition.grading.label_jobs import build_label_job
from error_pattern_recognition.grading.mbpp_review import DEFAULT_FINDINGS, load_findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=Path("data/exercise_library/mbpp-sanitized.json"))
    parser.add_argument("--candidates", type=Path, default=Path("data/synthetic_grading/mbpp_candidates.jsonl"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--findings", type=Path, default=DEFAULT_FINDINGS)
    parser.add_argument("--splits", nargs="+", choices=("train", "validation", "test", "prompt"),
                        default=["train", "validation"], help="Default leaves test and prompt jobs unprepared.")
    args = parser.parse_args()
    library_bytes, candidate_bytes = args.library.read_bytes(), args.candidates.read_bytes()
    findings = load_findings(args.findings, args.library)
    library = {item["task_id"]: item for item in load_mbpp(args.library)}
    candidates = [json.loads(line) for line in candidate_bytes.decode("utf-8").splitlines() if line.strip()]
    jobs, excluded, seen = [], Counter(), set()
    for candidate in candidates:
        task_id = candidate.get("task_id")
        if task_id not in library:
            raise ValueError(f"Candidate references unknown task: {task_id}")
        if task_id in findings:
            excluded["known_review_finding"] += 1
            continue
        job, reason = build_label_job(candidate, library[task_id])
        if reason:
            excluded[reason] += 1
        elif job["split"] not in args.splits:
            excluded["split_not_requested"] += 1
        elif job["job_id"] in seen:
            raise ValueError(f"Duplicate job ID: {job['job_id']}")
        else:
            seen.add(job["job_id"])
            jobs.append(job)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(job, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n" for job in jobs).encode("utf-8")
    (args.output_dir / "jobs.jsonl").write_bytes(payload)
    summary = {"purpose": "Unexecuted synthetic research jobs; no scores and no teacher approval.",
               "library_sha256": hashlib.sha256(library_bytes).hexdigest(),
               "candidates_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
               "review_findings_sha256": hashlib.sha256(args.findings.read_bytes()).hexdigest(),
               "review_scope": "Known defects excluded; remaining exercises are not approved or verified.",
               "jobs_sha256": hashlib.sha256(payload).hexdigest(), "requested_splits": args.splits,
               "jobs": len(jobs), "jobs_by_split": dict(Counter(job["split"] for job in jobs)),
               "exercises_by_split": {split: len({job['exercise_id'] for job in jobs if job['split'] == split}) for split in args.splits},
               "excluded_candidates_by_reason": dict(sorted(excluded.items()))}
    (args.output_dir / "manifest.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
