"""Check library loading and literal text search, with no execution."""
import json
from pathlib import Path

import pytest

from error_pattern_recognition.grading.exercise_library import load_mbpp, search_mbpp


def test_library_search_and_integrity():
    path = Path(__file__).resolve().parents[1] / "data/exercise_library/mbpp-sanitized.json"
    rows = load_mbpp(path)
    assert len(rows) == 427
    assert len({item["task_id"] for item in rows}) == len(rows)
    assert search_mbpp(rows, "2")[0]["task_id"] == 2
    assert search_mbpp(rows, "StrIng")
    assert search_mbpp(rows, "a-unique-unmatched-query-xyz") == []


def test_invalid_library_rejected_without_executing_text(tmp_path):
    marker = tmp_path / "executed"
    data = [{"task_id": 1, "prompt": "question", "code": f"open({str(marker)!r}, 'w').write('bad')",
             "test_list": ["malicious-looking text"], "test_imports": []}]
    path = tmp_path / "data.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert load_mbpp(path)[0]["code"] == data[0]["code"]
    assert not marker.exists()
    path.write_text(json.dumps(data * 2), encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        load_mbpp(path)
