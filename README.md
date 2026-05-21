# AI-PBPK / ADME Predictor

**Explainable AI-assisted Caco-2 permeability screening with scaffold validation, uncertainty estimation, applicability-domain analysis, SHAP interpretation, and an educational PK/NCA simulator.**

This project is a computational pharmacology portfolio platform for early ADME screening and translational modeling education. It uses a real public Caco-2 permeability dataset and presents predictions responsibly: no clinical, regulatory, safety, efficacy, dose, validated human PK, or PBPK claims are made.

## What This Demonstrates

- Real public ADME dataset integration
- RDKit molecular validation, descriptors, and Morgan fingerprints
- Baseline ML models for Caco-2 permeability classification and regression
- Random split and Bemis-Murcko scaffold split validation
- SHAP explainability for global and local model interpretation
- Confidence scoring and prediction entropy
- Applicability-domain warnings using nearest-neighbor chemical similarity
- Streamlit app with molecule rendering and downloadable reports
- Educational PK/NCA simulator for AUC, AUMC, MRT, CL, CL/F, Vss, lambda_z, half-life, and extrapolated AUC
- Unit-tested Python package structure

## Scientific Motivation

Early drug discovery often requires interpretable, fast, and scientifically honest assessment of permeability-related risk. Caco-2 permeability is a useful in vitro proxy for epithelial transport, but it is not the same as human exposure. This project separates molecular ADME screening from educational PK/NCA simulation so users can learn both ML-based structure-property modeling and pharmacokinetic exposure calculations without overclaiming clinical validity.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Run tests:

```bash
python -m pytest
```

## App Screenshots

Add screenshots before public release:

- `docs/screenshots/app_molecule_input.png`
- `docs/screenshots/app_prediction_summary.png`
- `docs/screenshots/app_explainability.png`
- `docs/screenshots/pk_nca_simulator.png`

## Dataset

Primary dataset: **TDC Caco2_Wang** public benchmark.

| Field | Value |
|---|---|
| Source | Therapeutics Data Commons benchmark mirrored by scikit-fingerprints on Hugging Face |
| Endpoint | Experimental Caco-2 log(Papp) |
| Processed sample size | 906 valid canonicalized molecules |
| ML tasks | Median-threshold permeability classification and continuous log(Papp) regression |
| Dataset documentation | `reports/caco2_wang_dataset_metadata.csv` |

Only real public ADME/PK datasets are allowed for model training and final results. Toy molecules are used only for tests and UI examples.

## Model Metrics

| Validation | Task | Best model | Key metrics |
|---|---|---|---|
| Random split | Classification | XGBoost | AUROC 0.946, F1 0.863 |
| Random split | Regression | Random forest regressor | R2 0.785, MAE 0.297 |
| Scaffold split | Classification | XGBoost | AUROC 0.934, F1 0.841 |
| Scaffold split | Regression | XGBoost regressor | R2 0.650, MAE 0.392 |

## Why Scaffold Split Matters

Random splits can overestimate performance in drug-discovery ML because close structural analogs may appear in both train and test sets. Bemis-Murcko scaffold splitting keeps identical core scaffolds out of both sets simultaneously, giving a stricter estimate of generalization to chemically distinct molecules.

## Explainability

SHAP analyses are generated for the XGBoost classifier and regressor:

- Summary plots
- Beeswarm plots
- Bar importance plots
- Local aspirin explanation
- Local caffeine explanation

Interpretation focuses on TPSA, HBD/HBA, molecular weight, logP, flexibility, and Morgan fingerprint substructure signals.

## Applicability Domain

Predictions include nearest-neighbor Morgan fingerprint Tanimoto similarity to training chemistry. If a molecule is chemically distant from the training set, the app warns:

> This molecule is chemically dissimilar to most training compounds. Prediction reliability may be reduced.

## PK/NCA Simulator

The PK/NCA module is educational and mechanistic. It simulates:

- IV bolus one-compartment profiles
- Oral one-compartment profiles with first-order absorption
- IV infusion profiles

It calculates AUC, AUMC, MRT/MBRT, lambda_z, half-life, extrapolated AUC, percent extrapolated AUC, Cmax, Tmax, CL, CL/F, Vz, and Vss where appropriate. It does not convert Caco-2 permeability into validated human PK.

## Repository Map

```text
app/                 Streamlit interface
data/                Public dataset files
docs/                Guides, model card, architecture, release checklist
models/              Saved baseline model artifacts
notebooks/           Dataset QC and EDA notebook
reports/             Metrics, figures, reports, manuscript drafts
src/adme_predictor/  Source modules
tests/               Unit tests
```

## Key Reports

- `docs/model_card.md`
- `docs/beginner_usage_guide.md`
- `docs/pk_nca_guide.md`
- `reports/technical_report.md`
- `reports/manuscript.md`
- `reports/scaffold_split_comparison.md`
- `reports/shap_interpretation.md`
- `reports/outlier_analysis.md`
- `reports/pk_nca_methods.md`

## Limitations

- Caco-2 permeability is an in vitro assay endpoint, not a clinical endpoint.
- Median-threshold classification is dataset-specific.
- Scaffold validation is more rigorous than random splitting but still not prospective external validation.
- Confidence scores are model-derived uncertainty indicators, not calibrated clinical certainty.
- Applicability-domain warnings depend on fingerprint similarity and cannot detect every reliability issue.
- PK/NCA simulations use assumed parameters and are educational only.

## Future Roadmap

- External validation with additional public ADME datasets
- Scaffold validation across solubility, clearance, protein binding, and bioavailability endpoints
- Model calibration and conformal prediction
- Larger public benchmark comparison
- Explicit transporter and ionization features
- Educational PBPK extensions clearly separated from validated predictive claims
- Deployment-ready app screenshots and hosted demo

## Citation

If using this project, cite the underlying data source and tools:

- Therapeutics Data Commons Caco2_Wang benchmark
- RDKit
- scikit-learn
- XGBoost
- SHAP

Formal citation details should be added before publication or manuscript submission.

## License

Add an explicit open-source license before public release. Suggested options: MIT for software code, with separate notes for public dataset usage and citations.

## Author / Contact

Author: `<Your Name>`  
Contact: `<email or LinkedIn>`  
Portfolio: `<portfolio URL>`
