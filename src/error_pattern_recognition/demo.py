"""Presentation-safe model registry and label explanations."""

from __future__ import annotations

from pathlib import Path

MODEL_REGISTRY = {
    "Synthetic 8-class SVM": Path("reports/experiments/synthetic_svm/model.joblib"),
    "CodeContests binary SVM": Path("reports/experiments/codecontests_svm/model.joblib"),
    "Synthetic 8-class CodeBERT": Path("reports/experiments/synthetic_codebert/model"),
    "CodeContests binary CodeBERT": Path("reports/experiments/codecontests_codebert/model"),
}

LABEL_EXPLANATIONS = {
    "correct_solution": "The submission resembles code accepted as a correct solution.",
    "syntax_error": "The submission contains malformed Python syntax.",
    "variable_misuse": "A variable appears undefined, confused, or inconsistently used.",
    "loop_logic_error": "Iteration bounds, updates, or termination logic appear incorrect.",
    "conditional_logic_error": "A condition or Boolean branch appears incorrect.",
    "function_definition_error": "The function signature, call, or return behavior appears incorrect.",
    "data_structure_misuse": "A collection, index, or mutation operation appears inappropriate.",
    "algorithmic_inefficiency": "The code uses an unnecessarily expensive algorithmic pattern.",
}

DEMO_EXAMPLES = {
    "Synthetic — correct solution": (
        "def solve_47(numbers):\n    return [number * 2 for number in numbers]"
    ),
    "Synthetic — syntax error": "if 5 > 3:\nprint('large')",
    "Synthetic — variable misuse": (
        "def solve_4(x, y):\n    result = x + y\n    return total"
    ),
    "Synthetic — loop logic error": (
        "def solve_36(n):\n"
        "    count = 0\n"
        "    while count < n:\n"
        "        print(count)\n"
        "    return count"
    ),
    "CodeContests — correct solution": (
        "for s in[*open(0)][2::2]:f=s.split().count;print(f('1')<<f('0'))"
    ),
    "CodeContests — Python 2 syntax error": (
        "from sys import stdin\n"
        "def solve():\n"
        "    s, n, k = map(int, raw_input().split())\n"
        "    if k == s:\n"
        "        return 1\n"
        "    if k > s or n == 1:\n"
        "        return 0\n"
        "    p = n / k\n"
        "    if s >= n + (k - 1) * p:\n"
        "        return 0\n"
        "    return 1\n\n"
        "T = int(stdin.readline())\n"
        "for _ in xrange(T):\n"
        '    print "YES" if solve() else "NO"\n'
    ),
}


def available_models(root: str | Path = ".") -> dict[str, Path]:
    """Return only model artifacts that currently exist."""
    root_path = Path(root)
    return {
        name: root_path / relative_path
        for name, relative_path in MODEL_REGISTRY.items()
        if (root_path / relative_path).exists()
    }
