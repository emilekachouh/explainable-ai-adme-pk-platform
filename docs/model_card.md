# Model Card: AI-PBPK / ADME Predictor

## Intended Use

Explainable AI-assisted early discovery screening for Caco-2 permeability-related risk from molecular structure. The platform is also suitable for educational translational modeling demonstrations.

## Not Intended For

- Clinical decision-making
- Regulatory submission
- Human PK or PBPK claims
- Dose selection or therapeutic recommendations

## Training Dataset

TDC Caco2_Wang public benchmark with experimentally measured Caco-2 log(Papp). Processed sample size: 906 valid canonicalized molecules.

## Evaluation Strategy

The project reports both random train/test split validation and Bemis-Murcko scaffold split validation. Scaffold split is stricter because test molecules have chemically distinct core scaffolds from training molecules.

## Explainability

RDKit descriptors, Morgan fingerprints, feature importance, and SHAP analyses are used to interpret global and local model behavior. Interpretations emphasize TPSA, HBD/HBA, molecular weight, logP, flexibility, and fingerprint-defined chemical motifs.

## Applicability Domain

Predictions include nearest-neighbor Tanimoto similarity to training molecules. Chemically dissimilar inputs are flagged because reliability may be reduced outside the training chemistry.

## Limitations

- Caco-2 data are in vitro permeability measurements and do not validate clinical absorption.
- Median-threshold classification is dataset-specific.
- Experimental noise, assay protocol variation, and chemical domain shift can affect performance.
- Scaffold validation is more credible than random splitting but still not prospective external validation.

## Appropriate Use Cases

- Early ADME triage
- Molecule prioritization support
- Computational pharmacology portfolio demonstration
- Educational explanation of descriptors, permeability, and validation design