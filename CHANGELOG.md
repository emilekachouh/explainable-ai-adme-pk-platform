# Changelog

All notable changes to the Explainable Caco-2 Permeability Screening + PK Education Platform
are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2025

### Added

**Core ML pipeline**
- Caco-2 permeability classification trained on TDC Caco2_Wang public benchmark (906 molecules)
- RDKit descriptor featurisation: MW, logP, TPSA, HBD/HBA, rotatable bonds, rings, Csp3, Morgan fingerprints
- Random Forest and XGBoost classifiers; random forest and XGBoost regressors
- Random train/test split and Bemis-Murcko scaffold split validation (both reported)
- Binary entropy confidence scoring and probability-margin confidence
- Nearest-neighbour Tanimoto applicability-domain check with explicit out-of-domain warnings
- Graceful fallback to descriptor-based heuristic prediction if model artifacts unavailable

**Single molecule screening workbench**
- SMILES input and validation (RDKit canonicalization)
- 221 RDKit-validated example molecules across 18 therapeutic categories
- Descriptor table, Lipinski/ADME rule-based flags, physicochemical status pills
- Caco-2 permeability prediction with probability, confidence category, and entropy
- Applicability-domain Tanimoto similarity with domain-shift warning
- Descriptor-based model interpretation panel (rule-based threshold profiles; distinct from live SHAP)
- SVG molecule rendering (no GUI/X11 dependencies)
- Per-molecule experiment recommendation

**Batch SMILES screening**
- CSV upload (name, smiles, optional category columns) and paste-SMILES input
- Per-molecule: validation, canonicalization, descriptors, prediction, confidence, applicability domain, scenario F/ka
- Summary metrics: total / valid / invalid / high-perm / low-perm / outside-domain count
- Top-ranked compound lists: most permeability-favorable, most polarity-limited, highest-confidence high-perm
- Downloadable results CSV and failures CSV

**Molecule comparison mode**
- Side-by-side comparison of 2–10 molecules across physicochemical, model & trust, and PK assumption tabs
- Bar charts for MW, logP, TPSA, Caco-2 probability, confidence, applicability similarity, scenario F/ka
- Automatic beginner and PhD-level comparison interpretation

**Multi-drug PK comparison**
- Select 2–5 molecules; compute permeability-informed oral PK curve comparison
- Scenario-adjusted and reference overlays with distinct traces
- AUC / Cmax / CL/F ratio table and bar charts
- Literature teaching preset notes for supported drugs

**Educational PK/NCA simulator**
- IV bolus, oral first-order absorption, IV infusion one-compartment profiles
- 6 teaching presets + 26 curated literature drug PK teaching profiles
- NCA metrics: AUC, AUMC, MRT/MBRT, lambda_z, t1/2, Cmax, Tmax, CL, CL/F, Vz, Vss
- Linear and semi-log C-t overlay plots

**Absorption sensitivity simulator**
- User-editable scenario F and ka (mapped from Caco-2 probability as starting point)
- Reference vs permeability-adjusted oral PK overlay
- AUC ratio, Cmax ratio, Tmax shift, CL/F ratio
- True CL held fixed by design; CL/F changes with F
- Explicit disclaimer that F and ka are educational assumptions, not model predictions

**Report and export**
- Downloadable per-molecule markdown report
- Descriptor CSV and PK-impact table CSV
- Multi-drug comparison markdown report and metrics CSV

**Evidence and documentation**
- Evidence & Limits page: model trust panel, validation comparison, responsible-use notes
- Reviewer summary for AI/ML recruiters, pharmacologists, and PIs
- Offline SHAP figure support (loadable from `reports/figures/shap/` if generated)

**Scientific safety**
- No clinical, regulatory, safety, efficacy, dose, or validated human PK claims
- Scenario F and ka clearly labeled as educational assumptions throughout
- Permeability-to-CL relationship explicitly denied ("permeability does not determine true systemic CL")
- 179+ automated tests for scientific correctness and software correctness

**Open-source release**
- MIT License
- CONTRIBUTING.md, CODE_OF_CONDUCT.md, CITATION.cff, SECURITY.md
- docs/data_card.md, docs/methods.md, docs/model_card.md
- scripts/qc_release_check.py for automated release QC
- 10 curated screenshots in docs/screenshots/
