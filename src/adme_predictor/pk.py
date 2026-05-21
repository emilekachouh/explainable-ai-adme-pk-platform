"""Educational pharmacokinetic simulation models."""

from __future__ import annotations

import numpy as np
import pandas as pd


def make_time_grid(duration: float, interval: float) -> np.ndarray:
    """Create a regular simulation time grid including time zero."""
    if duration <= 0:
        raise ValueError("Simulation duration must be positive.")
    if interval <= 0:
        raise ValueError("Sampling interval must be positive.")
    return np.arange(0.0, duration + interval * 0.5, interval, dtype=float)


def validate_positive_parameters(**parameters: float) -> None:
    """Validate that pharmacokinetic parameters are positive."""
    for name, value in parameters.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive.")


def simulate_iv_bolus(
    dose: float,
    vd: float,
    kel: float,
    times: np.ndarray,
) -> pd.DataFrame:
    """Simulate one-compartment IV bolus concentrations."""
    validate_positive_parameters(dose=dose, vd=vd, kel=kel)
    concentration = (dose / vd) * np.exp(-kel * times)
    return pd.DataFrame({"time": times.astype(float), "concentration": concentration.astype(float)})


def simulate_oral_first_order(
    dose: float,
    vd: float,
    kel: float,
    ka: float,
    bioavailability: float,
    times: np.ndarray,
    tolerance: float = 1e-6,
) -> tuple[pd.DataFrame, list[str]]:
    """Simulate oral one-compartment first-order absorption concentrations."""
    validate_positive_parameters(dose=dose, vd=vd, kel=kel, ka=ka)
    if not 0 < bioavailability <= 1:
        raise ValueError("Bioavailability F must be greater than 0 and less than or equal to 1.")

    warnings = []
    if ka <= kel:
        warnings.append(
            "ka <= kel: oral simulation may show flip-flop kinetics or parameter identifiability issues."
        )

    if abs(ka - kel) <= tolerance:
        concentration = (bioavailability * dose * ka / vd) * times * np.exp(-kel * times)
        warnings.append("ka is approximately equal to kel; used stable limiting approximation.")
    else:
        concentration = (
            (bioavailability * dose * ka) / (vd * (ka - kel))
        ) * (np.exp(-kel * times) - np.exp(-ka * times))

    concentration = np.maximum(concentration, 0.0)
    return (
        pd.DataFrame({"time": times.astype(float), "concentration": concentration.astype(float)}),
        warnings,
    )


def simulate_iv_infusion(
    dose: float,
    vd: float,
    kel: float,
    infusion_duration: float,
    times: np.ndarray,
) -> pd.DataFrame:
    """Simulate one-compartment IV infusion concentrations."""
    validate_positive_parameters(dose=dose, vd=vd, kel=kel, infusion_duration=infusion_duration)
    clearance = kel * vd
    infusion_rate = dose / infusion_duration
    c_end = (infusion_rate / clearance) * (1.0 - np.exp(-kel * infusion_duration))

    concentration = np.where(
        times <= infusion_duration,
        (infusion_rate / clearance) * (1.0 - np.exp(-kel * times)),
        c_end * np.exp(-kel * (times - infusion_duration)),
    )
    return pd.DataFrame({"time": times.astype(float), "concentration": concentration.astype(float)})


def simulate_pk_profile(
    route: str,
    dose: float,
    vd: float,
    kel: float,
    duration: float,
    interval: float,
    ka: float | None = None,
    bioavailability: float = 1.0,
    infusion_duration: float | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """Simulate a PK concentration-time profile for the selected route."""
    times = make_time_grid(duration, interval)
    route_normalized = route.lower().strip()

    if route_normalized == "iv bolus":
        return simulate_iv_bolus(dose, vd, kel, times), []
    if route_normalized == "oral":
        if ka is None:
            raise ValueError("ka is required for oral simulation.")
        return simulate_oral_first_order(dose, vd, kel, ka, bioavailability, times)
    if route_normalized == "iv infusion":
        if infusion_duration is None:
            raise ValueError("infusion_duration is required for IV infusion simulation.")
        return simulate_iv_infusion(dose, vd, kel, infusion_duration, times), []

    raise ValueError("route must be one of: IV bolus, oral, IV infusion.")
