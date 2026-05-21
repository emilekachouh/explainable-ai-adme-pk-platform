# LinkedIn Demo Script

Hi, I built an open-source AI-assisted ADME screening platform that combines machine learning, chemistry, and pharmacokinetics education.

The app starts with a SMILES string, validates the molecule with RDKit, calculates molecular descriptors, and predicts Caco-2 permeability class using a model trained on real public experimental data.

To make the model more scientifically credible, I evaluated it with both random split and Bemis-Murcko scaffold split validation, so it is tested on chemically distinct structures.

The platform also includes SHAP explainability, confidence scoring, and applicability-domain warnings so users can see when predictions may be less reliable.

I also added an educational PK/NCA simulator that demonstrates AUC, AUMC, MRT, clearance, half-life, and extrapolated AUC from assumed parameters.

This is not clinical PK prediction. It is an explainable early discovery and educational computational pharmacology prototype.

The project reflects my interest in AI, pharmacology, translational modeling, and scientifically responsible machine learning.
