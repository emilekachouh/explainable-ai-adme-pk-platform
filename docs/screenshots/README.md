# Screenshot Index

Fresh screenshots captured from the live Streamlit app (v2 refinement pass).
All 15 screenshots passed automated content checks — no error text, no missing artifacts, no broken cards.

## Regeneration

```bash
# Terminal 1 — start app
.venv/Scripts/streamlit.exe run app/streamlit_app.py --server.port 8507 --server.headless true

# Terminal 2 — capture
.venv/Scripts/python.exe scripts/capture_streamlit_screenshots.py
```

## Screenshot manifest

| Screenshot | Section | What a reviewer should notice | Best use |
|---|---|---|---|
| `01_home_dashboard.png` | Home dashboard | Pharma-style hero, 6 workflow cards, 5 metric chips, scientific boundary banner | GitHub README, recruiter demo |
| `02_how_to_use_and_app_overview.png` | How-to-use / app overview | 7-step beginner workflow expanded, scientific guide, equation panel, IVIVE note | Student onboarding, LinkedIn |
| `03_molecule_input_aspirin.png` | Aspirin molecule profile | SVG structure, canonical SMILES, medicinal-chemistry teaching note, status pills (logP / polarity / domain), key properties | PI review, recruiter demo |
| `04_descriptor_summary.png` | Descriptor and ADME signals | Descriptor table, MW/logP/TPSA/HBD/HBA explanation cards, bar chart, Lipinski flags | PK/ADME reviewer |
| `05_permeability_prediction.png` | Caco-2 permeability prediction | Prediction card, probability progress bar, biological interpretation, dataset context, decision-support text | AI-health recruiter, PI review |
| `06_confidence_and_uncertainty.png` | Confidence and uncertainty | High-confidence category, score, entropy, reliability explanation cards | Model-risk review |
| `07_applicability_domain.png` | Applicability domain | Tanimoto similarity 0.36 (Borderline), nearest training SMILES, domain-shift warning, experimental recommendation | Academic reviewer |
| `08_explainable_ai.png` | Explainable AI evidence | Descriptor driver table with chemical interpretation; SHAP disclaimer | Explainability portfolio |
| `09_molecule_comparison.png` | Molecule Comparison Mode | Color-coded permeability class table (green/red), 7 bar charts (MW/LogP/TPSA/Confidence/Domain/Suggested F/Suggested ka), auto-interpretation paragraph | LinkedIn, recruiter demo |
| `10_pk_nca_simulator.png` | Educational PK/NCA simulator | Concentration-time plot, 7 NCA metric cards (Cmax/Tmax/AUCinf/t½/MRT/CL-F/Vss), route-specific warnings | PI review, PK teaching |
| `11_permeability_to_pk_impact.png` | Permeability → PK Impact centerpiece (top) | Selected molecule banner, core equations card, default assumption mapping, 7 editable parameter controls, 9 exposure metric cards (True CL fixed, AUC ratio, Cmax ratio, Tmax shift, CL/F ratio) | PK/ADME reviewer |
| `12_pk_impact_comparison_curves.png` | PK Impact — curve and scenario panels | Editable scenario parameters, metric cards with delta indicators, linear C-t curve overlay (Reference vs Permeability-adjusted), beginner and PhD interpretation cards | PK teaching, PI review |
| `13_equations_iv_oral_ivive.png` | Equations, IV/oral dosing, IVIVE | PK equations expander, IV vs oral dosing explanation, IVIVE requirements and limitations | Academic review |
| `14_report_download_section.png` | PK Impact — curves + report download | Concentration-time curve (two scenarios), beginner + PhD interpretation, warning banner, three download buttons (markdown report, descriptor CSV, PK impact CSV) | GitHub README, reviewer handoff |
| `15_scientific_limitations_and_reviewer_summary.png` | Evidence and responsible use | Three audience-specific reviewer cards (AI/ML recruiter, computational pharmacology, academic PI), external validation roadmap | PI review, scientific rigor |

## Known UI notes (post-audit)

| Item | Status |
|---|---|
| Comparison table color-coded rows | Fixed (`applymap` → `map` for pandas compatibility) |
| PK Impact curve screenshot distinct from metrics screenshot | Fixed (capture script now scrolls to parameter controls) |
| All 15 screenshots non-empty and content-checked | Confirmed |
| `applymap` pandas deprecation error in comparison mode | Fixed in `app/streamlit_app.py` |

## Scientific boundary

Screenshots show Caco-2 permeability prediction and educational PK/NCA simulation only.
They do not show validated human PK, clinical, regulatory, safety, efficacy, or dose prediction.
True systemic CL is held fixed by design in the permeability-to-PK impact section.
