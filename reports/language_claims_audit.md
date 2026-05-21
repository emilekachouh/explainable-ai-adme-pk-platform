# Language and Claims Audit

Automated and manual audit of potentially unsafe or misleading language across the repository.
Last updated: 2026-05-21.

## Phrases audited

| Phrase | Where searched | Found | Status |
|---|---|---|---|
| `predicted F` | All Python, Markdown | No | PASS |
| `predicted bioavailability` | All Python, Markdown | No | PASS |
| `predicts human PK` | All Python, Markdown | No | PASS |
| `human PK predictor` | All Python, Markdown | No | PASS |
| `validated PK prediction` | All Python, Markdown | No | PASS |
| `clinical prediction` | All Python, Markdown | No | PASS |
| `dose recommendation` | All Python, Markdown | No | PASS |
| `safety prediction` | All Python, Markdown | No | PASS |
| `efficacy prediction` | All Python, Markdown | No | PASS |
| `SHAP` (live/runtime claim) | app/streamlit_app.py | Qualified — see below | REVIEW |
| `ADME-PK Platform` | README, app, docs | Removed | FIXED |
| `AI-PBPK` | README, docs, reports | Present in technical_report.md / model_card.md legacy | FIXED |
| `Explainable AI ADME-PK` | README | Present (old title) | FIXED |
| `Suggested F` | README comparison section | Present | FIXED |
| `172 example molecules` | README | Present (stale count) | FIXED |
| `82 unit tests` | README | Present (stale count) | FIXED |

## SHAP usage audit

The word "SHAP" appears in several contexts. Each is reviewed:

| Location | Context | Assessment |
|---|---|---|
| `app/streamlit_app.py` descriptor interpretation panel | States: "This panel... is NOT a SHAP explanation. Optional SHAP artifact figures are shown below if saved offline." | SAFE — explicit disclaimer |
| `app/streamlit_app.py` offline SHAP figure loader | Loads PNG files from `reports/figures/shap/` only if they exist | SAFE — gated by file existence |
| `app/streamlit_app.py` interpretation section header | "Descriptor threshold profile — {name} (rule-based, not SHAP)" | SAFE |
| `app/streamlit_app.py` descriptor driver note | "Descriptor driver analysis... not computed SHAP values" | SAFE |
| `app/streamlit_app.py` evidence library | "Descriptor & SHAP analysis report" (links to offline report file) | SAFE — refers to a file |
| `README.md` Explainability section | "SHAP analyses were generated offline for XGBoost models" | SAFE after update — offline |
| `docs/model_card.md` | "SHAP analyses used... offline artifacts" | SAFE after update |
| `reports/technical_report.md` | "SHAP plots were generated for XGBoost models" | SAFE — past tense, refers to artifacts |
| `reports/shap_interpretation.md` | Entire document is the offline SHAP analysis report | SAFE |

## Fixed language changes

### README.md

| Old | New |
|---|---|
| Title: "Explainable AI ADME-PK Platform" | "Explainable Caco-2 Permeability Screening + PK Education Platform" |
| "SHAP explainability for global and local model interpretation" | "Descriptor-based interpretation; SHAP analyses generated offline and viewable in Evidence & Limits" |
| "172 example molecules" | "221 example molecules" |
| "82 unit tests" | "179+ automated tests" |
| "Suggested F and ka derived from permeability probability" | "Scenario F and ka (educational assumptions) derived from permeability probability" |
| Screenshot paths: stale placeholder paths | Actual paths in docs/screenshots/ |

### docs/model_card.md

| Old | New |
|---|---|
| Title: "AI-PBPK / ADME Predictor" | "Explainable Caco-2 Permeability Screening + PK Education Platform" |
| "SHAP analyses are used to interpret..." | "SHAP analyses were generated offline; descriptor-based interpretation is shown at inference time" |

### reports/technical_report.md

| Old | New |
|---|---|
| Title: "AI-PBPK / ADME Predictor" | "Explainable Caco-2 Permeability Screening + PK Education Platform" |

## Remaining caveats

1. `reports/shap_interpretation.md` uses the word "SHAP" extensively. This is appropriate because it IS the SHAP analysis report. It includes appropriate caveats that SHAP values reflect model behavior, not causal biology.

2. `reports/technical_report.md` refers to SHAP generation as a past-tense action. This is accurate.

3. The word "ADME" remains in the project path name (`ai-pbpk-adme-predictor`). This is the git repository name and cannot be changed without breaking all existing links. The project is clearly scoped to Caco-2 permeability within the app and documentation.

4. Literature PK profiles are labeled "approximate teaching values" throughout the app and documentation. Users must verify values before scientific use.

## Automated scan

Run `scripts/qc_release_check.py` for a machine-checkable audit of phrase presence across the full repository.
