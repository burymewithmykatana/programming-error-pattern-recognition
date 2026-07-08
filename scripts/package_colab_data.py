"""Copy prepared CSV splits into the Google Drive/Colab data layout.

The script intentionally copies only CSV inputs needed by the Colab notebook.
Large Hugging Face caches, trained models, and prediction exports remain outside
Git and should stay on external storage.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REQUIRED_SPLITS = {
    "synthetic": ("train.csv", "test.csv"),
    "code_contests": ("train.csv", "valid.csv", "test.csv"),
}


def package_colab_data(source_root: Path, destination_root: Path) -> list[Path]:
    """Copy prepared split CSV files to the expected Colab data directory."""
    copied: list[Path] = []
    for dataset_name, split_files in REQUIRED_SPLITS.items():
        source_dir = source_root / dataset_name
        destination_dir = destination_root / dataset_name
        destination_dir.mkdir(parents=True, exist_ok=True)
        for split_file in split_files:
            source_file = source_dir / split_file
            if not source_file.exists():
                raise FileNotFoundError(f"Missing prepared split: {source_file}")
            destination_file = destination_dir / split_file
            shutil.copy2(source_file, destination_file)
            copied.append(destination_file)
    return copied


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package prepared CSV splits for the CodeBERT Colab notebook."
    )
    parser.add_argument(
        "--source-root",
        default="data/processed",
        help="Directory containing synthetic/ and code_contests/ split folders.",
    )
    parser.add_argument(
        "--destination-root",
        default=r"D:\error-pattern-data",
        help="Destination directory to copy Colab-ready CSV splits into.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    copied = package_colab_data(Path(args.source_root), Path(args.destination_root))
    print(f"Copied {len(copied)} files to {Path(args.destination_root).resolve()}")
    for path in copied:
        print(path)


if __name__ == "__main__":
    main()
