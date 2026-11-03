"""Known defects are excluded, and a stale review file cannot silently pass."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from error_pattern_recognition.grading.mbpp_review import load_findings

ROOT = Path(__file__).resolve().parents[1]


def test_review_findings_are_bound_to_library_and_unique(tmp_path):
    library = tmp_path / "library.json"
    library.write_text("[]", encoding="utf-8")
    findings = tmp_path / "findings.json"
    data = {"schema_version": 1, "library_sha256": hashlib.sha256(library.read_bytes()).hexdigest(),
            "excluded": [{"task_id": 605, "reason": "bad reference", "evidence": "report.json"}]}
    findings.write_text(json.dumps(data), encoding="utf-8")
    assert 605 in load_findings(findings, library)
    data["excluded"].append(data["excluded"][0])
    findings.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_findings(findings, library)
    library.write_text("[1]", encoding="utf-8")
    with pytest.raises(ValueError, match="does not match"):
        load_findings(findings, library)


def test_prepared_queue_excludes_all_known_findings(tmp_path):
    completed = subprocess.run([sys.executable, str(ROOT / "scripts/prepare_mbpp_label_jobs.py"),
                                "--output-dir", str(tmp_path)], cwd=ROOT, capture_output=True, text=True, check=True)
    manifest = json.loads(completed.stdout)
    jobs = [json.loads(line) for line in (tmp_path / "jobs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert manifest["excluded_candidates_by_reason"]["known_review_finding"] > 0
    assert not {603, 605}.intersection(job["task_id"] for job in jobs)
    assert manifest["review_findings_sha256"]
    assert any(job["task_id"] == 602 for job in jobs)
