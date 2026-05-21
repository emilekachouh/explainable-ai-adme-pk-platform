# Explainable AI-Assisted Caco-2 Permeability Screening with Educational PK/NCA Simulation

## Abstract

We developed an explainable AI-assisted ADME screening platform using a real public Caco-2 permeability benchmark. The platform integrates RDKit molecular descriptors, Morgan fingerprints, baseline machine learning, random and scaffold split validation, SHAP interpretation, confidence estimation, applicability-domain analysis, and an educational PK/NCA simulator. The system is intended for early discovery support and computational pharmacology education, not clinical or regulatory prediction.

## Introduction

Permeability is a key consideration in early drug discovery. Caco-2 assays provide an in vitro proxy for epithelial transport, but permeability alone does not determine human exposure. Computational tools can help prioritize compounds, but responsible validation and interpretation are essential to avoid overclaiming model capability.

## Methods

The TDC Caco2_Wang dataset was used as the primary public experimental benchmark. SMILES were validated and canonicalized using RDKit. Duplicate canonical structures were aggregated by mean endpoint value. Molecular descriptors, Lipinski-style flags, and Morgan fingerprints were generated.

Classification models predicted median-threshold permeability class, while regression models predicted continuous log(Papp). Logistic regression, random forest, and XGBoost classifiers were trained. Linear regression, random forest, and XGBoost regressors were trained for continuous prediction.

Models were evaluated using random train/test splitting and Bemis-Murcko scaffold splitting. SHAP analyses were generated for XGBoost models. Confidence was estimated using probability margin and entropy. Applicability domain was estimated using nearest-neighbor Morgan fingerprint Tanimoto similarity.

An educational PK/NCA module was implemented using one-compartment IV bolus, oral first-order absorption, and IV infusion equations. NCA calculations included AUC, AUMC, MRT/MBRT, terminal lambda_z, half-life, extrapolated AUC, clearance labels, Vz, and Vss where appropriate.

## Results

The processed dataset contained 906 valid molecules. The best random-split classifier was XGBoost with AUROC 0.946 and F1 0.863. The best scaffold-split classifier was XGBoost with AUROC 0.934 and F1 0.841. Regression performance decreased under scaffold validation, consistent with the increased difficulty of predicting chemically distinct test scaffolds.

SHAP interpretation highlighted chemically plausible contributions from polarity, hydrogen bonding, molecular size, lipophilicity, flexibility, and substructure fingerprints.

## Discussion

The comparison between random and scaffold validation is central to scientific credibility. Random split performance may benefit from structural similarity between train and test molecules. Scaffold split validation provides a stricter assessment of whether the model captures transferable ADME patterns. The observed performance drop is scientifically informative rather than a failure.

## Limitations

Caco-2 data are in vitro measurements and do not validate human absorption or systemic exposure. The binary permeability class is a dataset-derived threshold. Confidence and applicability-domain estimates are computational indicators, not clinical certainty. The PK/NCA module demonstrates equations under assumed parameters and does not validate human PK.

## Conclusion

This project demonstrates a scientifically cautious, explainable ADME screening prototype suitable for early discovery education and portfolio presentation. The platform combines machine learning, interpretability, validation rigor, and pharmacokinetic teaching tools while avoiding clinical overclaiming.

## References

- Therapeutics Data Commons Caco2_Wang benchmark
- RDKit
- scikit-learn
- XGBoost
- SHAP
- Standard pharmacokinetics and noncompartmental analysis references
