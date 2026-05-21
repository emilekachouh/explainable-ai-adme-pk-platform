# Technical Report

## Abstract-Style Summary

AI-PBPK / ADME Predictor is an explainable computational ADME screening prototype using real public Caco-2 permeability data. The platform combines RDKit descriptors, Morgan fingerprints, baseline machine learning, scaffold-split validation, SHAP interpretation, uncertainty scoring, applicability-domain analysis, and an educational PK/NCA simulator. The system is designed for early discovery support and education, not clinical or regulatory prediction.

## Dataset

The primary dataset is the TDC Caco2_Wang public benchmark, mirrored by scikit-fingerprints on Hugging Face. The endpoint is experimental Caco-2 log(Papp). After preprocessing, 906 valid canonicalized molecules remained.

## Preprocessing

Rows were validated for required SMILES and endpoint fields. SMILES were canonicalized with RDKit. Invalid molecules were removed. Duplicate canonical SMILES were aggregated by averaging endpoint values. A median-threshold binary permeability class was created for classification.

## Descriptor Generation

Features include molecular weight, logP, TPSA, HBD, HBA, rotatable bonds, ring counts, formal charge, fraction CSP3, heavy atom count, heteroatom count, molar refractivity, Lipinski/ADME flags, and Morgan fingerprints.

## Model Training

Baseline classification models included logistic regression, random forest, and XGBoost. Regression models included linear regression, random forest regressor, and XGBoost regressor.

## Random Split Validation

The best random-split classifier was XGBoost with AUROC 0.946 and F1 0.863. The best random-split regressor was random forest regressor with R2 0.785 and MAE 0.297.

## Scaffold Split Validation

Bemis-Murcko scaffold splitting was used to reduce chemical leakage. The split included 450 total unique scaffolds with zero overlap between train and test. The best scaffold-split classifier was XGBoost with AUROC 0.934 and F1 0.841. The best scaffold-split regressor was XGBoost regressor with R2 0.650 and MAE 0.392.

## SHAP Interpretation

SHAP plots were generated for XGBoost classifier and regressor models. Interpretable drivers include TPSA, HBD/HBA, molecular weight, logP, flexibility, and fingerprint-defined substructures. Fingerprint contributions should be interpreted as structural pattern signals rather than direct causal mechanisms.

## Uncertainty Estimation

Prediction confidence is calculated from probability margin and entropy. The confidence score is `max(p, 1-p)`, with High, Medium, and Low confidence categories. This is model-derived uncertainty, not calibrated clinical certainty.

## Applicability Domain

Applicability domain is assessed by nearest-neighbor Morgan fingerprint Tanimoto similarity to training molecules. Chemically distant molecules receive a reliability warning.

## PK/NCA Simulator

The educational PK/NCA simulator supports IV bolus, oral first-order absorption, and IV infusion one-compartment profiles. It calculates AUC, AUMC, MRT/MBRT, terminal lambda_z, half-life, extrapolated AUC, Cmax, Tmax, CL, CL/F, Vz, and Vss when scientifically appropriate.

## Limitations

Caco-2 permeability is an in vitro proxy. Oral absorption and human PK depend on many additional factors. Scaffold validation improves rigor but is not prospective external validation. The PK/NCA module uses assumed parameters and is educational only.

## Future Work

Future work should add external public datasets, additional ADME endpoints, calibration, conformal prediction, scaffold validation across tasks, and prospective-style benchmark evaluation.
