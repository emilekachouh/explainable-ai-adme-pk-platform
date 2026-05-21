# Screenshot Index

Fresh screenshots captured after batch-screening addition and descriptor-based explainability label fixes (post SHAP-overclaiming cleanup).

| Screenshot | App section shown | What reviewer should look at | Recommended use |
|---|---|---|---|
| `01_home_dashboard.png` | Home dashboard | App title, workflow strip, metric cards, and scientific boundary notice. | GitHub README, recruiter demo |
| `02_single_molecule_profile.png` | Single molecule profile | Aspirin SVG structure, canonical SMILES, key physicochemical properties, descriptor status pills. | PI review, recruiter demo |
| `03_descriptor_based_interpretation.png` | Descriptor-based interpretation | Rule-based descriptor threshold profile (not labeled SHAP), driver analysis, chemical caveats. | Explainability portfolio, AI-health recruiter |
| `04_batch_upload.png` | Batch screening — upload | CSV file uploader and paste-SMILES input panels with format hint card. | Pharma usability, recruiter demo |
| `05_batch_results.png` | Batch screening — results | Summary metrics, results table, top-ranked lists, and download buttons for a 5-compound run. | Pharma usability, GitHub README |
| `06_molecule_comparison.png` | Molecule comparison | Physicochemical, model & trust, and PK assumptions tabs across 5 compounds. | LinkedIn, recruiter demo |
| `07_multi_drug_pk_overlay.png` | Multi-drug PK overlay | Five-drug scenario-adjusted oral PK curves visible simultaneously with distinct traces. | PI review, PK teaching |
| `08_absorption_sensitivity_simulator.png` | Absorption sensitivity simulator | F/ka sliders, reference vs adjusted C-t overlay, exposure ratios, and educational disclaimer. | PK/ADME reviewer |
| `09_report_download.png` | Report download section | Report preview and markdown/CSV download buttons. No 'predicted F' language. | GitHub README, reviewer handoff |
| `10_model_credibility_limits.png` | Model credibility and limits | Model trust panel, validation mode comparison, scientific boundaries, and responsible-use notice. | PI review, scientific rigor |

**Scientific boundary:** screenshots show Caco-2 permeability classification and educational PK/NCA simulation only. No validated human PK, clinical, regulatory, safety, efficacy, or dose prediction is shown.

**Explainability label:** the interpretation panel is labeled 'Descriptor-Based Model Interpretation' — not SHAP. SHAP figures are offline-only artifacts stored under `reports/figures/shap/`.
