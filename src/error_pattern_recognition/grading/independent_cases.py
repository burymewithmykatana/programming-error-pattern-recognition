"""Manually reasoned supplemental cases for research; no teacher approval."""
import hashlib
import json


def independent_cases(source: dict) -> list[dict]:
    if source.get("task_id") != 602:
        return []
    digest = hashlib.sha256(json.dumps(source, sort_keys=True, ensure_ascii=False,
                                      separators=(",", ":")).encode("utf-8")).hexdigest()
    if digest != "72db1252c920ea75ad08bd1c924cc906e98173f587744a6725144866ccc93c6e":
        raise ValueError("Supplemental cases require review against the changed MBPP-602 source.")
    # Cases have at most one repeated character, avoiding the prompt's ambiguity
    # when multiple characters repeat. Unicode means Python code points here.
    cases = [("empty", "", None), ("singleton", "x", None),
             ("adjacent", "aa", "a"), ("late", "abcc", "c"),
             ("unicode", "\u00e9x\u00e9", "\u00e9"), ("case_sensitive", "aA", None)]
    return [{"test_id": f"mbpp-602-independent-{name}", "function_name": "first_repeated_char",
             "input": [value], "keyword_input": {}, "expected": expected,
             "comparison": "python_equality", "points": 1,
             "origin": "manually_reasoned_research_case_v1"} for name, value, expected in cases]
