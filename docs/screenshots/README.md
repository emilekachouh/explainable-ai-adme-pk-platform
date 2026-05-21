# Screenshot Index

Screenshots generated from the Explainable AI ADME-PK Platform after the full professional refinement pass (v2).

## Regeneration instructions

```bash
# Start the app in one terminal
.venv/Scripts/streamlit.exe run app/streamlit_app.py

# In another terminal, generate screenshots
.venv/Scripts/python.exe scripts/capture_streamlit_screenshots.py
```

## Screenshot manifest

| Screenshot | App section shown | What a reviewer should notice | Recommended use |
|---|---|---|---|
| `01_home_dashboard.png` | Home dashboard | Pharma-style hero, workflow cards, metric summary, and scientific boundary banner. | GitHub README, recruiter demo |
| `02_how_to_use_and_app_overview.png` | How-to-use and app overview | 7-step beginner workflow, scientific grounding, and expandable guides. | GitHub README, student onboarding |
| `03_molecule_input_aspirin.png` | Aspirin molecule profile | SVG rendering, canonical SMILES, medicinal chemistry teaching note, key properties, and status pills. | PI review, recruiter demo |
| `04_descriptor_summary.png` | Descriptor and ADME signals | Descriptor table, explanation cards for MW/logP/TPSA/HBD/HBA, medicinal chemistry interpretation, and Lipinski flags. | PK/ADME reviewer |
| `05_permeability_prediction.png` | Caco-2 permeability prediction | Prediction card, probability gauge, biological interpretation, dataset context, and decision-support text. | AI-health recruiter, PI review |
| `06_confidence_and_uncertainty.png` | Confidence and uncertainty | Confidence score, entropy, reliability explanation, and boundary card. | Model-risk review |
| `07_applicability_domain.png` | Applicability domain | Tanimoto similarity gauge, nearest training SMILES, domain category, and experimental follow-up recommendation. | Academic reviewer |
| `08_explainable_ai.png` | Explainable AI evidence | Descriptor driver table with chemical interpretation; SHAP disclaimer and optional saved SHAP figures. | Explainability portfolio |
| `09_molecule_comparison.png` | Molecule comparison mode | Aspirin, caffeine, ibuprofen, metformin, and propranolol; MW/logP/TPSA/confidence/domain/F/ka bar charts; auto-interpretation. | LinkedIn, recruiter demo |
| `10_pk_nca_simulator.png` | Educational PK/NCA simulator | Drug teaching profile loader, preset selector, parameter controls, 7 NCA metric cards, linear/semilog plots. | PI review, PK teaching |
| `11_permeability_to_pk_impact.png` | Permeability to PK Impact — centerpiece | Molecule summary, editable Dose/Vd/CL/F/ka sliders, reference vs adjusted PK curve overlay. | PK/ADME reviewer |
| `12_pk_impact_comparison_curves.png` | PK impact comparison curves | Linear and semi-log concentration-time curve tabs; true CL fixed annotation; scenario table. | PK teaching, PI review |
| `13_equations_iv_oral_ivive.png` | Equations, IV/oral, IVIVE | AUC_oral = F × Dose / CL; CL/F; kel; route-specific NCA distinctions; IVIVE limitations. | Academic review |
| `14_report_download_section.png` | Report download section | Structured markdown report with molecule profile, descriptors, prediction, AUC ratios, CL/F, equations, and references. | GitHub README, reviewer handoff |
| `15_scientific_limitations_and_reviewer_summary.png` | Scientific limits and reviewer summary | Reviewer summary cards for AI/ML recruiter, comp. pharm., and academic PI; external validation roadmap. | PI review, scientific rigor |

## Scientific boundary

Screenshots show Caco-2 permeability prediction and educational PK/NCA simulation only. They do not show validated human PK, clinical, regulatory, safety, efficacy, or dose prediction. The permeability-to-PK impact section shows educational absorption assumption exploration with true CL held constant by design.
