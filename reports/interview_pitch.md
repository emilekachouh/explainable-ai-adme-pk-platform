# Interview Pitch Materials

Prepared for: Emile Achou
Project: Explainable Caco-2 Permeability Screening + PK Education Platform

---

## 30-Second Pitch

"I built an open-source Caco-2 permeability screening platform that takes a molecular structure, computes physicochemical descriptors, classifies it using an XGBoost model trained on real public ADME data, and layers in confidence scoring, applicability-domain checks, and descriptor-based interpretation. It also includes a batch screening mode and an educational PK/NCA simulator that shows how absorption assumptions translate to oral exposure differences. Everything is scientifically scoped — it predicts permeability class, not clinical bioavailability — and it's deployed as a Streamlit app with 179 automated tests."

---

## 90-Second Technical Pitch

"The project starts with the TDC Caco2_Wang public benchmark — 906 experimentally measured Caco-2 permeability values. I featurise each molecule using RDKit descriptors plus Morgan fingerprints, train XGBoost and random forest classifiers, and validate on both a random split and a Bemis-Murcko scaffold split.

The scaffold split is important: it keeps structurally similar compounds out of both train and test, so I'm testing generalization to chemically distinct molecules, not just close analogs. I get AUROC 0.946 on the random split and 0.934 on the scaffold split.

On top of the model, I built three layers of scientific responsibility. First, confidence scoring — derived from prediction entropy and probability margin, so I can tell the user whether the classifier is decisive or uncertain. Second, applicability-domain checking — a Tanimoto nearest-neighbour similarity to training chemistry, so I can flag when the model is extrapolating. Third, descriptor-based interpretation — showing which physicochemical features likely drove the prediction, clearly labeled as heuristic analysis rather than live SHAP values.

For pharma usability I added batch SMILES upload so you can screen 50 compounds at once. For education I built an absorption sensitivity simulator that maps the Caco-2 probability to default F and ka assumptions, simulates one-compartment oral PK, and shows how AUC, Cmax, and CL/F shift — while explicitly keeping true systemic clearance fixed, which is the key scientific boundary.

The whole thing is tested with 179 automated tests that check both software correctness and scientific correctness: things like 'CL/F must increase when F decreases' and 'true CL must remain unchanged across scenarios.'"

---

## PI-Facing Pitch

"I designed this platform to illustrate several concepts that matter for early ADME triage: separating permeability classification from bioavailability prediction, quantifying model confidence, flagging chemical domain shift, and demonstrating how a Caco-2 signal can inform — but not determine — oral absorption assumptions in a PK simulation.

The scientific boundaries are deliberate and explicit. The ML model predicts a median-threshold Caco-2 permeability class. It does not predict human oral bioavailability F, which depends on solubility, dissolution, efflux, hepatic metabolism, and formulation factors that Caco-2 alone cannot capture. The PK module uses user-editable scenario F and ka values derived from permeability probability as a starting point, not as validated predictions.

The scaffold split validation addresses the structural analog leakage problem that inflates random-split metrics in drug-discovery ML. The applicability-domain check addresses the extrapolation problem. Both are essential for any serious ADME model.

For a group working on early ADME triage, this platform could be extended to include solubility, protein binding, or clearance endpoints following the same architecture."

---

## Microsoft / Amazon Applied Scientist Pitch

"This project demonstrates the full ML engineering stack for a biomedical classification task:

**Data engineering:** I took a raw public ADME dataset, validated and canonicalized 906 SMILES with RDKit, engineered both descriptor-based and fingerprint-based features, and implemented a median-threshold binary classification target with proper train/test split isolation.

**Model development:** Compared logistic regression, random forest, and XGBoost. Selected XGBoost based on AUROC performance. Saved artifacts as joblib files with a descriptor-based fallback for graceful deployment degradation when artifacts are unavailable.

**Validation rigor:** Implemented Bemis-Murcko scaffold split to test generalization to novel scaffolds — this is the standard more rigorous approach in cheminformatics, not just random split.

**Uncertainty quantification:** Binary entropy and probability margin confidence scoring at inference time. Not just a single threshold prediction.

**Deployment:** Streamlit Cloud deployment with cached inference, SVG rendering, health checks, and graceful fallback. Batch SMILES upload for pharma-scale screening workflows.

**Testing:** 179 automated tests. Tests cover scientific correctness (pharmacokinetic equations), software correctness (descriptor values, confidence bounds), and integration tests.

**Scientific responsibility:** Explicit labeling of educational assumptions. Separation of ML output from downstream model outputs (no predicted bioavailability, no clinical claims). This is important for responsible AI in health domains.

This is the kind of project where I had to make judgment calls about what the model should and shouldn't claim — that's a skill that matters for applied science roles at the intersection of ML and domain expertise."

---

## AI-Biotech Hiring Manager Pitch

"I built a computational ADME screening platform that a medicinal chemist or DMPK scientist could actually use for early hypothesis generation. The workflow mirrors real pharma early-discovery workflows:

