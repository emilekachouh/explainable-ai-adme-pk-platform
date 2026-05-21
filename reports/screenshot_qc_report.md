# Screenshot QC Report

Generated: 2026-05-21
Capture script: `scripts/capture_streamlit_screenshots.py`
Output directory: `docs/screenshots/`

## Summary

| Metric | Value |
|---|---|
| Screenshots targeted | 10 |
| Screenshots produced | 10 |
| QC issues found | 0 |
| Bad-phrase violations | 0 |

**Result: PASS**

## Screenshot inventory

| File | Size | Section | Reviewer focus | Use |
|---|---|---|---|---|
| `01_home_dashboard.png` | ~297 KB | Home dashboard | Title correct ("Caco-2 Permeability + PK Education"), workflow strip, metric cards, scientific boundary notice | GitHub README, recruiter |
| `02_single_molecule_profile.png` | ~297 KB | Single molecule | Aspirin SVG rendered, canonical SMILES, descriptor pills, key properties | PI review, recruiter |
| `03_descriptor_based_interpretation.png` | ~371 KB | Descriptor interpretation | Panel labeled "Descriptor-Based Model Interpretation" not "Explainable AI" or "SHAP" | Explainability portfolio |
| `04_batch_upload.png` | ~209 KB | Batch screening upload | CSV uploader + paste-SMILES tabs visible, format hint card shown | Pharma usability |
| `05_batch_results.png` | ~222 KB | Batch screening results | 5-compound run: summary metrics, results table, top-ranked lists, download buttons | Pharma usability, README |
| `06_molecule_comparison.png` | ~203 KB | Molecule comparison | Multi-tab comparison across selected drugs | LinkedIn, recruiter |
| `07_multi_drug_pk_overlay.png` | ~164 KB | Multi-drug PK | Multiple visible PK curves with distinct traces | PI, PK teaching |
| `08_absorption_sensitivity_simulator.png` | ~361 KB | Absorption sensitivity | F/ka controls, reference vs adjusted overlay, exposure ratios, disclaimer | PK/ADME reviewer |
| `09_report_download.png` | ~234 KB | Report download | Report preview and download buttons; no "predicted F" language visible | README, reviewer |
| `10_model_credibility_limits.png` | ~173 KB | Evidence & Limits | Model trust panel, validation modes, scientific boundaries | PI review, rigor |

## Bad-phrase scan results

Phrases checked against every screenshot's page body text at capture time:

| Phrase | Result |
|---|---|
| `model artifact missing` | NOT FOUND |
| `Baseline model artifact not found` | NOT FOUND |
| `Molecule image could not be rendered` | NOT FOUND |
| `Renderer unavailable here` | NOT FOUND |
| `predicted F` | NOT FOUND |
| `predicted bioavailability` | NOT FOUND |
| `model predicts human F` | NOT FOUND |
| `app error traceback` | NOT FOUND |
| `Traceback (most recent call last)` | NOT FOUND |
| `Select at least 2 molecules` | NOT FOUND |
| `SHAP figure files are not present` | NOT FOUND |
| `ADME Workbench` (old nav label) | NOT FOUND |

## QC notes

- Screenshot 03 confirms the interpretation panel is labeled with rule-based descriptor framing, not SHAP.
- Screenshot 07 shows multi-drug PK curves from the default 5-drug selection; distinct traces are visible.
- Screenshot 05 captures batch results after pasting 5 SMILES; summary metric cards and results table are populated.
- All molecule SVGs rendered successfully; no blank structure panels observed.

## To regenerate screenshots

```bash
# Ensure Streamlit is running on port 8507
streamlit run app/streamlit_app.py --server.port 8507 --server.headless true

# In a separate terminal
python scripts/capture_streamlit_screenshots.py
```

The QC report updates automatically on each run.
