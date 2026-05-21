# Data Card: Caco-2 Wang Permeability Dataset

## Overview

| Field | Value |
|---|---|
| Name | TDC Caco2_Wang |
| Source | Therapeutics Data Commons (TDC) benchmark |
| Secondary mirror | scikit-fingerprints on Hugging Face |
| Original publication | Wang, N.-N. et al., *ADMET Evaluation in Drug Discovery. 12.* J. Chem. Inf. Model. 2016, 56, 763–786 |
| Endpoint | Experimental Caco-2 apparent permeability: log(Papp) in cm/s |
| Raw sample count | 910 rows |
| Processed sample count | 906 valid canonicalized molecules |
| File location | `data/raw/tdc_caco2_wang.csv`, `data/processed/tdc_caco2_wang_processed.csv` |

## Preprocessing Steps

1. Required SMILES and log(Papp) fields validated for presence and type.
2. SMILES canonicalized with RDKit. Molecules that fail RDKit parsing were removed (4 rows).
3. Duplicate canonical SMILES aggregated by averaging log(Papp) values.
4. Median log(Papp) threshold computed on the processed training split and used to create a binary permeability class (0 = low, 1 = high). This threshold is dataset-specific and not a regulatory or clinical cutoff.

## Endpoint Definition

The binary classification target is:
- **1 (high permeability):** log(Papp) ≥ dataset median
- **0 (low permeability):** log(Papp) < dataset median

The dataset median varies slightly depending on the train/test split. The threshold used in the deployed model is the median of the training split only to prevent data leakage.

## Class Distribution

Approximately balanced at 50/50 by construction (median-threshold split), with minor imbalance from the specific training split used.

## Feature Engineering

Descriptors computed from SMILES using RDKit:
- Molecular weight (MW)
- Wildman-Crippen logP (logP)
- Topological polar surface area (TPSA)
- Hydrogen bond donors (HBD)
- Hydrogen bond acceptors (HBA)
- Rotatable bonds
- Number of aromatic rings and heteroatom-containing rings
- Formal charge
- Fraction Csp3
- Heavy atom count
- Heteroatom count
- Molar refractivity

Morgan fingerprints (radius 2, 2048 bits) are also computed and used as supplementary features.

## Validation Strategy

Two splits are reported:
1. **Random split** (80/20): stratified by class. Standard benchmark comparison.
2. **Bemis-Murcko scaffold split** (80/20): molecules with identical core scaffolds are kept entirely within either train or test. More representative of generalization to chemically distinct new molecules.

Both splits use the same 906-molecule processed dataset.

## Known Limitations

- Caco-2 Papp values reflect in vitro passive and some active transport across a human colon adenocarcinoma cell monolayer. They do not directly reflect in vivo human intestinal absorption.
- The dataset contains compounds from diverse chemical space, but is biased toward oral small molecules. Peptides, biologics, and very large or very polar compounds are underrepresented.
- Experimental variability in Caco-2 assays (lab-to-lab, protocol-to-protocol) may introduce noise that limits ceiling performance.
- The dataset does not include efflux ratio data, so P-gp or BCRP substrates may be incorrectly classified as high-permeability.
- Scaffold split is stricter than random but is still not a prospective external validation.

## Known Biases

- Compounds in the public Caco-2 Wang dataset were selected and published by the original research group and are not a random sample of chemical space.
- FDA-approved oral drugs are likely over-represented relative to compounds that failed ADME screening.
- Highly polar compounds (peptides, biologics, charged molecules) are underrepresented.

## Intended Use

- Training a Caco-2 permeability classifier and regressor for research and educational demonstration.
- Benchmarking descriptor-based ML approaches against published Caco-2 datasets.
- Educational illustration of ADME screening workflows.

## Not Intended For

- Clinical decision-making about drug absorption.
- Regulatory submissions or IND/NDA support.
- Replacing in vitro Caco-2 assays.
- Prediction of in vivo human oral bioavailability (F), which depends on additional factors including solubility, dissolution, efflux, metabolism, and formulation.

## Citation

If you use this dataset, cite the original publication:

> Wang, N.-N., Dong, J., Deng, Y.-H., Zhu, M.-F., Wen, M., Yao, Z.-J., Lu, A.-P., Wang, J.-B., Cao, D.-S.
> "ADMET Evaluation in Drug Discovery. 12. Development of Binary Classification Models for Prediction of
> Caco-2 Cell Permeability." *J. Chem. Inf. Model.* 2016, 56(4), 763–786.

And the TDC benchmark:

> Huang, K. et al. "Therapeutics Data Commons: Machine Learning Datasets and Tasks for Drug Discovery
> and Development." *Advances in NeurIPS Track on Datasets and Benchmarks.* 2021.
