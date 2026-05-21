# SHAP Interpretation Report

This report interprets XGBoost classifier and regressor behavior for the TDC Caco2_Wang Caco-2 permeability benchmark. The analysis supports explainable early ADME screening; it does not establish clinical PK or PBPK validity.

## Scientific Interpretation

- TPSA: Higher polar surface area commonly reduces passive membrane diffusion because polar surface must be desolvated before crossing lipid-rich barriers.
- HBD/HBA: Hydrogen bond donors and acceptors can increase aqueous interaction and reduce passive permeability when excessive, consistent with Lipinski-style ADME heuristics.
- Molecular weight: Larger molecules often show lower passive permeability because size increases desolvation and conformational costs.
- logP: Moderate lipophilicity can support membrane partitioning, but very high logP may introduce solubility and assay-liability concerns.
- Flexibility: Many rotatable bonds can reduce permeability by increasing entropic cost and conformational heterogeneity.
- Fingerprint contributions: Morgan fingerprint bits capture scaffold-specific and substituent-specific motifs not represented by global descriptors.

## Scaffold-Related Chemistry

SHAP values on fingerprint bits should be interpreted as structural pattern signals, not direct mechanistic causal claims. Their importance indicates that local substructures and scaffolds contribute to model decisions.

## Passive Permeability and Oral Absorption Context

Caco-2 permeability is a useful in vitro proxy for intestinal epithelial transport, but oral absorption also depends on solubility, dissolution, metabolism, transporters, protein binding, dose, formulation, and physiology. These models should therefore support early prioritization rather than clinical prediction.