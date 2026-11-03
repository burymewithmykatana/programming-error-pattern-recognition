"""Test static conversion and preservation of unsupported assertions."""
from pathlib import Path

import pytest

from error_pattern_recognition.grading import score_test_results
from error_pattern_recognition.grading.exercise_library import load_mbpp
from error_pattern_recognition.grading.mbpp_drafts import mbpp_to_draft


def _row(tests):
    return {"task_id": 123, "prompt": "Compute f.", "code": "def f(x, *, scale=1):\n    return x * scale\n",
            "test_imports": [], "test_list": tests}


def test_simple_literal_assertions_become_unapproved_drafts():
    row = _row(["assert f(3, scale=2) == 6", "assert [1, 2] == f([1, 2])"])
    draft = mbpp_to_draft(row)
    assert draft["function_name"] == "f"
    assert draft["review_required"] is True and draft["approved_for_grading"] is False
    assert draft["tests"][0]["input"] == [3]
    assert draft["tests"][0]["keyword_input"] == {"scale": 2}
    assert draft["tests"][1]["expected"] == [1, 2]
    assert draft["source"]["original_assertions"] == row["test_list"]
    with pytest.raises(ValueError, match="unapproved draft"):
        score_test_results(draft, [{"test_id": test["test_id"], "status": "passed"} for test in draft["tests"]])


def test_complex_assertions_and_non_json_literals_are_not_silently_changed(tmp_path):
    marker = tmp_path / "must_not_exist"
    assertions = [f"assert f(__import__('pathlib').Path({str(marker)!r}).touch()) == 1",
                  "assert f((1, 2)) == (1, 2)", "assert set(f([1])) == {1}", "assert f(1) > 0"]
    draft = mbpp_to_draft(_row(assertions))
    assert not marker.exists()
    assert draft["tests"] == []
    assert len(draft["conversion"]["unsupported"]) == len(assertions)
    assert draft["source"]["original_assertions"] == assertions
    assert draft["function_name"] is None


def test_multiple_reference_functions_do_not_guess_an_entry_point():
    row = _row(["assert f(1) == 1", "assert g(2) == 2"])
    row["code"] += "\ndef g(x):\n    return x\n"
    draft = mbpp_to_draft(row)
    assert draft["function_name"] is None
    assert draft["conversion"]["converted_count"] == 2


def test_real_dataset_wrapped_assertions_are_retained():
    path = Path(__file__).resolve().parents[1] / "data/exercise_library/mbpp-sanitized.json"
    row = load_mbpp(path)[0]
    draft = mbpp_to_draft(row)
    assert draft["exercise_id"] == "mbpp-2"
    assert draft["conversion"]["converted_count"] == 0
    assert draft["source"]["original_assertions"] == row["test_list"]
