# Contributing

Thank you for your interest in contributing to the Explainable Caco-2 Permeability Screening + PK Education Platform.

## Setting up the environment

```bash
git clone <repository-url>
cd ai-pbpk-adme-predictor
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Running tests

```bash
python -m pytest
```

All 179+ tests must pass before a pull request can be merged.

## Running the app locally

```bash
streamlit run app/streamlit_app.py
```

## Opening issues

- Use the GitHub Issues tracker.
- Label bugs, feature requests, and documentation issues clearly.
- For scientific concerns (e.g., incorrect PK logic, overclaiming language), label them `scientific-accuracy`.

## Contribution areas

- Bug fixes in `src/adme_predictor/`
- Additional example molecules (must be RDKit-valid, real drug SMILES)
- Additional literature PK teaching profiles (must cite a reference, labeled as approximate)
- Documentation improvements
- Test coverage improvements
- UI/UX improvements to `app/streamlit_app.py`
- Performance improvements
- Accessibility improvements

## Scientific caution

This project makes deliberate scientific claims and has deliberate scientific limits.
Before modifying model logic, PK equations, interpretation language, or claim language, read:

- `docs/model_card.md`
- `docs/data_and_modeling_policy.md`
- `docs/pk_nca_guide.md`
- The `SCIENTIFIC_BOUNDARIES` constant in `src/adme_predictor/education.py`

**Do not add:**
- Claims that the model predicts validated human bioavailability F
- Claims that permeability determines true systemic clearance
- Clinical, regulatory, safety, efficacy, or dose prediction claims
- Unsourced or invented PK parameters labeled as literature values
- Models trained on non-public or proprietary data without clear documentation

## Commit style

Use short imperative commit messages:
- `fix: correct CL/F formula in education.py`
- `feat: add solubility descriptor flag`
- `docs: update model card limitations section`
- `test: add batch screening 50-compound stress test`

## Code style

- Python 3.9+ compatible
- Type hints on all public functions
- No comments that explain what code does — only comments explaining why
- No unused imports

## Pull request checklist

- [ ] All tests pass (`python -m pytest`)
- [ ] No new unsafe scientific claims introduced
- [ ] Screenshot README updated if UI changed
- [ ] `reports/language_claims_audit.md` reviewed if claim language changed
