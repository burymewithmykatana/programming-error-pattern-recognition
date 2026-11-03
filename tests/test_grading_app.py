"""Exercise the synthetic Streamlit teacher-review flow."""
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest


def test_synthetic_review_and_teacher_override():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "grading_app.py"), default_timeout=30).run()
    assert not app.exception
    assert "Synthetic demonstration" in app.info[0].value
    assert len(app.metric) == 1
    assert "427 of 427 questions" in [item.value for item in app.markdown]
    assert any("Draft conversion:" in item.value for item in app.markdown)
    app.text_input[0].set_value("a-unique-unmatched-query-xyz").run()
    assert any("No exercises match" in item.value for item in app.info)
    app.text_input[0].set_value("").run()
    app.selectbox[1].select("add-subtracts").run()
    assert app.metric[0].value == "2 / 10"
    app.number_input[0].set_value(0.0)
    app.button[0].click().run()
    assert not app.exception
    assert "Explain" in app.error[0].value
    app.text_area[0].set_value("Teacher reviewed the alternative solution")
    app.button[0].click().run()
    assert not app.exception
    assert "Review prepared" in app.success[0].value


def test_recorded_container_pilot_is_reviewable():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "grading_app.py"), default_timeout=60).run()
    app.selectbox[0].select("mbpp-602").run()
    app.selectbox[1].select("mbpp-602-mutant-1").run()
    assert not app.exception
    assert app.metric[0].value == "5 / 9"
    assert any("teacher approval" in w.value for w in app.warning)
