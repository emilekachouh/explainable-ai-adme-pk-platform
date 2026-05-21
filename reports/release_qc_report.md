# Release QC Report

Generated: by `scripts/qc_release_check.py`

**Result: PASS**  
Passed: 74 | Failed: 0 | Warnings: 0 | Total: 74

## Check Results

| Status | Check | Notes |
|---|---|---|
| [OK] PASS | File exists: README.md |  |
| [OK] PASS | File exists: LICENSE |  |
| [OK] PASS | File exists: CONTRIBUTING.md |  |
| [OK] PASS | File exists: CODE_OF_CONDUCT.md |  |
| [OK] PASS | File exists: CITATION.cff |  |
| [OK] PASS | File exists: SECURITY.md |  |
| [OK] PASS | File exists: CHANGELOG.md |  |
| [OK] PASS | File exists: requirements.txt |  |
| [OK] PASS | File exists: app/streamlit_app.py |  |
| [OK] PASS | File exists: docs/model_card.md |  |
| [OK] PASS | File exists: docs/data_card.md |  |
| [OK] PASS | File exists: docs/methods.md |  |
| [OK] PASS | File exists: docs/screenshots/README.md |  |
| [OK] PASS | File exists: src/adme_predictor/__init__.py |  |
| [OK] PASS | File exists: tests/conftest.py |  |
| [OK] PASS | File exists: pytest.ini |  |
| [OK] PASS | Unsafe phrase scan: app\streamlit_app.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\applicability.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\app_health.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\config.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\data.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\demo_model.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\drug_pk_profiles.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\education.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\evaluation.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\example_molecules.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\features.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\fold_change.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\interpretability.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\modeling.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\nca.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\pk.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\pk_visualization.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\reporting.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\scaffold.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\uncertainty.py |  |
| [OK] PASS | Unsafe phrase scan: src\adme_predictor\__init__.py |  |
| [OK] PASS | Unsafe phrases in Markdown docs |  |
| [OK] PASS | Screenshot exists: 01_home_dashboard.png |  |
| [OK] PASS | Screenshot exists: 02_single_molecule_profile.png |  |
| [OK] PASS | Screenshot exists: 03_descriptor_based_interpretation.png |  |
| [OK] PASS | Screenshot exists: 04_batch_upload.png |  |
| [OK] PASS | Screenshot exists: 05_batch_results.png |  |
| [OK] PASS | Screenshot exists: 06_molecule_comparison.png |  |
| [OK] PASS | Screenshot exists: 07_multi_drug_pk_overlay.png |  |
| [OK] PASS | Screenshot exists: 08_absorption_sensitivity_simulator.png |  |
| [OK] PASS | Screenshot exists: 09_report_download.png |  |
| [OK] PASS | Screenshot exists: 10_model_credibility_limits.png |  |
| [OK] PASS | docs/screenshots/README.md exists |  |
| [OK] PASS | Screenshot not blank: 01_home_dashboard.png |  |
| [OK] PASS | Screenshot not blank: 02_single_molecule_profile.png |  |
| [OK] PASS | Screenshot not blank: 03_descriptor_based_interpretation.png |  |
| [OK] PASS | Screenshot not blank: 04_batch_upload.png |  |
| [OK] PASS | Screenshot not blank: 05_batch_results.png |  |
| [OK] PASS | Screenshot not blank: 06_molecule_comparison.png |  |
| [OK] PASS | Screenshot not blank: 07_multi_drug_pk_overlay.png |  |
| [OK] PASS | Screenshot not blank: 08_absorption_sensitivity_simulator.png |  |
| [OK] PASS | Screenshot not blank: 09_report_download.png |  |
| [OK] PASS | Screenshot not blank: 10_model_credibility_limits.png |  |
| [OK] PASS | requirements.txt contains: streamlit |  |
| [OK] PASS | requirements.txt contains: pandas |  |
| [OK] PASS | requirements.txt contains: numpy |  |
| [OK] PASS | requirements.txt contains: rdkit |  |
| [OK] PASS | requirements.txt contains: scikit-learn |  |
| [OK] PASS | requirements.txt contains: xgboost |  |
| [OK] PASS | requirements.txt contains: joblib |  |
| [OK] PASS | tests/ directory exists |  |
| [OK] PASS | At least 15 test files present | Found 18 test files |
| [OK] PASS | app/streamlit_app.py parses (no syntax error) |  |
| [OK] PASS | Molecule library count >= 200 (221 found) | Found approximately 221 molecules; expected >= 200 |
| [OK] PASS | README title contains 'Caco-2' | Title may still use overclaiming name |
| [OK] PASS | README does not use 'AI-PBPK' title | Found 'AI-PBPK' in README header area |
| [OK] PASS | README has LICENSE section |  |
| [OK] PASS | README has live app placeholder or URL |  |

---
Run `python scripts/qc_release_check.py` to regenerate.
