# PK/NCA Simulation Methods

An educational pharmacokinetic simulation and noncompartmental analysis module was added to the AI-PBPK / ADME Predictor platform. The module is intended for mechanistic instruction and transparent exposure-metric calculation under user-specified assumptions. It is not a validated human PK or PBPK prediction engine.

## Compartmental Simulation

Three one-compartment profiles are supported. The IV bolus model assumes instantaneous input and first-order elimination:

```text
C(t) = Dose / Vd x exp(-kel x t)
```

The oral model assumes first-order absorption and elimination:

```text
C(t) = (F x Dose x ka) / (Vd x (ka - kel)) x [exp(-kel x t) - exp(-ka x t)]
```

When `ka` is approximately equal to `kel`, the implementation applies the limiting expression:

```text
C(t) = F x Dose x ka / Vd x t x exp(-kel x t)
```

The IV infusion model uses zero-order input during infusion followed by first-order post-infusion decline:

```text
C(t) = (R0 / CL) x [1 - exp(-kel x t)]
C(t > Tinf) = C_end x exp[-kel x (t - Tinf)]
```

where `R0 = Dose / Tinf` and `CL = kel x Vd`.

## Noncompartmental Analysis

The NCA implementation calculates linear trapezoidal AUC, linear-up/log-down AUC, AUMC, MRT/MBRT, terminal `lambda_z`, half-life, AUC extrapolated to infinity, percent extrapolated AUC, Cmax, Tmax, clearance labels, Vz, and Vss where scientifically appropriate.

For IV profiles, clearance is reported as:

```text
CL = Dose / AUC
```

For oral profiles, apparent clearance is reported:

```text
CL/F = Dose / AUC
```

True clearance and Vss are not inferred from oral profiles alone because bioavailability and systemic disposition cannot be separated without additional assumptions or data.

## Safety and Interpretation Rules

The module reports warnings for sparse terminal phases, high percent extrapolated AUC, and oral `ka <= kel`, where flip-flop kinetics or parameter identifiability issues may occur. These warnings are intended to teach the limits of NCA and compartmental assumptions.

The simulator is explicitly separated from the Caco-2 permeability ML model. The ML model estimates permeability-related screening risk from molecular structure; the PK/NCA module demonstrates exposure calculations from assumed parameters. No clinical, regulatory, safety, efficacy, or dose prediction claims are made.
