# Ten-Minute Presentation Review

## Slide 1 - Title

This project is about programming error pattern recognition. The goal is to take Python code submissions and identify recurring error patterns that can help instructors review student work more efficiently. The project combines a practical pattern-recognition pipeline, measured experiments, and a comparison with a successful research model.

## Slide 2 - Project Goal and PR Framing

The input is a source-code submission and the output is a predicted label, such as correct solution, syntax error, or another programming mistake category. From a pattern recognition perspective, the project has the full workflow: represent raw code, extract features or contextual embeddings, train classifiers, evaluate predictions, and interpret results.

## Slide 3 - Research Questions

The main question is whether source-code representations can recognize recurring programming errors. A second question is whether results from generated labels transfer to real submissions. The final question asks what a successful model needs beyond this project, especially when full training on the desired dataset is limited by resources.

## Slide 4 - System Built

The project is not only a notebook. It includes a reusable Python package for loading data, preprocessing code, training models, evaluating results, and running inference. It also includes command-line scripts, saved experiment artifacts, tests, and a Streamlit dashboard where an instructor can paste code or upload a CSV file.

## Slide 5 - Datasets and Labels

There are two datasets and two different claims. The synthetic dataset has 976 unique balanced Python examples across eight labels. It supports the prototype taxonomy. The CodeContests dataset contains real submissions, but it does not provide detailed semantic error labels. Therefore, accepted solutions are labeled correct, and only incorrect submissions that fail Python AST parsing are labeled syntax errors.

## Slide 6 - Data Integrity Controls

To avoid inflated results, the pipeline normalizes and hashes each code sample. Duplicates are removed, and the run rejects train-test overlap. The synthetic data uses a deterministic stratified split. CodeContests uses official problem splits, which is important because mixing solutions from the same problem across train and test could make the result too optimistic.

## Slide 7 - Model Approaches

The baseline is TF-IDF plus Linear SVM. It is fast, reproducible, and strong for lexical code patterns. The deep model is CodeBERT with a sequence-classification head. CodeBERT can represent more context than TF-IDF, but the full CodeContests training target was resource-heavy, so the project reports a reduced real-data CodeBERT run.

## Slide 8 - Measured Model Results

On the synthetic eight-class task, the SVM performed best, with Macro F1 around 0.903. CodeBERT was weaker on the small synthetic set, with Macro F1 around 0.439. On CodeContests, the SVM reached accuracy around 0.705 but Macro F1 only 0.440. Reduced CodeBERT reached accuracy around 0.661 and Macro F1 around 0.458.

## Slide 9 - Real-Data Interpretation

The real test set is severely imbalanced: 2,000 correct submissions and only 59 syntax errors. This means accuracy is misleading. The SVM found 18 of 59 syntax errors. CodeBERT found 51 of 59 syntax errors, so its recall was much better. However, CodeBERT also incorrectly flagged 691 correct submissions as syntax errors, so its syntax-error precision was still low.

## Slide 10 - Confusion Matrices

The confusion matrices show the main lesson visually. The synthetic SVM result is strong because many generated categories have recognizable templates. In the real dataset, both models struggle with the minority syntax-error class. CodeBERT shifts toward high recall, while the SVM is more conservative but misses more syntax errors.

## Slide 11 - Successful External Study: BIFI

Because full training on the desired dataset could not be completed, the project includes BIFI as a successful related model. BIFI stands for Break-It-Fix-It. It is a program-repair model, not just a classifier. It uses a parser or compiler-style critic to verify whether generated code is valid. It reports 90.5% repair accuracy on GitHub-Python AST parse errors and 71.7% on DeepFix C.

## Slide 12 - Our System Compared With BIFI

The comparison explains what a stronger future model requires. This project classifies errors using labels and AST-based filtering. BIFI repairs code using a critic and iterative synthetic-real adaptation. Its advantage is that it learns from large unlabeled corpora and verified feedback. Its cost is more data, more compute, and a more complex training loop. Also, parser feedback mainly helps syntax errors, not semantic bugs.

## Slide 13 - Project Achievements

The project achieved a complete pattern-recognition system: package, scripts, tests, experiments, report, presentation, and dashboard. It achieved strong synthetic performance and honest real-data validation. It also showed that CodeBERT improves syntax-error recall, but the low precision means the model should support review rather than make final decisions.

## Slide 14 - Limitations

The most important limitation is that synthetic labels do not prove classroom generalization. CodeContests is real but not a classroom dataset, and it lacks semantic error labels. The current formulation is single-label, but real submissions can contain multiple errors. A stronger system needs expert annotation, unit tests, or another behavioral signal.

## Slide 15 - Conclusion

The project demonstrates a complete PR workflow for programming error pattern recognition. The synthetic task proves the pipeline can learn the proposed taxonomy. The real task shows the boundary of the current claims. The BIFI study points to the next step: combine source-code models with parser, compiler, or unit-test feedback so the model learns from verified behavior, not only static labels.

## Slide 16 - References

The key reference is BIFI by Yasunaga and Liang, published at ICML 2021. DrRepair is another related model that uses diagnostic feedback. The project also uses DeepMind CodeContests and Microsoft CodeBERT as the main external dataset and transformer representation.
