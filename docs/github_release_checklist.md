# GitHub Release Checklist

## Validation

- Run `python -m pytest`
- Run `streamlit run app/streamlit_app.py`
- Test example molecules in the app
- Test PK/NCA simulator routes
- Verify downloadable reports work

## Files and Reports

- Verify `README.md`
- Verify `docs/model_card.md`
- Verify `docs/beginner_usage_guide.md`
- Verify `docs/architecture.md`
- Verify `reports/technical_report.md`
- Verify `reports/manuscript.md`
- Verify `reports/scaffold_split_comparison.md`
- Verify `reports/shap_interpretation.md`
- Verify `reports/outlier_analysis.md`
- Verify `reports/pk_nca_methods.md`

## Figures

- Verify `reports/figures/`
- Verify `reports/figures/shap/`
- Add app screenshots to `docs/screenshots/`

## Safety and Release Hygiene

- Check no secrets or credentials are present
- Check no private data are present
- Check no huge unnecessary files are committed
- Confirm dataset source and license/usage notes are documented
- Confirm model limitations are clear
- Confirm clinical/regulatory claims are not made

## GitHub Setup

- Add explicit license file
- Make initial commit
- Push to GitHub
- Add repository topics:
  - `adme`
  - `pharmacokinetics`
  - `machine-learning`
  - `rdkit`
  - `streamlit`
  - `drug-discovery`
  - `computational-pharmacology`
- Add screenshots to README
- Add a short demo video or GIF
- Create first release tag
