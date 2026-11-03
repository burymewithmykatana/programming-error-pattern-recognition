"""Convert a conservative subset of MBPP assertions into unapproved drafts.

Parsing and literal extraction are static; reference and assertion text are
never executed. Unsupported tests are retained as source text for teacher review.
"""
from __future__ import annotations

import ast
import math
import warnings
from typing import Any

SOURCE_URL = "https://github.com/google-research/google-research/blob/83f1e7b59e762648c953de751d31f75720683622/mbpp/sanitized-mbpp.json"


def _json_literal(node: ast.AST) -> Any:
    value = ast.literal_eval(node)

    def valid(item: Any, depth: int = 0) -> bool:
        if depth > 20:
            return False
        if item is None or isinstance(item, (bool, int, str)):
            return True
        if isinstance(item, float):
            return math.isfinite(item)
        if isinstance(item, list):
            return all(valid(child, depth + 1) for child in item)
        if isinstance(item, dict):
            return all(isinstance(key, str) and valid(child, depth + 1) for key, child in item.items())
        return False

    if not valid(value):
        raise ValueError("Only JSON-compatible literals are supported.")
    return value


def _parse_test(text: str, functions: set[str]) -> tuple[str, list[Any], dict[str, Any], Any]:
    if len(text) > 10000:
        raise ValueError("Assertion is too long for automatic conversion.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        parsed = ast.parse(text, mode="exec")
    if len(parsed.body) != 1 or not isinstance(parsed.body[0], ast.Assert) or parsed.body[0].msg is not None:
        raise ValueError("Expected a single assert without a message.")
    expr = parsed.body[0].test
    if not isinstance(expr, ast.Compare) or len(expr.ops) != 1 or not isinstance(expr.ops[0], ast.Eq):
        raise ValueError("Expected a single equality assertion.")
    left, right = expr.left, expr.comparators[0]
    if isinstance(left, ast.Call) and isinstance(left.func, ast.Name) and left.func.id in functions:
        call, expected_node = left, right
    elif isinstance(right, ast.Call) and isinstance(right.func, ast.Name) and right.func.id in functions:
        call, expected_node = right, left
    else:
        raise ValueError("Expected a direct call to a reference function.")
    if any(isinstance(arg, ast.Starred) for arg in call.args) or any(kw.arg is None for kw in call.keywords):
        raise ValueError("Starred arguments are not supported.")
    kwargs = {kw.arg: _json_literal(kw.value) for kw in call.keywords}
    if len(kwargs) != len(call.keywords):
        raise ValueError("Duplicate keyword arguments are not supported.")
    return call.func.id, [_json_literal(arg) for arg in call.args], kwargs, _json_literal(expected_node)


def mbpp_to_draft(row: dict[str, Any]) -> dict[str, Any]:
    """Create an unapproved draft; retain every original assertion unchanged."""
    if not isinstance(row, dict) or not isinstance(row.get("task_id"), int) or isinstance(row["task_id"], bool):
        raise ValueError("MBPP task_id must be an integer.")
    if not all(isinstance(row.get(key), str) and row[key].strip() for key in ("prompt", "code")):
        raise ValueError("MBPP prompt and code must be nonempty strings.")
    if not isinstance(row.get("test_list"), list) or not all(isinstance(item, str) for item in row["test_list"]):
        raise ValueError("MBPP test_list must contain strings.")
    if not isinstance(row.get("test_imports"), list) or not all(isinstance(item, str) for item in row["test_imports"]):
        raise ValueError("MBPP test_imports must contain strings.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            module = ast.parse(row["code"])
        functions = {item.name for item in module.body if isinstance(item, ast.FunctionDef)}
    except (SyntaxError, ValueError):
        functions = set()
    converted, unsupported = [], []
    for index, text in enumerate(row["test_list"], 1):
        try:
            name, args, kwargs, expected = _parse_test(text, functions)
            converted.append({"test_id": f"mbpp-{row['task_id']}-{index}", "function_name": name,
                              "input": args, "keyword_input": kwargs, "expected": expected,
                              "comparison": "python_equality", "points": 1, "source_assertion_index": index})
        except (ValueError, SyntaxError, TypeError, RecursionError, MemoryError) as exc:
            unsupported.append({"source_assertion_index": index, "reason": str(exc) or type(exc).__name__})
    names = {item["function_name"] for item in converted}
    function_name = next(iter(names)) if len(names) == 1 else None
    notices = []
    if len(names) != 1:
        notices.append("Entry point is ambiguous or could not be determined; teacher review is required.")
    if unsupported:
        notices.append("Some original assertions could not be converted and remain as source text.")
    if row["test_imports"]:
        notices.append("The original tests include imports; they have not been interpreted or executed.")
    return {
        "exercise_id": f"mbpp-{row['task_id']}", "function_name": function_name,
        "prompt": row["prompt"], "reference_solution": row["code"], "tests": converted,
        "review_required": True, "approved_for_grading": False,
        "draft_notice": "Unverified draft; points default to 1 per converted test. Do not use for grading until reviewed.",
        "source": {"dataset": "MBPP sanitized", "task_id": row["task_id"], "url": SOURCE_URL,
                   "attribution": "Austin et al., Google Research (2021); dataset card states CC BY 4.0.",
                   "test_imports": row["test_imports"], "original_assertions": row["test_list"]},
        "conversion": {"original_count": len(row["test_list"]), "converted_count": len(converted),
                       "unsupported": unsupported, "warnings": notices},
    }
