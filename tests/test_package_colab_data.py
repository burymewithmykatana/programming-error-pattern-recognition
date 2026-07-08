from pathlib import Path

from scripts.package_colab_data import package_colab_data


def test_package_colab_data_copies_required_splits(tmp_path: Path) -> None:
    source = tmp_path / "processed"
    destination = tmp_path / "drive_data"
    for dataset_name, split_names in {
        "synthetic": ("train.csv", "test.csv"),
        "code_contests": ("train.csv", "valid.csv", "test.csv"),
    }.items():
        dataset_dir = source / dataset_name
        dataset_dir.mkdir(parents=True)
        for split_name in split_names:
            (dataset_dir / split_name).write_text("code,label\nprint(1),correct_solution\n")

    copied = package_colab_data(source, destination)

    assert len(copied) == 5
    assert (destination / "synthetic/train.csv").exists()
    assert (destination / "synthetic/test.csv").exists()
    assert (destination / "code_contests/train.csv").exists()
    assert (destination / "code_contests/valid.csv").exists()
    assert (destination / "code_contests/test.csv").exists()
