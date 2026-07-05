"""Tests for transformer configuration and dependency gating."""

from pathlib import Path

import pandas as pd
import pytest

from error_pattern_recognition.models.transformer_classifier import (
    TRANSFORMER_INSTALL_HINT,
    TransformerClassifierConfig,
    TransformerCodeClassifier,
    build_label_mapping,
    missing_transformer_dependencies,
)
from error_pattern_recognition.training.train_transformer import train_transformer


def test_transformer_config_from_project_config() -> None:
    config = {
        "model": {"name": "custom-code-model", "max_length": 128, "num_labels": 4},
        "training": {"epochs": 2, "batch_size": 16, "learning_rate": 0.00003},
    }

    parsed = TransformerClassifierConfig.from_config(config)

    assert parsed.model_name == "custom-code-model"
    assert parsed.max_length == 128
    assert parsed.num_labels == 4
    assert parsed.epochs == 2
    assert parsed.batch_size == 16
    assert parsed.learning_rate == pytest.approx(0.00003)


def test_transformer_config_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="max_length"):
        TransformerClassifierConfig(max_length=0).validate()


def test_transformer_fit_validates_training_input_lengths() -> None:
    model = TransformerCodeClassifier(TransformerClassifierConfig())

    with pytest.raises(ValueError, match="same length"):
        model.fit(["print(1)"], [], "unused")


def test_transformer_predict_empty_input_short_circuits() -> None:
    model = TransformerCodeClassifier(TransformerClassifierConfig())

    assert model.predict([]) == []


def test_transformer_predict_requires_loaded_model(monkeypatch: pytest.MonkeyPatch) -> None:
    model = TransformerCodeClassifier(TransformerClassifierConfig())
    monkeypatch.setattr(
        "error_pattern_recognition.models.transformer_classifier._ensure_transformer_dependencies",
        lambda **_: None,
    )

    with pytest.raises(ValueError, match="not loaded"):
        model.predict(["print(1)"])


def test_train_transformer_passes_dataset_and_output_to_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dataset = tmp_path / "dataset.csv"
    pd.DataFrame(
        {
            "code": ["print(1)", "for i in range(10 print(i)"],
            "label": ["correct_solution", "syntax_error"],
        }
    ).to_csv(dataset, index=False)

    config = {"model": {"num_labels": 2}}
    output_path = tmp_path / "model"
    captured: dict[str, object] = {}

    def fake_fit(
        self: TransformerCodeClassifier,
        code_snippets: list[str],
        labels: list[str],
        fit_output_path: str | Path,
    ) -> TransformerCodeClassifier:
        captured["config"] = self.config
        captured["code_snippets"] = code_snippets
        captured["labels"] = labels
        captured["output_path"] = fit_output_path
        return self

    monkeypatch.setattr(TransformerCodeClassifier, "fit", fake_fit)

    model = train_transformer(dataset, config, output_path)

    assert isinstance(model, TransformerCodeClassifier)
    assert captured["code_snippets"] == ["print(1)", "for i in range(10 print(i)"]
    assert captured["labels"] == ["correct_solution", "syntax_error"]
    assert captured["output_path"] == output_path


def test_transformer_dependency_error_is_actionable() -> None:
    model = TransformerCodeClassifier(TransformerClassifierConfig())
    missing = missing_transformer_dependencies()

    if not missing:
        pytest.skip("Transformer optional dependencies are installed.")

    with pytest.raises(ImportError) as exc_info:
        model.fit(["print(1)"], ["correct_solution"], "unused")
    assert TRANSFORMER_INSTALL_HINT in str(exc_info.value)


def test_build_label_mapping_uses_supported_label_order() -> None:
    mapping = build_label_mapping(["syntax_error", "custom_label", "correct_solution"])

    assert mapping == {
        "correct_solution": 0,
        "syntax_error": 1,
        "custom_label": 2,
    }


def test_transformer_load_restores_artifact_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "transformer"
    artifact.mkdir()
    (artifact / "transformer_config.json").write_text(
        '{"model_name": "local-model", "max_length": 64, "num_labels": 2, '
        '"epochs": 1, "batch_size": 2, "learning_rate": 0.001}',
        encoding="utf-8",
    )
    (artifact / "label_mapping.json").write_text(
        '{"label_to_id": {"correct_solution": 0, "syntax_error": 1}, '
        '"id_to_label": {"0": "correct_solution", "1": "syntax_error"}}',
        encoding="utf-8",
    )
    fake_transformers = _FakeTransformers()
    monkeypatch.setattr(
        "error_pattern_recognition.models.transformer_classifier._ensure_transformer_dependencies",
        lambda **_: None,
    )
    monkeypatch.setattr(
        "error_pattern_recognition.models.transformer_classifier._import_module",
        lambda module_name: fake_transformers,
    )

    model = TransformerCodeClassifier.load(artifact)

    assert model.config.model_name == "local-model"
    assert model.config.max_length == 64
    assert model.label_to_id == {"correct_solution": 0, "syntax_error": 1}
    assert model.id_to_label == {0: "correct_solution", 1: "syntax_error"}
    assert fake_transformers.tokenizer_path == str(artifact)
    assert fake_transformers.model_path == str(artifact)


def test_transformer_predict_maps_model_outputs_to_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = TransformerCodeClassifier(TransformerClassifierConfig(max_length=32))
    model.tokenizer = _FakeTokenizer()
    model.model = _FakeModel()
    model.id_to_label = {0: "correct_solution", 1: "syntax_error"}
    monkeypatch.setattr(
        "error_pattern_recognition.models.transformer_classifier._ensure_transformer_dependencies",
        lambda **_: None,
    )
    monkeypatch.setattr(
        "error_pattern_recognition.models.transformer_classifier._import_module",
        lambda module_name: _FakeTorch(),
    )

    assert model.predict(["print(1)", "for i in range(10 print(i)"]) == [
        "syntax_error",
        "correct_solution",
    ]


class _FakeAutoTokenizer:
    def __init__(self, owner: "_FakeTransformers") -> None:
        self.owner = owner

    def from_pretrained(self, path: str) -> "_FakeTokenizer":
        self.owner.tokenizer_path = path
        return _FakeTokenizer()


class _FakeAutoModel:
    def __init__(self, owner: "_FakeTransformers") -> None:
        self.owner = owner

    def from_pretrained(self, path: str) -> "_FakeModel":
        self.owner.model_path = path
        return _FakeModel()


class _FakeTransformers:
    def __init__(self) -> None:
        self.tokenizer_path = ""
        self.model_path = ""
        self.AutoTokenizer = _FakeAutoTokenizer(self)
        self.AutoModelForSequenceClassification = _FakeAutoModel(self)


class _FakeTokenizer:
    def __call__(self, code_snippets: list[str], **_: object) -> dict[str, list[list[int]]]:
        return {"input_ids": [[len(code)] for code in code_snippets]}


class _FakeModel:
    def eval(self) -> None:
        return None

    def __call__(self, **_: object) -> "_FakeOutputs":
        return _FakeOutputs()


class _FakeOutputs:
    logits = None

    def __init__(self) -> None:
        self.logits = _FakeLogits()


class _FakeLogits:
    def argmax(self, dim: int) -> "_FakeTensor":
        assert dim == -1
        return _FakeTensor([1, 0])


class _FakeTensor:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def tolist(self) -> list[int]:
        return self.values


class _FakeNoGrad:
    def __enter__(self) -> None:
        return None

    def __exit__(self, *_: object) -> None:
        return None


class _FakeTorch:
    def no_grad(self) -> _FakeNoGrad:
        return _FakeNoGrad()
