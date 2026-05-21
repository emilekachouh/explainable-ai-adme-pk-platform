# Outlier and Reliability Analysis

This analysis reviews molecules and descriptor regions where baseline predictions may be less reliable. It supports early discovery screening only and does not imply clinical validity.

## Extreme Descriptor Values

- molecular_weight: 20 molecules outside 1st/99th percentile range
- logp: 20 molecules outside 1st/99th percentile range
- tpsa: 26 molecules outside 1st/99th percentile range
- rotatable_bonds: 93 molecules outside 1st/99th percentile range

Extreme molecular weight, TPSA, logP, or flexibility can indicate chemistry that is less represented in the training distribution. Predictions for such molecules should be reviewed with applicability-domain output.

## Poorly Predicted Molecules

                                                                                                  canonical_smiles  observed_log_papp  predicted_log_papp  absolute_error
                                                   COc1ccc2c(c1OC)C[N+]1(Cc3ccc(Cl)cc3)CCc3cc4c(cc3C1C2)OCO4.[Cl-]          -6.231422           -4.870158        1.361264
                                                       NCCCC[C@H](N[C@@H](CCc1ccccc1)C(=O)O)C(=O)N1CCC[C@H]1C(=O)O          -7.390000           -6.304681        1.085319
COc1ccc2c(O[C@H]3C[C@H]4C(=O)NCCCCC/C=C\[C@@H]5C[C@@]5(C(=O)NS(=O)(=O)C5CC5)NC(=O)[C@@H]4C3)nc(-c3ccc(F)cc3)nc2c1C          -4.490000           -5.494409        1.004409
                                                                   Cc1ccnc2[nH]c(Cc3nc4ccc(/C(N)=N\O)cc4[nH]3)nc12          -6.699485           -5.703695        0.995790
                                               CC(C)CC(NC(=O)CN)C(=O)OC[C@@H]1O[C@H](n2cc(F)c(=O)[nH]c2=O)C[C@H]1O          -5.200674           -6.082463        0.881788
                                          CCOC(=O)c1ccc2c(C(C(=O)NS(=O)(=O)c3ccc(C)cc3OC)c3ccc4c(c3)OCO4)cn(C)c2c1          -4.699485           -5.494259        0.794775
                                                             COC(=O)c1cc(OC)c2c(c1-c1c(C(=O)OC)cc(OC)c3c1OCO3)OCO2          -4.168745           -4.958774        0.790028
                 N=C(N)NCCC[C@@H](NC(=O)[C@@H](N)Cc1ccc(O)cc1)C(=O)N[C@@H](Cc1ccccc1)C(=O)N[C@@H](Cc1ccccc1)C(N)=O          -7.760000           -6.977850        0.782151
                                                    NC(=O)[C@H]1CCCN1C(=O)[C@@H](Cc1c[nH]cn1)NC(=O)[C@H]1CCC(=O)N1          -6.831341           -6.063207        0.768134
                                                                          C/C=C/C/C=C/CCC(=O)[C@@H]1O[C@@H]1C(N)=O          -5.422406           -4.657213        0.765193

## Possible Reasons for Prediction Failure

- Chemical diversity limitations: a public benchmark may not cover all scaffolds or chemotypes.
- Dataset limitations: Caco-2 measurements vary with assay protocol, pH, transporter expression, and lab conditions.
- Experimental noise: permeability endpoints can contain measurement variability.
- Domain shift: new molecules may differ from the training chemistry even when descriptors look plausible.
- Descriptor limits: global descriptors and fingerprints may miss ionization, conformation, transporter effects, and formulation-relevant properties.