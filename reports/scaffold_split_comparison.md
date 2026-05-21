# Scaffold Split Validation Comparison

This report compares the original random split baseline with a Bemis-Murcko scaffold split. Scaffold splitting is stricter because compounds sharing the same core scaffold are kept entirely in train or test, reducing the chance that the model benefits from close structural analogs across the split.

## Split Summary

- Train rows: 723
- Test rows: 183
- Total unique scaffolds: 450
- Train unique scaffolds: 441
- Test unique scaffolds: 9
- Overlapping scaffolds: 0
- Train class counts: {0: 357, 1: 366}
- Test class counts: {0: 96, 1: 87}

## Metric Comparison

| task | model | metric | random_split | scaffold_split | performance_drop |
| --- | --- | --- | --- | --- | --- |
| classification | logistic_regression | balanced_accuracy | 0.791 | 0.736 | 0.056 |
| classification | logistic_regression | f1 | 0.798 | 0.741 | 0.057 |
| classification | logistic_regression | auroc | 0.852 | 0.796 | 0.056 |
| classification | random_forest | balanced_accuracy | 0.841 | 0.834 | 0.006 |
| classification | random_forest | f1 | 0.843 | 0.836 | 0.007 |
| classification | random_forest | auroc | 0.940 | 0.920 | 0.021 |
| classification | xgboost | balanced_accuracy | 0.863 | 0.847 | 0.015 |
| classification | xgboost | f1 | 0.863 | 0.841 | 0.022 |
| classification | xgboost | auroc | 0.946 | 0.934 | 0.012 |
| regression | linear_regression | mae | 0.590 | 1.546 | -0.956 |
| regression | linear_regression | r2 | 0.056 | -5.563 | 5.619 |
| regression | random_forest_regressor | mae | 0.297 | 0.411 | -0.113 |
| regression | random_forest_regressor | r2 | 0.785 | 0.614 | 0.170 |
| regression | xgboost_regressor | mae | 0.314 | 0.392 | -0.078 |
| regression | xgboost_regressor | r2 | 0.765 | 0.650 | 0.116 |

## Scientific Interpretation

Scaffold split validation is harder than random splitting in drug-discovery ML because the test set is chemically less redundant with the training set. A model that performs well only on a random split may be learning scaffold similarity rather than portable ADME relationships.

The best scaffold-split classifier was `xgboost` with AUROC 0.934, balanced accuracy 0.847, and F1 0.841. This should be interpreted as a stricter estimate of prospective screening behavior than the random split.

The best scaffold-split regressor was `xgboost_regressor` with MAE 0.392 and R2 0.650. Regression performance is especially sensitive to whether the test scaffolds occupy endpoint ranges represented in training.

If scaffold performance drops relative to random split performance, that does not mean the model is useless. It means the original random split likely benefited from chemically similar analogs appearing in both train and test. The scaffold result is more credible for early discovery screening because it asks whether descriptors and fingerprints capture transferable permeability patterns.

Important ADME interpretation remains qualitative: TPSA, HBD/HBA, logP, molecular weight, and flexibility are mechanistically relevant to permeability, but this model is not a clinical predictor. It is an explainable AI-assisted ADME screening prototype.

For recruiter or interviewer credibility, showing both random and scaffold validation is valuable because it demonstrates awareness of chemical leakage, dataset bias, and the difference between conventional ML validation and drug-discovery validation.