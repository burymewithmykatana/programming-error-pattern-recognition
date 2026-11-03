"""Check static mutation, exercise splits, and absence of invented labels."""
import ast
import importlib.util
from pathlib import Path

import pytest


def _load():
    spec = importlib.util.spec_from_file_location("mbpp_candidates", Path(__file__).resolve().parents[1] / "scripts/generate_mbpp_candidates.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mutations_are_static_unscored_and_keep_exercise_partition(tmp_path):
    module = _load()
    marker = tmp_path / "not-executed"
    row = {"task_id": 601, "prompt": "Add one.",
           "code": f"open({str(marker)!r}, 'w').write('bad')\ndef f(x):\n    return x + 1\n",
           "test_list": ["assert f(2) == 3"], "test_imports": []}
    result = module.make_candidates(row)
    assert not marker.exists()
    assert len(result) == 2
    assert all(item["split"] == "train" and "score" not in item for item in result)
    assert result[1]["mutation"] == {"site_index": 0, "from": "Add", "to": "Sub"}
    assert result[0]["student_code"] != result[1]["student_code"]
    for item in result:
        ast.parse(item["student_code"])
        assert item["source_assertions"] == row["test_list"]


def test_official_partition_and_ambiguous_entry():
    module = _load()
    assert [module.mbpp_split(x) for x in (2, 11, 511, 601)] == ["prompt", "test", "validation", "train"]
    with pytest.raises(ValueError):
        module.mbpp_split(975)
    row = {"task_id": 3, "prompt": "x", "code": "def f(x): return x + 1",
           "test_list": ["assert set(f([1])) == {1}"], "test_imports": []}
    assert module.make_candidates(row) == []
