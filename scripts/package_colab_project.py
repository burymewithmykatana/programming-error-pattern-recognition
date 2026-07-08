"""Create a lightweight project archive for running the Colab notebook.

Use this when the working branch has not been pushed to GitHub yet. The archive
contains source code, configs, scripts, tests, docs, and notebooks, but excludes
large local datasets, caches, trained model artifacts, and VCS files.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".mypy_cache",
    ".ruff_cache",
}

EXCLUDED_ROOT_DIRS = {
    "data/processed",
    "reports/experiments",
    "models",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".joblib",
    ".pt",
    ".bin",
    ".safetensors",
}


def should_include(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    parts = relative.parts
    if any(part in EXCLUDED_DIRS for part in parts):
        return False
    relative_posix = relative.as_posix()
    if any(
        relative_posix == excluded or relative_posix.startswith(f"{excluded}/")
        for excluded in EXCLUDED_ROOT_DIRS
    ):
        return False
    if path.name.startswith("~$"):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return True


def package_project(root: Path, output: Path) -> int:
    """Write a zip archive of the project and return the number of files added."""
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.resolve() == output.resolve():
                continue
            if not should_include(path, root):
                continue
            archive.write(path, path.relative_to(root).as_posix())
            count += 1
    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package the current project tree for Colab execution."
    )
    parser.add_argument("--root", default=".", help="Project root to package.")
    parser.add_argument(
        "--output",
        default=r"D:\error-pattern-project.zip",
        help="Destination zip file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output)
    count = package_project(root, output)
    print(f"Archived {count} files to {output.resolve()}")


if __name__ == "__main__":
    main()
