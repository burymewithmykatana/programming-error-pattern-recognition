"""File I/O helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    """Write a JSON file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def read_json(path: str | Path) -> dict[str, Any]:
    """Read a JSON file."""
    input_path = Path(path)
    if not input_path.exists():
        raise FileNotFoundError(f"JSON file not found: {input_path}")
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"JSON file must contain an object: {input_path}")
    return data


def write_text(path: str | Path, text: str) -> None:
    """Write a text file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
