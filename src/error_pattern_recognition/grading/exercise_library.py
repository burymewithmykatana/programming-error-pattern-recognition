"""Read and search a local MBPP exercise library without executing code."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_mbpp(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("MBPP library must contain a list of exercises.")
    result = []
    seen = set()
    for row in data:
        if not isinstance(row, dict) or not isinstance(row.get("task_id"), int) or isinstance(row["task_id"], bool):
            raise ValueError("Each MBPP exercise must have an integer task_id.")
        if row["task_id"] in seen:
            raise ValueError("MBPP task IDs must be unique.")
        if not all(isinstance(row.get(key), str) and row[key].strip() for key in ("prompt", "code")):
            raise ValueError("Each MBPP exercise must have prompt and reference code text.")
        for key in ("test_list", "test_imports"):
            if not isinstance(row.get(key), list) or not all(isinstance(item, str) for item in row[key]):
                raise ValueError(f"MBPP {key} must be a list of strings.")
        seen.add(row["task_id"])
        result.append(row)
    return result


def search_mbpp(rows: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    """Case-insensitive keyword search in task IDs and prompts."""
    terms = query.casefold().split()
    return [row for row in rows if all(term in f"{row['task_id']} {row['prompt']}".casefold() for term in terms)]
