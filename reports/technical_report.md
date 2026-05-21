# Technical Report

## Abstract-Style Summary

AI-PBPK / ADME Predictor is an explainable computational ADME screening prototype using real public Caco-2 permeability data. The platform combines RDKit descriptors, Morgan fingerprints, baseline machine learning, scaffold-split validation, SHAP interpretation, uncertainty scoring, applicability-domain analysis, and an educational PK/NCA simulator. The system is designed for early discovery support and education, not clinical or regulatory prediction.

## App Education and Reporting Layer

The Streamlit app includes a visible explanation of what the platform does, a stepwise usage guide, reviewer-focused explanation levels, and downloadable markdown/CSV reports. Reports include the selected molecule, canonical SMILES, descriptor table, permeability prediction, confidence, entropy, applicability-domain result, feature interpretation summary, permeability-to-F/ka assumptions, AUC/Cmax/Tmax/CL/F comparisons, limitations, and reference sources.

## PK Equation and Interpretation Layer

The educational PK/NCA module documents IV bolus, oral first-order absorption, elimination, AUC, CL/F, MRT, half-life, and Vss equations. Permeability-related assumptions are mapped to F and ka in an educational oral scenario while dose, Vd, and true CL are held constant. This demonstrates why AUC and Cmax can change and why apparent CL/F can change without claiming that permeability changes true systemic clearance.

## IVIVE Boundary and References

The app explains that IVIVE would require validated intrinsic clearance, protein binding, blood-to-plasma ratio, permeability/solubility, transporter involvement, hepatic blood-flow assumptions, fraction absorbed, bioavailability, route/dose/formulation metadata, and external human PK validation. Reference sources are listed in `docs/reference_sources.md`. This platform currently demonstrates Caco-2 permeability screening and educational absorption scenarios only.

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
