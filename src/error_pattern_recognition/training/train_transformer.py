"""Future transformer training workflow."""

from pathlib import Path
from typing import Any


def train_transformer(_data_path: str | Path, _config: dict[str, Any], _output_path: str | Path) -> None:
    """Reserve the transformer training entrypoint without making it mandatory."""
    raise NotImplementedError("Transformer training requires future Hugging Face integration.")

