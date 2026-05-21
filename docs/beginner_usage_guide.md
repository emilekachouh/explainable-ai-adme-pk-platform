# Beginner Usage Guide

## What This App Does

This platform links molecular structure to explainable Caco-2 permeability prediction, then shows how permeability-related assumptions can influence educational oral PK simulations. It is intended for early ADME learning and hypothesis generation, not clinical PK prediction.

## How To Use

1. Select an example molecule or paste a SMILES.
2. Review descriptors such as MW, logP, TPSA, and HBD/HBA.
3. View the Caco-2 permeability prediction.
4. Check confidence and applicability domain.
5. Compare molecules to learn structure-property trends.
6. Use the Permeability to PK Impact tool to explore F and ka assumptions.
7. Download the markdown report or CSV tables.

## IV Bolus, Oral Dosing, NCA, PBPK, and IVIVE

- IV bolus means drug is placed directly into systemic circulation, so F = 1.
- Oral dosing includes absorption and first-pass effects, so the app reports CL/F rather than true CL unless F is known.
- NCA means noncompartmental analysis; it calculates exposure summaries such as AUC, AUMC, MRT, Cmax, and Tmax from concentration-time data.
- PBPK means physiologically based pharmacokinetic modeling; this app does not perform validated PBPK.
- IVIVE means in vitro-in vivo extrapolation. This app does not perform validated IVIVE.

Permeability-related assumptions can change F and ka in the educational oral simulation. They do not by themselves change true systemic clearance.

This guide explains how to run and interpret the AI-PBPK / ADME Predictor app.

## Install

From the repository root:

```bash
pip install -r requirements.txt
```

## Run the App

```bash
streamlit run app/streamlit_app.py
```

Open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## Enter a SMILES

Use the ADME Screening tab. You can choose an example molecule such as aspirin, caffeine, or ethanol, or enter a custom SMILES string.

The app validates the SMILES with RDKit, canonicalizes it, renders the 2D structure, and calculates molecular descriptors.

## Interpret the Caco-2 Permeability Prediction

The prediction is a Caco-2 permeability class relative to the median of the processed public TDC Caco2_Wang dataset.

It is not a human PK prediction. It is not a clinical absorption prediction. It is a screening estimate based on molecular structure and an in vitro permeability dataset.

## Interpret Confidence

The confidence score is based on the model probability margin:

```text
confidence = max(p, 1 - p)
```

The app also reports prediction entropy. High confidence means the model probability is far from 0.5. It does not mean clinical certainty.

## Applicability Domain

Applicability domain asks whether the input molecule is chemically similar to the training chemistry. The app compares Morgan fingerprints using nearest-neighbor Tanimoto similarity.

If the molecule is outside the domain, the app warns:

```text
This molecule is chemically dissimilar to most training compounds. Prediction reliability may be reduced.
```

## Use the PK/NCA Simulator

Open the PK/NCA Simulator tab. Choose:

- Route: IV bolus, oral, or IV infusion
- Dose
- Vd
- kel
- ka and F for oral dosing
- Infusion duration for IV infusion
- Simulation duration
- Sampling interval

The simulator displays concentration-time plots, an NCA table, warnings, and downloadable outputs.

## What Not to Overclaim

Do not claim:

- Validated human PK prediction
- Clinical dose prediction
- Safety or efficacy prediction
- Regulatory readiness
- PBPK validation

Correct description:

```text
This is an explainable AI-assisted ADME screening and educational PK/NCA simulation platform.
```
