# Final Quality Audit

## What the App Can Do

- Validate and canonicalize SMILES
- Render 2D molecular structures
- Calculate RDKit molecular descriptors and ADME flags
- Predict Caco-2 permeability class using a public-data baseline model
- Report prediction confidence and entropy
- Assess applicability domain using chemical similarity
- Display SHAP explainability assets
- Generate downloadable ADME reports
- Simulate educational PK profiles
- Calculate NCA metrics and warnings
- Generate downloadable PK/NCA outputs

## What the App Cannot Do

- Predict validated human PK
- Replace PBPK modeling
- Predict clinical absorption, safety, efficacy, or dose
- Support regulatory decisions
- Guarantee reliability outside training chemistry
- Infer true oral clearance or Vss without assumptions

## Scientific Risks

- Caco-2 assay variability and experimental noise
- Dataset-specific median threshold
- Chemical domain shift
- Scaffold split still not equivalent to prospective validation
- Fingerprint SHAP values may be difficult to map to mechanistic chemistry
- PK/NCA parameters are assumed by the user

## Software Risks

- Saved model artifacts may be environment-specific
- Large generated files may not be ideal for GitHub release
- Streamlit layout should be checked with screenshots before release
- Additional dependency pinning may be needed for reproducibility

## Reviewer / Interviewer Talking Points

- Real public dataset, not synthetic model data
- Scaffold split included to address chemical leakage
- SHAP, confidence, and applicability domain added for responsible AI behavior
- Clear separation between ML permeability screening and educational PK/NCA simulation
- Unit-tested modular Python design

## PI Talking Points

- Scientifically cautious interpretation
- Caco-2 endpoint limitations documented
- NCA equations and assumptions made explicit
- No clinical or regulatory claims
- Future path can include external ADME datasets and validated PK endpoints

## Future Validation Path Toward Human PK

1. Add public experimental human or animal PK datasets with documented dose, route, units, and assay conditions.
2. Separate training by endpoint and species.
3. Use scaffold and external validation.
4. Add uncertainty calibration and conformal intervals.
5. Compare against mechanistic PBPK or NCA baselines.
6. Document model domain, failure modes, and endpoint-specific limitations.
