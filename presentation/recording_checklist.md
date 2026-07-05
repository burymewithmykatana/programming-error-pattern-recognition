# Recording Checklist

## Before recording

- Use a 1920×1080 display and disable notifications.
- Open `presentation/project_presentation.pptx`.
- Start the dashboard with `streamlit run app.py`.
- Confirm both SVM models appear in the sidebar.
- Keep `presentation/persian_narration.md` on a second screen or printed.
- Close unrelated browser tabs and terminals.
- Record a 20-second audio test.

## Reliable demo sequence

1. Select **Synthetic 8-class SVM** and run **Synthetic — correct solution**.
2. Run **Synthetic — syntax error**.
3. Run **Synthetic — variable misuse** and explain that this label comes from the synthetic taxonomy.
4. Select **CodeContests binary SVM** and run the two **CodeContests — ...** examples.
5. Upload a small CSV with a `code` column and download predictions.
6. Show the interpretation-boundary message at the bottom.

## Final verification

- Do not claim that 0.70 real-data accuracy means good syntax-error detection.
- State the real test distribution: 2,000 correct and 59 syntax-error samples.
- State that CodeBERT values are reported only after Colab execution.
- Keep the recording between 12 and 14 minutes.
- Verify that code and student identifiers are not visible.
