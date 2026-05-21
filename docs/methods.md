# Methods

This document describes the computational methods used in the Explainable Caco-2 Permeability Screening + PK Education Platform.

## 1. Molecular Representation

### RDKit Descriptors

All molecules are parsed and validated using RDKit (version ≥ 2023). Descriptors computed:

| Descriptor | Symbol | Notes |
|---|---|---|
| Molecular weight | MW | Wildman-Crippen |
| LogP | logP | Wildman-Crippen estimate |
| Topological polar surface area | TPSA | Ertl method |
| Hydrogen bond donors | HBD | Lipinski |
| Hydrogen bond acceptors | HBA | Lipinski |
| Rotatable bonds | RotBonds | RDKIT RDKitDescriptors |
| Aromatic ring count | ArRings | |
| Formal charge | FC | Net charge |
| Fraction Csp3 | fCsp3 | |
| Heavy atom count | HeavyAtoms | |
| Heteroatom count | Heteroatoms | |
| Molar refractivity | MR | Crippen |

### Morgan Fingerprints

Circular Morgan fingerprints (radius = 2, 2048 bits) are computed using `rdkit.Chem.AllChem.GetMorganFingerprintAsBitVect`. These are used for:
- Applicability-domain nearest-neighbour similarity
- Supplementary features in the random forest model

## 2. Classification Target

Binary class label: `1` if `log(Papp) ≥ training split median`, else `0`.
The threshold is computed on the training portion only to prevent leakage.

## 3. Model Training

### Classifiers evaluated

| Model | Library | Key hyperparameters |
|---|---|---|
| Logistic Regression | scikit-learn | C=1.0, max_iter=1000 |
| Random Forest | scikit-learn | n_estimators=200 |
| XGBoost | xgboost | n_estimators=300, learning_rate=0.05 |

The best-performing classifier is XGBoost (AUROC 0.946 random split, 0.934 scaffold split).
The deployed model is saved as `models/baseline_permeability_classifier.joblib`.

### Regressors evaluated (continuous log(Papp) prediction)

| Model | Best metrics (scaffold split) |
|---|---|
| Linear Regression | R² 0.05, MAE 0.59 |
| Random Forest Regressor | R² 0.65, MAE 0.39 |
| XGBoost Regressor | R² 0.65, MAE 0.39 |

## 4. Validation Strategy

### Random split

80/20 stratified split. Provides a standard benchmark comparison point. May overestimate generalization due to structural analogs appearing in both train and test.

### Bemis-Murcko scaffold split

Molecules are grouped by their Bemis-Murcko scaffold (core ring system + linkers). All molecules sharing a scaffold are placed entirely in either train or test. Test molecules have scaffolds not seen in training, providing a stricter estimate of generalization to chemically novel compounds.

Both splits are reported side-by-side in `reports/scaffold_split_comparison.md`.

## 5. Confidence Scoring

Prediction confidence is derived from the classifier probability output:

```
margin = |probability - 0.5|
entropy = -(p * log2(p) + (1-p) * log2(1-p))   # binary entropy
```

Categories:
- **High confidence:** margin > 0.30 (probability < 0.20 or > 0.80)
- **Medium confidence:** 0.15 < margin ≤ 0.30
- **Low confidence:** margin ≤ 0.15 (probability near 0.50)

## 6. Applicability Domain

Applicability domain is assessed using Tanimoto similarity between the query molecule's Morgan fingerprint and the nearest neighbor in the training set:

```
similarity = max(Tanimoto(query, training_mol) for training_mol in training_set)
```

Categories:
- **In domain:** similarity ≥ 0.40
- **Borderline:** 0.25 ≤ similarity < 0.40
- **Outside domain:** similarity < 0.25 (prediction reliability reduced)

## 7. Descriptor-Based Interpretation

The interpretation panel shows each descriptor value relative to rule-based thresholds known to influence passive membrane permeability:

| Descriptor | Favorable range | Basis |
|---|---|---|
| TPSA | < 140 Å² (ideally < 90 Å²) | Veber rules, Lipinski |
| logP | 0.5 – 4.5 | Lipinski, ADMET heuristics |
| HBD | ≤ 2 (ideally ≤ 1) | Lipinski |
| HBA | ≤ 8 | Lipinski |
| MW | < 500 Da | Lipinski |
| Rotatable bonds | ≤ 10 | Veber |

This is a rule-based heuristic visualization. It does not compute SHAP values at inference time.

**SHAP (SHapley Additive exPlanations)** values were computed offline for the trained XGBoost model using the `shap` library and saved as static figures in `reports/figures/shap/`. These figures can be viewed in the Evidence & Limits page if present. They are not recomputed at runtime.

## 8. Educational PK/NCA Equations

### IV bolus (one-compartment)

```
C(t) = (Dose / Vd) × exp(-kel × t)
kel = CL / Vd
```

### Oral first-order absorption (one-compartment)

```
C(t) = (F × Dose × ka) / [Vd × (ka − kel)] × [exp(-kel × t) − exp(-ka × t)]
```

F (bioavailability) and ka (absorption rate constant) are user-editable educational assumptions.
They are not predicted by the Caco-2 classifier.

### Key PK relationships

```
AUC_IV    = Dose / CL
AUC_oral  = F × Dose / CL
CL/F      = Dose / AUC_oral      (apparent oral clearance)
kel       = CL / Vd
t½        = ln(2) / lambda_z
MRT       = AUMC / AUC
Vss (IV)  = Dose × AUMC / AUC²
```

True systemic clearance (CL) is independent of oral bioavailability F and is not changed by permeability assumptions.

## 9. Absorption Sensitivity Simulator

The absorption sensitivity simulator:
1. Maps the Caco-2 probability to a default scenario F and ka using a sigmoid-like mapping.
2. Allows the user to edit F and ka independently.
3. Simulates a reference scenario (fixed F = 0.80, ka = 1.20 h⁻¹) and an adjusted scenario.
4. Computes AUC ratio, Cmax ratio, Tmax shift, and CL/F ratio.
5. Holds true CL fixed throughout.

**Scientific note:** Scenario F is an educational assumption. Human bioavailability F depends on permeability, solubility, dissolution, intestinal metabolism, hepatic first-pass, efflux transport, dose, and formulation — none of which are fully predicted from Caco-2 permeability alone.

## 10. Report Generation

Reports are generated in memory using Python string formatting. No external LaTeX or document processing is required. Reports include:
- Molecule name, canonical SMILES, category
- Descriptor table
- Caco-2 prediction, probability, confidence, entropy
- Applicability domain result
- Descriptor driver summary (rule-based interpretation)
- Scenario F/ka assumptions
- AUC/Cmax/Tmax/CL/F ratio table
- Scientific limitations block
- Reference sources

Reports are delivered as downloadable markdown (`.md`) or CSV (`.csv`) via Streamlit `st.download_button`.
