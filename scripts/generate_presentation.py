"""Generate the editable project PowerPoint from measured experiment outputs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "presentation" / "project_presentation.pptx"
FIGURES = ROOT / "reports" / "figures"
NAVY = RGBColor(12, 23, 42)
CYAN = RGBColor(34, 211, 238)
WHITE = RGBColor(241, 245, 249)
MUTED = RGBColor(148, 163, 184)


def read_metrics(name: str) -> dict[str, float]:
    path = ROOT / "reports" / "experiments" / name / "metrics.json"
    return json.loads(path.read_text(encoding="utf-8"))


def create_figures() -> tuple[Path, Path, Path]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    synthetic = read_metrics("synthetic_svm")
    real = read_metrics("codecontests_svm")

    metrics_path = FIGURES / "svm_metrics.png"
    labels = ["Accuracy", "Macro F1", "Weighted F1"]
    x = range(len(labels))
    plt.figure(figsize=(8, 4.5))
    plt.bar([i - 0.18 for i in x], [synthetic["accuracy"], synthetic["macro_f1"], synthetic["weighted_f1"]], width=0.36, label="Synthetic 8-class")
    plt.bar([i + 0.18 for i in x], [real["accuracy"], real["macro_f1"], real["weighted_f1"]], width=0.36, label="CodeContests binary")
    plt.xticks(list(x), labels)
    plt.ylim(0, 1)
    plt.ylabel("Score")
    plt.legend()
    plt.tight_layout()
    plt.savefig(metrics_path, dpi=180, transparent=False)
    plt.close()

    confusion_paths = []
    for name, title in (
        ("synthetic_svm", "Synthetic 8-class confusion matrix"),
        ("codecontests_svm", "CodeContests binary confusion matrix"),
    ):
        matrix = pd.read_csv(
            ROOT / "reports" / "experiments" / name / "confusion_matrix.csv",
            index_col=0,
        )
        path = FIGURES / f"{name}_confusion.png"
        plt.figure(figsize=(7, 5.5))
        plt.imshow(matrix.values, cmap="Blues")
        plt.colorbar()
        plt.xticks(range(len(matrix.columns)), matrix.columns, rotation=55, ha="right", fontsize=7)
        plt.yticks(range(len(matrix.index)), matrix.index, fontsize=7)
        plt.title(title)
        for row in range(len(matrix.index)):
            for column in range(len(matrix.columns)):
                plt.text(column, row, str(matrix.iat[row, column]), ha="center", va="center", fontsize=7)
        plt.tight_layout()
        plt.savefig(path, dpi=180)
        plt.close()
        confusion_paths.append(path)
    return metrics_path, confusion_paths[0], confusion_paths[1]


def set_background(slide) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = NAVY


def add_title(slide, title: str, subtitle: str | None = None) -> None:
    box = slide.shapes.add_textbox(Inches(0.7), Inches(0.45), Inches(11.9), Inches(0.8))
    paragraph = box.text_frame.paragraphs[0]
    paragraph.text = title
    paragraph.font.name = "Aptos Display"
    paragraph.font.size = Pt(28)
    paragraph.font.bold = True
    paragraph.font.color.rgb = WHITE
    if subtitle:
        sub = slide.shapes.add_textbox(Inches(0.72), Inches(1.15), Inches(11.5), Inches(0.45))
        p = sub.text_frame.paragraphs[0]
        p.text = subtitle
        p.font.name = "Aptos"
        p.font.size = Pt(13)
        p.font.color.rgb = CYAN


def add_bullets(slide, items: list[str], top: float = 1.65) -> None:
    box = slide.shapes.add_textbox(Inches(0.9), Inches(top), Inches(11.4), Inches(5.1))
    frame = box.text_frame
    frame.clear()
    for index, text in enumerate(items):
        p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        p.text = text
        p.font.name = "Aptos"
        p.font.size = Pt(21)
        p.font.color.rgb = WHITE
        p.space_after = Pt(17)
        p.level = 0


def add_slide(prs: Presentation, title: str, bullets: list[str], subtitle: str | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide)
    add_title(slide, title, subtitle)
    add_bullets(slide, bullets)
    return slide


def build_presentation() -> Path:
    metrics_figure, synthetic_confusion, real_confusion = create_figures()
    synthetic = read_metrics("synthetic_svm")
    real = read_metrics("codecontests_svm")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide)
    title = slide.shapes.add_textbox(Inches(0.9), Inches(2.1), Inches(11.5), Inches(1.5))
    p = title.text_frame.paragraphs[0]
    p.text = "Programming Error Pattern Recognition"
    p.font.name = "Aptos Display"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    s = title.text_frame.add_paragraph()
    s.text = "A dual synthetic and real-data evaluation"
    s.font.size = Pt(20)
    s.font.color.rgb = CYAN
    s.alignment = PP_ALIGN.CENTER

    add_slide(prs, "Why this problem matters", [
        "Programming courses receive many submissions with recurring mistakes.",
        "Automated triage can help instructors prioritize review and feedback.",
        "The model supports human review; it does not replace an instructor.",
    ])
    add_slide(prs, "Research question", [
        "Can source-code representations identify recurring error patterns?",
        "How does a prototype trained on generated labels behave on real submissions?",
        "What claims remain valid when real semantic labels are unavailable?",
    ])
    add_slide(prs, "Eight-label prototype taxonomy", [
        "Correct solution • syntax error • variable misuse • loop logic error",
        "Conditional logic error • function definition error",
        "Data-structure misuse • algorithmic inefficiency",
        "Current formulation assigns one dominant label per submission.",
    ])
    add_slide(prs, "Two datasets, two claims", [
        "Synthetic: 976 unique, balanced examples across eight prototype labels.",
        "CodeContests: real competitive-programming submissions.",
        "Real labels are limited to accepted solution vs AST-confirmed syntax error.",
        "Parseable incorrect code is excluded instead of receiving invented labels.",
    ])
    add_slide(prs, "Leakage-safe processing", [
        "Normalize line endings and outer whitespace; hash each code sample.",
        "Remove within-split duplicates and reject train/test overlap.",
        "Use stratified synthetic split and official CodeContests problem splits.",
        "Persist configuration, predictions, timings, metrics and confusion matrices.",
    ])
    add_slide(prs, "Baseline: TF-IDF + Linear SVM", [
        "Normalize Python code tokens and identifiers.",
        "Extract unigram and bigram TF-IDF features.",
        "Train a fast, reproducible LinearSVC classifier.",
        "Limitation: lexical features do not directly execute or reason about code.",
    ])
    add_slide(prs, "Deep model: CodeBERT", [
        "microsoft/codebert-base with a sequence-classification head.",
        "Maximum length 256; batch size 8; gradient accumulation.",
        "Mixed precision on CUDA, early stopping and fixed random seed.",
        "Executed in Colab; metrics are reported only after a completed run.",
    ])
    add_slide(prs, "Experimental protocol", [
        "Synthetic: 732 training and 244 unseen test examples.",
        "CodeContests: 19,999 training and 2,059 official test examples.",
        "Primary metric: Macro F1; accuracy is secondary under imbalance.",
        "Four planned runs: SVM and CodeBERT on both datasets.",
    ])

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide)
    add_title(slide, "Measured SVM results", "No estimated or placeholder model scores")
    slide.shapes.add_picture(str(metrics_figure), Inches(0.7), Inches(1.55), width=Inches(6.2))
    add_bullets(slide, [
        f"Synthetic: accuracy {synthetic['accuracy']:.3f}; Macro F1 {synthetic['macro_f1']:.3f}.",
        f"CodeContests: accuracy {real['accuracy']:.3f}; Macro F1 {real['macro_f1']:.3f}.",
        "Real test imbalance: 2,000 correct vs 59 syntax-error samples.",
        "Accuracy overstates minority-class performance.",
    ], top=1.75)
    slide.shapes[-1].left = Inches(7.15)
    slide.shapes[-1].width = Inches(5.4)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide)
    add_title(slide, "Confusion matrices and dashboard")
    slide.shapes.add_picture(str(synthetic_confusion), Inches(0.5), Inches(1.35), width=Inches(5.7))
    slide.shapes.add_picture(str(real_confusion), Inches(6.3), Inches(1.35), width=Inches(5.7))
    note = slide.shapes.add_textbox(Inches(0.8), Inches(6.55), Inches(11.8), Inches(0.4))
    p = note.text_frame.paragraphs[0]
    p.text = "Dashboard supports pasted code, prepared examples, CSV upload and model selection."
    p.font.size = Pt(15)
    p.font.color.rgb = CYAN
    p.alignment = PP_ALIGN.CENTER

    add_slide(prs, "Conclusion and next steps", [
        "The end-to-end pipeline is reproducible and leakage-aware.",
        "Strong synthetic performance demonstrates feasibility, not classroom validity.",
        "Real validation exposes severe imbalance and weak syntax-error precision.",
        "Next: finish Colab runs and collect expert-annotated student submissions.",
    ])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build_presentation())
