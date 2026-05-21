# Open-Source Release Checklist

Use this checklist before every public GitHub push or Streamlit Community Cloud deployment.

## Legal and licensing

- [x] LICENSE file present (MIT)
- [x] Copyright holder named in LICENSE
- [x] TDC dataset license terms noted in LICENSE
- [x] No proprietary data in `data/` or `models/`
- [x] No patient data, PHI, or PII anywhere in repository
- [x] SECURITY.md warns about not uploading sensitive structures to public demo

## Repository hygiene

- [x] `.gitignore` covers `.venv/`, `__pycache__/`, `*.pyc`, secrets, `.env`
- [ ] No secrets, API keys, or credentials committed
- [ ] No large binary files (> 50 MB) committed
      (model `.joblib` artifacts are small; verify with `git ls-files --others --exclude-standard`)
- [x] `pytest-cache-files-*` directories removed from root or gitignored
- [x] `.streamlit/New Text Document.txt` removed or gitignored
- [x] `requirements.txt` present and tested

## Documentation

- [x] README.md polished and accurate
- [x] README title: "Explainable Caco-2 Permeability Screening + PK Education Platform"
- [x] README molecule count accurate (221)
- [x] README test count accurate (179+)
- [x] README screenshot paths correct
- [x] README SHAP section accurately labeled (offline artifacts, not live)
- [x] docs/model_card.md updated with correct title
- [x] docs/data_card.md present
- [x] docs/methods.md present
- [x] CONTRIBUTING.md present
- [x] CHANGELOG.md present
- [x] CITATION.cff present
- [x] CODE_OF_CONDUCT.md present

## Scientific claims

- [x] App does not claim to predict human bioavailability F
- [x] App does not claim to perform validated PBPK
- [x] App does not make clinical, dose, safety, efficacy, or regulatory claims
- [x] Scenario F and ka are labeled as educational assumptions throughout
- [x] Descriptor-based interpretation is not labeled as live SHAP
- [x] All literature PK values labeled as "approximate teaching values"
- [x] reports/language_claims_audit.md reviewed

## Testing

- [x] `python -m pytest` passes (179+ tests)
- [x] `python scripts/qc_release_check.py` passes
- [x] App loads without crash: `streamlit run app/streamlit_app.py`
- [x] Single molecule screening works
- [x] Batch screening works
- [x] Molecule comparison works
- [x] Multi-drug PK overlay shows multiple curves
- [x] Absorption sensitivity simulator works
- [x] Report downloads work
- [x] No "Renderer unavailable" messages
- [x] No import errors in app startup

## Screenshots

- [x] 10 screenshots present in `docs/screenshots/`
- [x] docs/screenshots/README.md updated
- [x] reports/screenshot_qc_report.md reviewed
- [x] No blank molecule structures in screenshots
- [x] No "predicted F" in any screenshot
- [x] No misleading SHAP label in any screenshot

## GitHub actions (manual)

- [ ] Repository description set: "Explainable Caco-2 permeability screening + educational PK simulation platform"
- [ ] GitHub topics added: `caco2`, `adme`, `pharmacokinetics`, `cheminformatics`, `rdkit`, `machine-learning`, `streamlit`, `drug-discovery`
- [ ] Live app URL added to README once deployed: `<insert Streamlit Cloud URL>`
- [ ] Badge URLs updated in README once CI/CD is configured
