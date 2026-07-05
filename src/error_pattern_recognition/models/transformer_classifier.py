"""Transformer-based classifier interfaces."""

from dataclasses import asdict, dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from error_pattern_recognition.constants import SUPPORTED_LABELS
from error_pattern_recognition.utils.io import read_json, write_json

TRANSFORMER_RUNTIME_DEPENDENCIES = ("torch", "transformers")
TRANSFORMER_TRAINING_DEPENDENCIES = (*TRANSFORMER_RUNTIME_DEPENDENCIES, "accelerate")
TRANSFORMER_DEPENDENCIES = TRANSFORMER_TRAINING_DEPENDENCIES
TRANSFORMER_INSTALL_HINT = (
    "Transformer support requires optional dependencies. Install them with "
    "`pip install -e .[transformer]` before using transformer training or inference."
)


@dataclass(frozen=True)
class TransformerClassifierConfig:
    """Configuration for a Hugging Face sequence classifier."""

    model_name: str = "microsoft/codebert-base"
    max_length: int = 256
    num_labels: int = 8
    epochs: int = 3
    batch_size: int = 8
    learning_rate: float = 2e-5

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "TransformerClassifierConfig":
        """Build transformer settings from the project config mapping."""
        model_config = config.get("model", {})
        training_config = config.get("training", {})
        return cls(
            model_name=str(model_config.get("name", cls.model_name)),
            max_length=int(model_config.get("max_length", cls.max_length)),
            num_labels=int(model_config.get("num_labels", cls.num_labels)),
            epochs=int(training_config.get("epochs", cls.epochs)),
            batch_size=int(training_config.get("batch_size", cls.batch_size)),
            learning_rate=float(training_config.get("learning_rate", cls.learning_rate)),
        ).validate()

    def validate(self) -> "TransformerClassifierConfig":
        """Validate numeric transformer settings."""
        if not self.model_name.strip():
            raise ValueError("Transformer model name must be non-empty.")
        if self.max_length <= 0:
            raise ValueError("Transformer max_length must be positive.")
        if self.num_labels <= 1:
            raise ValueError("Transformer num_labels must be greater than one.")
        if self.epochs <= 0:
            raise ValueError("Transformer epochs must be positive.")
        if self.batch_size <= 0:
            raise ValueError("Transformer batch_size must be positive.")
        if self.learning_rate <= 0:
            raise ValueError("Transformer learning_rate must be positive.")
        return self


