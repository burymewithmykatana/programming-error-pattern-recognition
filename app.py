"""Streamlit demonstration dashboard for programming-error classification."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from error_pattern_recognition.demo import (
    DEMO_EXAMPLES,
    LABEL_EXPLANATIONS,
    available_models,
)
from error_pattern_recognition.inference.predictor import Predictor

st.set_page_config(page_title="Programming Error Pattern Recognition", layout="wide")


@st.cache_resource
def load_predictor(model_path: str) -> Predictor:
    """Cache model loading across Streamlit reruns."""
    return Predictor.from_model_path(model_path)


st.title("Programming Error Pattern Recognition")
st.caption("TF-IDF/SVM and CodeBERT experiments for Python student submissions")

models = available_models(ROOT)
if not models:
    st.error("No trained model artifacts were found. Run an experiment before starting the dashboard.")
    st.stop()

model_name = st.sidebar.selectbox("Model", list(models))
model_path = models[model_name]
st.sidebar.info(
    "Synthetic models predict eight prototype labels. CodeContests models only distinguish "
    "correct solutions from syntax errors."
)

mode = st.radio("Input mode", ("Paste code", "Upload CSV"), horizontal=True)
predictor = load_predictor(str(model_path))

if mode == "Paste code":
    example_name = st.selectbox("Prepared demonstration", list(DEMO_EXAMPLES))
    code = st.text_area("Python code", value=DEMO_EXAMPLES[example_name], height=260)
    if st.button("Predict", type="primary"):
        if not code.strip():
            st.warning("Enter Python code before prediction.")
        else:
            label = predictor.predict_one(code)
            st.metric("Predicted label", label)
            st.write(LABEL_EXPLANATIONS.get(label, "No explanation is registered for this label."))
            st.caption(f"Model: {model_name}")
else:
    uploaded = st.file_uploader("CSV containing a `code` column", type=["csv"])
    if uploaded is not None:
        frame = pd.read_csv(uploaded)
        if "code" not in frame.columns:
            st.error("The uploaded CSV must contain a `code` column.")
        elif frame["code"].isna().any():
            st.error("The uploaded CSV contains missing code values.")
        else:
            result = frame.copy()
            result["predicted_label"] = predictor.predict_many(
                result["code"].astype(str).tolist()
            )
            st.dataframe(result, use_container_width=True)
            st.download_button(
                "Download predictions",
                result.to_csv(index=False).encode("utf-8"),
                "predictions.csv",
                "text/csv",
            )

st.divider()
st.subheader("Interpretation boundary")
st.write(
    "The eight-class experiment is a synthetic prototype. The CodeContests experiment uses "
    "real competitive-programming submissions but supports only two evidence-backed labels."
)