1. **Structure input** — SMILES paste or batch CSV upload
2. **Descriptor profiling** — MW, logP, TPSA, HBD/HBA, Lipinski flags
3. **Permeability classification** — XGBoost Caco-2 model with probability output
4. **Trust assessment** — confidence score and applicability domain (is this molecule similar to training data?)
5. **Interpretation** — descriptor-based drivers of the prediction
6. **Follow-up guidance** — experiment recommendation based on class, confidence, and domain
7. **PK context** — educational simulation of how absorption assumptions affect AUC/Cmax/CL/F

The batch mode lets you process a plate of 50+ compounds in seconds. The report download gives you a markdown + CSV artifact you can attach to an internal discovery meeting.

The key differentiator is scientific responsibility: the platform makes specific, defensible claims about what it can and cannot predict. That's what separates a credible computational tool from an overfit demonstration notebook."

---

## Key Technical Bullets (resume-ready)

- Built and deployed an open-source Caco-2 permeability screening platform integrating RDKit descriptors (MW, logP, TPSA, HBD/HBA, Csp3, Morgan fingerprints), XGBoost classification, confidence scoring (entropy + probability margin), and Tanimoto applicability-domain analysis.
- Implemented dual-mode validation (random split: AUROC 0.946; Bemis-Murcko scaffold split: AUROC 0.934) to characterize generalization across chemically distinct molecular scaffolds.
- Developed batch SMILES screening mode for processing 50+ compounds simultaneously with per-compound prediction, confidence, applicability domain, and scenario F/ka assumptions.
- Built descriptor-based model interpretation panel and educational PK/NCA sensitivity simulator with explicit scientific guardrails separating Caco-2 permeability classification from human bioavailability/PK prediction.
- Authored 179 automated tests covering scientific correctness (CL/F invariance under true CL, AUC ratio consistency, scenario F bounds) and software correctness (descriptor calculation, confidence scoring, SMILES validation).
- Designed 26 curated literature teaching drug PK profiles and absorption sensitivity simulator with one-compartment oral PK simulation (AUC ratio, Cmax ratio, Tmax shift, CL/F ratio under fixed true CL).

---

## Key Scientific Limitations (say these proactively)

1. "The model predicts Caco-2 permeability class, not human oral bioavailability. Bioavailability depends on many factors beyond permeability."
2. "The dataset median threshold is not a clinical cutoff — it's a relative class label within this dataset."
3. "Scaffold split is stricter than random but is still not prospective external validation."
4. "The applicability-domain check flags chemical novelty, but similarity alone doesn't guarantee prediction reliability."
5. "The PK simulator uses assumed parameters — it's educational, not validated clinical prediction."
6. "SHAP values were computed offline for the trained model. The live app shows descriptor-based heuristic interpretation, not runtime SHAP."

---

## Likely Interview Questions and Answers

**Q: Why scaffold split instead of random split?**

A: In medicinal chemistry, you routinely synthesize analogs of a lead compound. Random split can put those analogs in both train and test, making the model look better than it is. Scaffold split enforces that the test set contains scaffolds not seen in training — closer to the prospective use case of predicting a new chemotype.

**Q: How do you handle molecules outside the training domain?**

A: I compute Tanimoto similarity between the query and all training set Morgan fingerprints and take the nearest-neighbor similarity. Below ~0.40, the model is extrapolating beyond well-represented chemical space. The app shows an explicit warning rather than silently returning a potentially unreliable prediction.

**Q: What's the scientific difference between CL and CL/F?**

A: CL is true systemic clearance — a drug's elimination rate divided by its plasma concentration. CL/F is apparent oral clearance — what you calculate from an oral AUC without knowing F separately. If F is 0.5, CL/F is twice the true CL. The simulator holds true CL constant and demonstrates that a change in F changes CL/F and AUC, but not CL itself — a frequently misunderstood distinction.

**Q: Why use entropy for confidence, not just probability?**

A: Probability margin (|p − 0.5|) is intuitive but equivalent to entropy for binary classification, so both are reported. Entropy makes the concept more generalizable to multi-class extensions. Also, for teaching purposes, entropy is more familiar in the information-theory framing that ML practitioners use.

**Q: What would you need to do to predict validated human oral bioavailability F?**

A: Caco-2 permeability is one of roughly five independent inputs: you'd also need aqueous solubility, dissolution rate, intestinal efflux/metabolism (P-gp, CYP3A4 in the gut wall), hepatic first-pass extraction (intrinsic clearance + protein binding + hepatic blood flow), and formulation details. The app explicitly explains this via the IVIVE explanation panel. A real F prediction would require all of these inputs and external human PK validation — a full PBPK modeling exercise, not a single classifier.

**Q: How do you ensure the app doesn't make misleading claims?**

A: Three layers. First, automated scientific correctness tests — one test literally asserts that CL/F increases when F decreases, and another asserts true CL never changes from a permeability change. Second, text scanning tests that walk all string literals in the app and fail if any implies the model predicts F or validated human PK. Third, the language claims audit document that lists every risky phrase and its current status.
