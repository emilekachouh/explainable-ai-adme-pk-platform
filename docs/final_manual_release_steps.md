# Final Manual Release Steps

These steps cannot be automated from the local repository and must be completed manually.

---

## A. Streamlit Cloud

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud) and sign in.
2. Open the app: **explainable-ai-adme-pk-platform**.
3. Click **Reboot app** to pick up the latest commit.
4. Confirm the live URL loads:
   [https://explainable-ai-adme-pk-platform-bkcqshfeecxdftn9wdbtby.streamlit.app/](https://explainable-ai-adme-pk-platform-bkcqshfeecxdftn9wdbtby.streamlit.app/)
5. Smoke-test the following sections:
   - [ ] **Single Molecule** — select Aspirin; confirm SVG renders, prediction appears, confidence and domain show correctly
   - [ ] **Batch Screening** — paste 3 SMILES; confirm summary metrics and results table populate
   - [ ] **Molecule Comparison** — select 3 molecules; confirm comparison tabs load
   - [ ] **Multi-Drug PK** — confirm 5 default drugs produce visible distinct curves
   - [ ] **PK/NCA Simulator** — select a teaching preset; confirm C-t plot and NCA table appear
   - [ ] **Absorption Sensitivity** — adjust F slider; confirm AUC ratio updates
   - [ ] **Report Download** — download markdown report; confirm it opens without error

---

## B. GitHub About section

1. Go to [https://github.com/emilekachouh/explainable-ai-adme-pk-platform](https://github.com/emilekachouh/explainable-ai-adme-pk-platform).
2. Click the gear icon next to **About**.
3. Set the **Description** to:

   > Open-source Caco-2 permeability screening and PK education platform with RDKit descriptors, ML classification, batch SMILES screening, applicability-domain checks, and educational PK/NCA sensitivity simulation.

4. Set the **Website** to:

   > https://explainable-ai-adme-pk-platform-bkcqshfeecxdftn9wdbtby.streamlit.app/

5. Save.

---

## C. GitHub topics

1. In the same **About** dialog, add these topics:

   ```
   caco2
   adme
   pharmacokinetics
   cheminformatics
   rdkit
   machine-learning
   streamlit
   drug-discovery
   dmpk
   pharma-ai
   ```

---

## D. Final app smoke test — molecules to check

| Molecule | Expected behaviour |
|---|---|
| Aspirin | High permeability prediction, in-domain, confidence ≥ medium |
| Caffeine | High permeability prediction, in-domain |
| Ibuprofen | High permeability prediction |
| Metformin | Low permeability prediction |
| Propranolol | High permeability prediction |
| Batch CSV upload (5 compounds) | All 5 processed; summary metrics populated; download CSV works |
| Multi-drug comparison (5 drugs) | Five visible curves in adjusted overlay |
| Markdown report download | File downloads, opens correctly, no "predicted F" language |

---

## E. Final scientific wording check (live app)

Confirm in the live app that:

- [ ] No page says "predicted F" or "predicted bioavailability"
- [ ] No page says "the model predicts human PK"
- [ ] The descriptor interpretation panel is labeled "Descriptor-Based Model Interpretation" (not "Explainable AI" or "SHAP")
- [ ] The scientific boundary notice appears on the home dashboard
- [ ] The absorption sensitivity disclaimer says F/ka are educational assumptions
- [ ] No page makes clinical, regulatory, dose, safety, or efficacy claims

---

## F. README badge links (optional)

Update the badge URLs in README.md once CI/CD is configured:

- Tests badge: replace with a real GitHub Actions workflow badge URL if CI is added
- PyPI badge: add only if the package is published to PyPI

Current badges are static labels; they are accurate but not dynamically linked.

---

## G. Post-release

- [ ] Share GitHub URL in your portfolio and CV
- [ ] Archive the `claude-final-polish` branch if it has been merged (it already has — branch is now `main`)
- [ ] Consider adding a GitHub Actions workflow (`ci.yml`) to auto-run `pytest` on push

---

## Status at time of final automated pass

| Item | Status |
|---|---|
| Tests | 179 / 179 passing |
| QC checks | 74 / 74 passing |
| Live URL in README | Inserted |
| CITATION.cff URLs | Inserted |
| LICENSE | MIT, Emile Achou |
| Open-source files | All present (15 / 15) |
| Screenshots | 10 curated screenshots present |
| Unsafe phrase scan | 0 violations |
| Last commit | `d427906` → updated in final release commit |
| Pushed to origin/main | Yes |
