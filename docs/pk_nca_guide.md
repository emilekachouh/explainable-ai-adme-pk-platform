# Educational PK/NCA Guide

This guide documents the educational pharmacokinetic and noncompartmental analysis module in AI-PBPK / ADME Predictor.

The PK/NCA simulator is mechanistic and instructional. It demonstrates how exposure metrics are calculated under explicit assumptions. It does not claim that Caco-2 permeability directly predicts human PK, and it must not be used for clinical, regulatory, safety, efficacy, or dose decisions.

## Simulation Models

### IV Bolus One-Compartment Model

For an IV bolus dose with first-order elimination:

```text
C(t) = Dose / Vd x exp(-kel x t)
```

Assumptions:

- Instantaneous systemic input
- One well-mixed compartment
- First-order elimination
- Constant volume of distribution

### Oral One-Compartment Model

For first-order absorption and first-order elimination:

```text
C(t) = (F x Dose x ka) / (Vd x (ka - kel)) x [exp(-kel x t) - exp(-ka x t)]
```

Assumptions:

- First-order absorption
- First-order elimination
- Fixed bioavailability `F`
- One well-mixed compartment

If `ka` is approximately equal to `kel`, the implementation uses the limiting approximation:

```text
C(t) = F x Dose x ka / Vd x t x exp(-kel x t)
```

If `ka <= kel`, the app warns that flip-flop kinetics or parameter identifiability issues may occur.

### IV Infusion Model

During infusion:

```text
C(t) = (R0 / CL) x [1 - exp(-kel x t)]
```

After infusion stops:

```text
C(t) = C_end x exp[-kel x (t - Tinf)]
```

Where:

```text
R0 = Dose / Tinf
CL = kel x Vd
```

## NCA Metrics

### AUC

Area under the concentration-time curve. The app supports:

- Linear trapezoidal AUC
- Linear-up/log-down AUC

Linear-up/log-down is commonly useful when concentrations decline exponentially in the elimination phase.

### AUMC

Area under the first moment curve:

```text
AUMC = integral time x concentration dt
```

### MRT / MBRT

Mean residence time or mean body residence time:

```text
MRT = AUMC / AUC
```

### Terminal Phase

The terminal elimination rate constant `lambda_z` is estimated from the final positive concentration points by log-linear regression.

```text
half-life = ln(2) / lambda_z
```

At least three usable terminal points are required. If fewer are available, the app warns the user.

### AUC Extrapolation

The extrapolated tail is calculated as:

```text
AUC_extrapolated = Clast / lambda_z
```

High percent extrapolated AUC suggests that the sampling duration may be insufficient.

### Clearance

For IV bolus or IV infusion:

```text
CL = Dose / AUC
```

For oral dosing:

```text
CL/F = Dose / AUC
```

Oral dosing reports apparent clearance because bioavailability affects exposure.

### Volume Terms

For IV assumptions:

```text
Vz = CL / lambda_z
Vss = Dose x AUMC / AUC^2
```

The app does not report true Vss for oral dosing unless assumptions are explicit, because oral exposure alone cannot separate clearance, bioavailability, and distribution.

## Correct Interpretation

The module teaches pharmacokinetic logic. It does not validate human exposure from molecular structure. Caco-2 permeability is one in vitro property. Human PK depends on solubility, dissolution, metabolism, transporters, plasma protein binding, blood flow, formulation, physiology, and dose.

Use this module to learn how AUC, AUMC, MRT, clearance, half-life, and extrapolation are calculated, not to make clinical or regulatory decisions.