class TransformerCodeClassifier:
    """Dependency-gated CodeBERT-style classifier interface."""

    def __init__(self, config: TransformerClassifierConfig) -> None:
        self.config = config.validate()
        self.label_to_id: dict[str, int] = {}
        self.id_to_label: dict[int, str] = {}
        self.tokenizer: Any | None = None
        self.model: Any | None = None

    @classmethod
    def load(cls, path: str | Path) -> "TransformerCodeClassifier":
        """Load a saved transformer classifier artifact."""
        artifact_path = Path(path)
        if not artifact_path.exists():
            raise FileNotFoundError(f"Transformer artifact not found: {artifact_path}")
        if not artifact_path.is_dir():
            raise ValueError(f"Transformer artifact path is not a directory: {artifact_path}")
        _ensure_transformer_dependencies(training=False)

        config = TransformerClassifierConfig(**read_json(artifact_path / "transformer_config.json"))
        mapping = read_json(artifact_path / "label_mapping.json")
        classifier = cls(config)
        classifier.label_to_id = _coerce_label_to_id(mapping.get("label_to_id"))
        classifier.id_to_label = _coerce_id_to_label(mapping.get("id_to_label"))

        transformers = _import_module("transformers")
        classifier.tokenizer = transformers.AutoTokenizer.from_pretrained(str(artifact_path))
        classifier.model = transformers.AutoModelForSequenceClassification.from_pretrained(
            str(artifact_path)
        )
        classifier.model.eval()
        return classifier

    def fit(
        self,
        code_snippets: list[str],
        labels: list[str],
        output_path: str | Path,
    ) -> "TransformerCodeClassifier":
        """Fine-tune a Hugging Face sequence classifier and save the artifact."""
        if not code_snippets:
            raise ValueError("Transformer training requires at least one code snippet.")
        if len(code_snippets) != len(labels):
            raise ValueError("Code snippets and labels must have the same length.")
        _ensure_transformer_dependencies(training=True)

        torch = _import_module("torch")
        transformers = _import_module("transformers")

        self.label_to_id = build_label_mapping(labels)
        self.id_to_label = {identifier: label for label, identifier in self.label_to_id.items()}
        encoded_labels = [self.label_to_id[label] for label in labels]

        tokenizer = transformers.AutoTokenizer.from_pretrained(self.config.model_name)
        model = transformers.AutoModelForSequenceClassification.from_pretrained(
            self.config.model_name,
            num_labels=len(self.label_to_id),
            id2label={str(identifier): label for identifier, label in self.id_to_label.items()},
            label2id=self.label_to_id,
        )
        train_dataset = _TokenizedCodeDataset(
            tokenizer=tokenizer,
            code_snippets=code_snippets,
            labels=encoded_labels,
            max_length=self.config.max_length,
            torch_module=torch,
        )

        artifact_path = Path(output_path)
        artifact_path.mkdir(parents=True, exist_ok=True)
        training_args = transformers.TrainingArguments(
            output_dir=str(artifact_path),
            num_train_epochs=self.config.epochs,
            per_device_train_batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
            save_strategy="epoch",
            report_to=[],
        )
        trainer = transformers.Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            tokenizer=tokenizer,
        )
        trainer.train()
        trainer.save_model(str(artifact_path))
        tokenizer.save_pretrained(str(artifact_path))
        self.tokenizer = tokenizer
        self.model = model
        write_json(
            artifact_path / "label_mapping.json",
            {
                "label_to_id": self.label_to_id,
                "id_to_label": {
                    str(identifier): label for identifier, label in self.id_to_label.items()
                },
            },
        )
        write_json(artifact_path / "transformer_config.json", asdict(self.config))
        return self

    def predict(self, code_snippets: list[str]) -> list[str]:
        """Predict labels for code snippets with a loaded transformer model."""
        if not code_snippets:
            return []
        _ensure_transformer_dependencies(training=False)
        if self.tokenizer is None or self.model is None:
            raise ValueError("Transformer model is not loaded. Use TransformerCodeClassifier.load().")
        if not self.id_to_label:
            raise ValueError("Transformer label mapping is not loaded.")

        torch = _import_module("torch")
        inputs = self.tokenizer(
            code_snippets,
            truncation=True,
            padding=True,
            max_length=self.config.max_length,
            return_tensors="pt",
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
        predicted_ids = outputs.logits.argmax(dim=-1).tolist()
        return [self.id_to_label[int(identifier)] for identifier in predicted_ids]


def missing_transformer_dependencies(*, training: bool = True) -> list[str]:
    """Return optional transformer packages that are not importable."""
    dependencies = TRANSFORMER_TRAINING_DEPENDENCIES if training else TRANSFORMER_RUNTIME_DEPENDENCIES
    return [dependency for dependency in dependencies if find_spec(dependency) is None]


def build_label_mapping(labels: list[str]) -> dict[str, int]:
    """Build a stable label-to-id mapping from training labels."""
    label_set = set(labels)
    ordered_labels = [label for label in SUPPORTED_LABELS if label in label_set]
    ordered_labels.extend(sorted(label_set - set(ordered_labels)))
    return {label: index for index, label in enumerate(ordered_labels)}


def _coerce_label_to_id(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ValueError("label_mapping.json must contain a label_to_id object.")
    return {str(label): int(identifier) for label, identifier in value.items()}


def _coerce_id_to_label(value: Any) -> dict[int, str]:
    if not isinstance(value, dict):
        raise ValueError("label_mapping.json must contain an id_to_label object.")
    return {int(identifier): str(label) for identifier, label in value.items()}


class _TokenizedCodeDataset:
    """Torch dataset backed by tokenized code snippets."""

    def __init__(
        self,
        *,
        tokenizer: Any,
        code_snippets: list[str],
        labels: list[int],
        max_length: int,
        torch_module: Any,
    ) -> None:
        self.encodings = tokenizer(
            code_snippets,
            truncation=True,
            padding=True,
            max_length=max_length,
        )
        self.labels = labels
        self.torch = torch_module

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> dict[str, Any]:
        item = {key: self.torch.tensor(values[index]) for key, values in self.encodings.items()}
        item["labels"] = self.torch.tensor(self.labels[index])
        return item


def _import_module(module_name: str) -> Any:
    module = __import__(module_name)
    return module


def _ensure_transformer_dependencies(*, training: bool = True) -> None:
    missing = missing_transformer_dependencies(training=training)
    if missing:
        raise ImportError(f"{TRANSFORMER_INSTALL_HINT} Missing packages: {', '.join(missing)}.")
