# Explainable AI ADME-PK Platform

**Real-data Caco-2 permeability prediction with explainability, applicability-domain checks, molecule comparison, educational PK/NCA simulation, and a permeability-to-PK impact centerpiece.**

> This platform takes a molecule, computes medicinal chemistry descriptors, predicts Caco-2 permeability risk using a real-data ML model, checks confidence and applicability domain, explains the prediction, and shows how permeability-related assumptions can alter educational oral PK simulations such as AUC, Cmax, Tmax, and CL/F. It is for ADME learning and hypothesis generation, not validated clinical PK prediction.

This is a computational pharmacology portfolio platform for early ADME screening and translational modeling education. It uses a real public Caco-2 permeability dataset and presents predictions responsibly: no clinical, regulatory, safety, efficacy, dose, validated human PK, or PBPK claims are made.

## What This Demonstrates

- Real public Caco-2 ADME dataset (TDC Caco2_Wang, 906 compounds)
- RDKit molecular validation, descriptors, and Morgan fingerprints
- Random Forest and XGBoost classifiers for Caco-2 permeability classification
- Random split and Bemis-Murcko scaffold split validation
- SHAP explainability for global and local model interpretation
- Binary entropy confidence scoring and prediction uncertainty
- Applicability-domain checks via nearest-neighbor Tanimoto similarity
- Pharma-style Streamlit workbench: SVG rendering, searchable 172-molecule library, comparison mode, downloadable reports
- Deployment-safe model loading with graceful descriptor-based fallback
- **Permeability-to-PK Impact centerpiece**: editable F/ka/Dose/Vd/CL parameters, overlay concentration-time curves (linear + semilog), AUC/Cmax/Tmax/CL-F ratio metrics, true CL held fixed by design
- Educational PK/NCA simulator with 6 teaching presets + 10 literature drug profiles (aspirin, ibuprofen, caffeine, metformin, propranolol, atenolol, warfarin, diazepam, midazolam, omeprazole)
- Explanation levels: Beginner, Pharmaceutics graduate student, PI / PK reviewer, AI/ML recruiter
- 82 unit tests covering scientific correctness (AUC ratios, CL/F invariance, true CL not changed by permeability) and software correctness

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

## Live App

Live demo URL: `<add Streamlit Cloud URL after deployment>`

The deployed app is intended as an interactive portfolio demonstration for explainable ADME screening and PK/NCA education. It should not be presented as a clinical, regulatory, safety, efficacy, dose, or validated human PK prediction tool.

## Recruiter and Reviewer Demo Value

The app is designed to communicate both software and scientific judgment:

- AI-health recruiters can see a deployed, interactive ML product rather than a static notebook.
- Biotech hiring managers can review model outputs, confidence, applicability domain, and scientific boundaries in one workflow.
- PK/ADME reviewers can inspect descriptors, Caco-2 interpretation, scaffold-validation rationale, and PK/NCA assumptions.
- The interface demonstrates deployment readiness: health checks, cached operations, graceful fallbacks, SVG rendering, and downloadable reports.

## App Screenshots

Add or update screenshots before public release:

- `docs/screenshots/adme_workbench.png`
- `docs/screenshots/molecule_comparison.png`
- `docs/screenshots/pk_nca_simulator.png`
- `docs/screenshots/evidence_limits.png`

## Streamlit Demo Experience

The app has been upgraded from a basic SMILES form into a structured workbench:

- Sidebar navigation for ADME screening, molecule comparison, PK/NCA simulation, and evidence review
- Beginner-friendly and reviewer-level explanation modes
- Clean page title, scientific subtitle, metric cards, tabs, expanders, and warning states
- SVG molecule rendering to avoid GUI/X11 dependencies on Streamlit Cloud
- Cached descriptor, prediction, applicability-domain, and rendering calls for lightweight deployment
- Graceful fallback messages when optional model artifacts or SHAP images are unavailable
- Markdown report download plus descriptor and PK-impact CSV downloads

## What The App Does

The platform links molecular structure to explainable Caco-2 permeability prediction, then shows how permeability-related assumptions can influence educational oral PK simulations. It combines RDKit descriptors, a real-data ML permeability model, confidence scoring, applicability-domain checks, SHAP-style interpretation, molecule comparison, and PK/NCA teaching tools. It is intended for early ADME learning and hypothesis generation, not clinical PK prediction.

## How To Use

1. Select an example molecule or paste a SMILES.
2. Review MW, logP, TPSA, HBD/HBA, and related descriptors.
3. View the Caco-2 permeability prediction.
4. Check confidence and applicability domain.
5. Compare molecules in comparison mode.
6. Use the Permeability to PK Impact tool to explore F and ka assumptions.
7. Download the markdown report and CSV tables.

## Model Loading and Deployment Behavior

The Streamlit app expects two lightweight artifacts:

