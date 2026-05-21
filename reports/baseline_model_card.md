# Baseline Caco-2 Permeability Model

This is an early discovery ADME screening prototype, not a clinical prediction tool.

Dataset: TDC Caco2_Wang public benchmark.
Endpoint: experimental Caco-2 log(Papp).
Classification target: high vs low permeability using the processed dataset median.
Regression target: continuous log(Papp).
Selected classifier: xgboost.

Scientific caveats:
- Caco-2 is an in vitro permeability proxy and does not prove human absorption.
- The median class threshold is data-derived and should not be treated as a clinical cutoff.
- Random train/test splitting can overestimate generalization to new chemical scaffolds.
- Descriptor and fingerprint baselines are useful controls, not final validated models.

Interpretability note: SHAP summary saved for the best tree-based classifier.