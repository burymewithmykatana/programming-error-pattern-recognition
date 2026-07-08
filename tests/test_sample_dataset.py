from pathlib import Path

from scripts.sample_dataset import sample_dataset


def test_sample_dataset_limits_each_label(tmp_path: Path) -> None:
    input_path = tmp_path / "dataset.csv"
    input_path.write_text(
        "code,label\n"
        "\"print(1)\",correct_solution\n"
        "\"print(2)\",correct_solution\n"
        "\"print(3)\",correct_solution\n"
        "\"for i in range(10 print(i)\",syntax_error\n"
        "\"def bad(x)\\n    return x\",syntax_error\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "sampled.csv"

    sampled = sample_dataset(
        input_path=input_path,
        output_path=output_path,
        max_per_label=2,
        seed=7,
    )

    assert output_path.exists()
    assert len(sampled) == 4
    assert sampled["label"].value_counts().to_dict() == {
        "correct_solution": 2,
        "syntax_error": 2,
    }
