# Project Architecture

## End-to-End Pipeline

```text
SMILES input
  -> RDKit validation and canonicalization
  -> RDKit descriptors and Morgan fingerprints
  -> Caco-2 permeability ML model
  -> confidence estimation
  -> applicability-domain check
  -> SHAP explanation
  -> ADME interpretation
  -> downloadable report
```

## Optional Educational PK/NCA Simulator

```text
Assumed PK parameters
  -> one-compartment simulation
  -> concentration-time profile
  -> NCA calculations
  -> warnings and assumptions
  -> plots, tables, and downloadable outputs
```

## Module Map

- `features.py`: SMILES validation, descriptors, Lipinski flags, Morgan fingerprints
- `data.py`: public dataset loading and preprocessing
- `modeling.py`: baseline model training and prediction
- `evaluation.py`: classification and regression metrics
- `scaffold.py`: Bemis-Murcko scaffold split validation
- `interpretability.py`: SHAP outputs
- `uncertainty.py`: confidence and entropy
- `applicability.py`: nearest-neighbor domain analysis
- `pk.py`: educational PK simulation
- `nca.py`: noncompartmental calculations
- `pk_visualization.py`: PK plots
- `reporting.py`: reports, figures, molecule rendering

## Scientific Boundary

The Caco-2 model estimates permeability-related screening risk. The PK/NCA simulator demonstrates exposure calculations from assumed parameters. These are connected educationally, not as a validated clinical prediction chain.