- `models/baseline_permeability_classifier.joblib`
- `models/baseline_feature_columns.joblib`

These are intentionally allowed in git because they are small enough for deployment and prevent the app from showing an empty "train the model first" state. If artifacts are unavailable, the app attempts first-run training through the existing public-data pipeline. If that also fails, it uses a transparent descriptor-based educational fallback so the demo remains usable while clearly labeling the prediction source.

## Example Molecule Library

The app includes **172 RDKit-canonicalized example molecules** organized by category:

- Analgesics/NSAIDs
- CNS drugs
- Cardiovascular drugs
- Antibiotics
- Antivirals
- Oncology drugs
- Steroids/hormones
- GI drugs
- Immunosuppressants
- Natural products/cannabinoids
- PK teaching examples
- Highly polar/low permeability examples
- Lipophilic/high permeability examples

Examples include caffeine, aspirin, ibuprofen, acetaminophen, naproxen, diclofenac, warfarin, beta blockers, calcium-channel blockers, statins, antibiotics, antivirals, oncology drugs, steroids, cannabinoids, and PK teaching compounds. Molecules with difficult peptide/biologic representations were skipped rather than represented with invented SMILES.

## Permeability to PK Impact — Centerpiece

This is the most scientifically interesting part of the platform. After predicting Caco-2 permeability for a selected molecule, the app:

1. Maps the permeability class probability to educational oral absorption assumptions (F and ka).
2. Lets the user edit Dose, Vd, true CL, reference F, reference ka, adjusted F, and adjusted ka.
3. Simulates two oral one-compartment profiles (reference and permeability-adjusted).
4. Plots both profiles on linear and semi-log axes.
5. Reports AUC ratio, Cmax ratio, Tmax shift, CL/F ratio — all with true CL held constant by design.
6. Provides beginner and PhD-level interpretation of why AUC changes, why CL/F changes, and why true CL does not change from permeability.

**Correct scientific logic preserved:**
- Permeability may affect F and ka (absorption assumptions).
- F affects AUC_oral = F × Dose / CL.
- ka affects Cmax and Tmax (absorption-rate-limited shape).
- True CL remains unchanged unless the user explicitly edits it.
- CL/F changes because F changes; apparent oral clearance is not true systemic clearance.

## Comparison Mode

The molecule comparison workflow lets users select 2-5 example molecules and compare:

- Molecular weight, LogP, TPSA, HBD/HBA
- Predicted Caco-2 permeability class and probability
- Prediction confidence score
- Applicability-domain nearest-neighbor similarity
- **Suggested F and ka** derived from permeability probability (new in v2)

Bar charts for all seven columns, plus automatic beginner and PhD-level interpretation.

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

The simulator includes teaching presets:

- IV bolus high clearance compound
- IV bolus low clearance compound
- Oral fast absorption
- Oral slow absorption
- Flip-flop kinetics example
- Insufficient sampling example

And 10 **literature drug teaching profiles** (approximate values for educational use, verify before scientific use):

- Aspirin, Ibuprofen, Caffeine, Metformin, Propranolol, Atenolol, Warfarin, Diazepam, Midazolam, Omeprazole

Educational expanders explain AUC, AUMC, MRT/MBRT, CL, CL/F, and Vss in beginner-friendly language while preserving the boundary that all outputs depend on assumed parameters.

### PK Equations

- IV bolus: `C(t) = Dose / Vd x exp(-kel x t)`
- Oral first-order absorption: `C(t) = (F x Dose x ka) / [Vd x (ka - kel)] x [exp(-kel x t) - exp(-ka x t)]`
- Elimination: `kel = CL / Vd`
- IV AUC: `AUC_IV = Dose / CL`
- Oral AUC: `AUC_oral = F x Dose / CL`
- Apparent oral clearance: `CL/F = Dose / AUC`
- NCA residence time: `MRT = AUMC / AUC`
- Half-life: `t1/2 = ln(2) / lambda_z`
- IV Vss assumption: `Vss = Dose x AUMC / AUC^2`

IV bolus places drug directly into systemic circulation, so F = 1 by definition. Oral dosing includes absorption and first-pass effects, so oral profiles report apparent clearance CL/F unless F is independently known. Permeability-related assumptions can influence F and ka in educational oral scenarios; they do not determine true systemic clearance.

## IVIVE and References

IVIVE means in vitro-in vivo extrapolation. A validated human PK workflow would require experimentally measured or validated inputs such as intrinsic clearance, protein binding, blood-to-plasma ratio, permeability/solubility, transporter involvement, hepatic blood-flow assumptions, fraction absorbed, bioavailability, route/dose/formulation metadata, and external human PK validation.

Reference sources are listed in `docs/reference_sources.md`, including FDA PBPK and bioavailability guidance pages, EMA PBPK reporting guidance, EMA clinical pharmacology/PK Q&A, and textbook references requiring citation-detail verification before publication.

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
