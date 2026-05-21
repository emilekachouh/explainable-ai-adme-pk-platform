# Data and Modeling Policy

## Data Sources

Final model training must use real public ADME/PK datasets with experimentally measured endpoints. Synthetic or fake data must not be used for final model training or final reported results.

Temporary toy molecules are allowed only for code tests, app validation, and UI demonstration.

Acceptable public sources include:

- Therapeutics Data Commons
- MoleculeNet
- ChEMBL-derived datasets
- PubChem assay datasets
- Published public ADME benchmark datasets

Each dataset must document:

- Source
- Endpoint
- Units
- Sample size
- License or usage note, when available
- Preprocessing steps
- Limitations

## PK Modeling Scope

Future PK modeling work should align with pharmacokinetics course concepts, including:

- AUC
- AUMC
- MBRT/MRT = AUMC/AUC
- CL = Dose/AUC for IV when appropriate
- Vss = Dose x AUMC / AUC^2 for IV NCA when appropriate
- Linear-up/log-down trapezoidal rule
- Terminal phase estimation
- Percentage extrapolated AUC
- Difference between NCA and compartmental modeling

## Claims

The platform must not make clinical claims. It should be presented as early discovery decision support and educational translational modeling.
