from pathlib import Path
import zipfile

from scripts.package_colab_project import package_project


def test_package_project_excludes_large_and_temporary_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (root / "src").mkdir()
    (root / "src" / "module.py").write_text("print('ok')\n")
    processed = root / "data" / "processed"
    processed.mkdir(parents=True)
    (processed / "train.csv").write_text("large data\n")
    reports = root / "reports" / "experiments" / "run"
    reports.mkdir(parents=True)
    (reports / "model.joblib").write_text("model\n")
    (root / "presentation").mkdir()
    (root / "presentation" / "~$slides.pptx").write_text("lock\n")

    output = tmp_path / "project.zip"
    count = package_project(root, output)

    assert count == 2
    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())

    assert "pyproject.toml" in names
    assert "src/module.py" in names
    assert "data/processed/train.csv" not in names
    assert "reports/experiments/run/model.joblib" not in names
    assert "presentation/~$slides.pptx" not in names
