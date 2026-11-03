"""Teacher-facing scoring based on externally supplied test evidence."""

from error_pattern_recognition.grading.scoring import score_test_results
from error_pattern_recognition.grading.review import build_review, finalize_review

__all__ = ["score_test_results", "build_review", "finalize_review"]
