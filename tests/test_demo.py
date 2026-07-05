"""Tests for dashboard model discovery."""

from error_pattern_recognition.demo import available_models


def test_available_models_filters_missing_artifacts(tmp_path) -> None:
    model = tmp_path / "reports" / "experiments" / "synthetic_svm" / "model.joblib"
    model.parent.mkdir(parents=True)
    model.write_bytes(b"artifact")

    models = available_models(tmp_path)

    assert models == {"Synthetic 8-class SVM": model}
