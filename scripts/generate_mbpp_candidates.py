"""Create static, unscored MBPP solution variants without executing source code."""
from __future__ import annotations

import argparse
import ast
import copy
import json
import sys
import warnings
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from error_pattern_recognition.grading.exercise_library import load_mbpp
from error_pattern_recognition.grading.mbpp_drafts import mbpp_to_draft, SOURCE_URL

REPLACEMENTS = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Add,
                ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.LtE,
                ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt}


def mbpp_split(task_id: int) -> str:
    """Use the original MBPP task-ID partition, keeping prompt examples separate."""
    if 1 <= task_id <= 10:
        return "prompt"
    if 11 <= task_id <= 510:
        return "test"
    if 511 <= task_id <= 600:
        return "validation"
    if 601 <= task_id <= 974:
        return "train"
    raise ValueError(f"Unexpected MBPP task_id: {task_id}")


def _sites(function: ast.FunctionDef) -> list[tuple[ast.AST, str, int | None]]:
    sites = []
    for node in ast.walk(function):
        if isinstance(node, (ast.BinOp, ast.AugAssign)) and type(node.op) in REPLACEMENTS:
            sites.append((node, "op", None))
        elif isinstance(node, ast.Compare):
            for index, operator in enumerate(node.ops):
                if type(operator) in REPLACEMENTS:
                    sites.append((node, "ops", index))
    return sites


def make_candidates(row: dict[str, Any], *, max_mutants: int = 2) -> list[dict[str, Any]]:
    """Return normalized reference and operator mutations, without behavior labels."""
    if max_mutants < 1:
        raise ValueError("max_mutants must be positive")
    draft = mbpp_to_draft(row)
    entry = draft["function_name"]
    if entry is None:
        return []
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            original = ast.parse(row["code"])
        function = next((node for node in original.body if isinstance(node, ast.FunctionDef) and node.name == entry), None)
        if function is None:
            return []
        normalized = ast.unparse(original) + "\n"
        compile(normalized, "<mbpp-reference>", "exec")  # Syntax check only; never execute.
    except (SyntaxError, ValueError, RecursionError):
        return []
    sites = _sites(function)
    if not sites:
        return []
    common = {"exercise_id": draft["exercise_id"], "task_id": row["task_id"], "split": mbpp_split(row["task_id"]),
              "prompt": row["prompt"], "function_name": entry, "reference_solution": row["code"],
              "source_assertions": row["test_list"], "source_test_imports": row["test_imports"],
              "source_url": SOURCE_URL, "attribution": "Austin et al., Google Research (2021); dataset card states CC BY 4.0.",
              "label_status": "unscored; requires isolated test execution and teacher review"}
    result = [{**common, "candidate_id": f"mbpp-{row['task_id']}-reference", "candidate_kind": "reference_copy",
               "student_code": normalized, "mutation": None}]
    for index in range(min(max_mutants, len(sites))):
        mutated = copy.deepcopy(original)
        function_copy = next(node for node in mutated.body if isinstance(node, ast.FunctionDef) and node.name == entry)
        node, attr, slot = _sites(function_copy)[index]
        before = node.op if attr == "op" else node.ops[slot]
        after = REPLACEMENTS[type(before)]()
        if attr == "op":
            node.op = after
        else:
            node.ops[slot] = after
        ast.fix_missing_locations(mutated)
        try:
            source = ast.unparse(mutated) + "\n"
            compile(source, "<mbpp-mutant>", "exec")  # Syntax check only; never execute.
        except (SyntaxError, ValueError, RecursionError):
            continue
        if source != normalized:
            result.append({**common, "candidate_id": f"mbpp-{row['task_id']}-mutant-{index + 1}",
                           "candidate_kind": "single_operator_mutation", "student_code": source,
                           "mutation": {"site_index": index, "from": type(before).__name__, "to": type(after).__name__}})
    return result if len(result) > 1 else []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/exercise_library/mbpp-sanitized.json"))
    parser.add_argument("--output", type=Path, default=Path("data/synthetic_grading/mbpp_candidates.jsonl"))
    parser.add_argument("--max-mutants", type=int, default=2)
    args = parser.parse_args()
    candidates = [candidate for row in load_mbpp(args.input) for candidate in make_candidates(row, max_mutants=args.max_mutants)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in candidates), encoding="utf-8")
    print(f"Wrote {len(candidates)} unscored candidates from {len({c['exercise_id'] for c in candidates})} MBPP exercises to {args.output}")


if __name__ == "__main__":
    main()
