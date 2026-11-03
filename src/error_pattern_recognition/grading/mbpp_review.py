"""Known MBPP defects: exclusion only, never evidence of approval."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FINDINGS = ROOT / "data/exercise_library/mbpp-review-findings.json"
DEFAULT_LIBRARY = ROOT / "data/exercise_library/mbpp-sanitized.json"


def load_findings(path: Path = DEFAULT_FINDINGS, library: Path = DEFAULT_LIBRARY) -> dict[int, dict[str, Any]]:
    """Validate the exclusion list and bind it to the exact library bytes."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Invalid MBPP findings schema.")
    digest = data.get("library_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Invalid MBPP library hash in findings.")
    if hashlib.sha256(library.read_bytes()).hexdigest() != digest:
        raise ValueError("MBPP library does not match the review findings; review is required.")
    entries = data.get("excluded")
    if not isinstance(entries, list):
        raise ValueError("MBPP exclusions must be a list.")
    result = {}
    for entry in entries:
        if (not isinstance(entry, dict) or type(entry.get("task_id")) is not int
                or entry["task_id"] <= 0 or entry["task_id"] in result
                or any(not isinstance(entry.get(k), str) or not entry[k].strip() for k in ("reason", "evidence"))):
            raise ValueError("Invalid or duplicate MBPP exclusion.")
        result[entry["task_id"]] = entry
    return result
