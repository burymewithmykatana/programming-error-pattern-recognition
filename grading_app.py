"""Teacher review demo using pre-recorded synthetic outcomes only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from error_pattern_recognition.grading import build_review, finalize_review
from error_pattern_recognition.grading.exercise_library import load_mbpp, search_mbpp
from error_pattern_recognition.grading.mbpp_drafts import mbpp_to_draft
from error_pattern_recognition.grading.mbpp_review import load_findings

DATA = ROOT / "data/synthetic_grading/submissions.jsonl"
st.set_page_config(page_title="Python grading review", layout="wide")
st.title("Python grading review")
st.info("Synthetic demonstration: test outcomes are pre-recorded. This app does not run code or call an LLM.")

if not DATA.exists():
    st.error("Synthetic examples are missing. Generate them with: python scripts/generate_synthetic_grading.py")
    st.stop()

try:
    rows = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
    recorded = ROOT / "data/synthetic_grading/container_reviews.jsonl"
    if recorded.exists():
        rows.extend(json.loads(line) for line in recorded.read_text(encoding="utf-8").splitlines() if line.strip())
    if not rows:
        raise ValueError("The synthetic dataset is empty.")
    exercises = {row["exercise"]["exercise_id"]: row["exercise"] for row in rows}
except (ValueError, KeyError, TypeError) as exc:
    st.error(f"Could not read synthetic examples: {exc}")
    st.stop()

exercise_id = st.selectbox("Exercise", list(exercises))
exercise = exercises[exercise_id]
if exercise.get("research_demo_only"):
    st.warning("Controlled synthetic container evidence. Exercise and rubric require teacher approval before classroom use.")
choices = [row for row in rows if row["exercise"]["exercise_id"] == exercise_id]
selected_id = st.selectbox("Synthetic submission", [row["submission_id"] for row in choices])
record = next(row for row in choices if row["submission_id"] == selected_id)

try:
    report = build_review(record)
except (ValueError, TypeError, KeyError) as exc:
    st.error(f"Could not build a review: {exc}")
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader("Exercise")
    st.write(exercise["prompt"])
    st.code(record["student_code"], language="python")
    with st.expander("Reference solution"):
        st.code(exercise["reference_solution"], language="python")
with right:
    st.subheader("Suggested score")
    if report["suggested_points"] is None:
        st.warning("A score is unavailable because test evidence is incomplete.")
    else:
        st.metric("Points for teacher review", f"{report['suggested_points']} / {report['maximum_points']}")
    st.caption("The suggestion is recalculated from the recorded outcomes and test weights.")

st.subheader("Test evidence")
for item in report["evidence"]:
    with st.expander(f"{item['test_id']} — {item['status']} ({item['earned_points']} / {item['points']} points)"):
        st.write({"input": item["input"], "expected": item["expected"], "actual": item["actual"], "error_type": item["error_type"]})

with st.form("teacher_review"):
    st.subheader("Teacher decision")
    starting = float(report["suggested_points"]) if report["suggested_points"] is not None else 0.0
    teacher_points = st.number_input("Awarded points", min_value=0.0, max_value=float(report["maximum_points"]), value=starting, step=0.5)
    feedback = st.text_area("Feedback or reason for changing the score")
    submitted = st.form_submit_button("Prepare review")

if submitted:
    try:
        decision = finalize_review(report, teacher_points, feedback)
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.success("Review prepared. Download it to keep a copy.")
        st.download_button("Download review JSON", json.dumps(decision, indent=2, ensure_ascii=False),
                           file_name=f"{selected_id}-review.json", mime="application/json")

st.divider()
with st.expander("Browse the MBPP exercise library (teacher view)"):
    st.caption("Google Research's sanitized MBPP benchmark. Reference code and tests are shown for teacher review; nothing here is executed or connected to grading yet.")
    try:
        library = load_mbpp(ROOT / "data/exercise_library/mbpp-sanitized.json")
        findings = load_findings()
        query = st.text_input("Search questions", placeholder="e.g. list, string, prime")
        matches = search_mbpp(library, query)
        st.write(f"{len(matches)} of {len(library)} questions")
        if matches:
            selected = st.selectbox("Library exercise", matches, format_func=lambda item: f"MBPP {item['task_id']}: {item['prompt'][:100]}")
            st.write(selected["prompt"])
            if selected["task_id"] in findings:
                st.error("Known review finding: " + findings[selected["task_id"]]["reason"])
            st.caption("Reference solution")
            st.code(selected["code"], language="python")
            st.caption("Original test imports and assertions")
            st.code("\n".join(selected["test_imports"] + selected["test_list"]), language="python")
            st.warning("Review the prompt, reference, tests, and point weights before using this exercise with students.")
            draft = mbpp_to_draft(selected)
            st.write(f"Draft conversion: {draft['conversion']['converted_count']} of {draft['conversion']['original_count']} assertions converted.")
            if draft["conversion"]["warnings"]:
                st.warning(" ".join(draft["conversion"]["warnings"]))
            st.download_button("Download exercise draft JSON", json.dumps(draft, indent=2, ensure_ascii=False),
                               file_name=f"mbpp-{selected['task_id']}-draft.json", mime="application/json",
                               key="download_mbpp_draft")
        else:
            st.info("No exercises match those search terms.")
    except (OSError, ValueError, TypeError) as exc:
        st.error(f"Exercise library could not be loaded: {exc}")
