"""Noncompartmental analysis utilities for educational PK profiles."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def linear_trapezoidal_auc(time: np.ndarray, concentration: np.ndarray) -> float:
    """Calculate AUC using the linear trapezoidal rule."""
    return float(np.trapezoid(concentration, time))


def linear_trapezoidal_aumc(time: np.ndarray, concentration: np.ndarray) -> float:
    """Calculate AUMC using linear trapezoids on time x concentration."""
    return float(np.trapezoid(time * concentration, time))


def linear_up_log_down_auc(time: np.ndarray, concentration: np.ndarray) -> float:
    """Calculate AUC using linear-up/log-down trapezoids."""
    auc = 0.0
    for index in range(1, len(time)):
        t0, t1 = time[index - 1], time[index]
        c0, c1 = concentration[index - 1], concentration[index]
        dt = t1 - t0
        if c1 < c0 and c0 > 0 and c1 > 0:
            auc += dt * (c0 - c1) / math.log(c0 / c1)
        else:
            auc += dt * (c0 + c1) / 2.0
    return float(auc)


def estimate_lambda_z(
    time: np.ndarray,
    concentration: np.ndarray,
    n_points: int = 3,
) -> tuple[float, float, list[str]]:
    """Estimate terminal elimination slope from the last positive concentrations."""
    warnings = []
    positive_mask = concentration > 0
    terminal_time = time[positive_mask]
    terminal_conc = concentration[positive_mask]

    if len(terminal_time) < n_points:
        warnings.append("Terminal phase has fewer than 3 usable positive points.")
        return float("nan"), float("nan"), warnings

    terminal_time = terminal_time[-n_points:]
    terminal_conc = terminal_conc[-n_points:]
    slope, intercept = np.polyfit(terminal_time, np.log(terminal_conc), 1)
    lambda_z = -float(slope)

    if lambda_z <= 0:
        warnings.append("Terminal lambda_z could not be estimated as a positive slope.")
        return float("nan"), float("nan"), warnings

    predicted = slope * terminal_time + intercept
    ss_res = float(np.sum((np.log(terminal_conc) - predicted) ** 2))
    ss_tot = float(np.sum((np.log(terminal_conc) - np.mean(np.log(terminal_conc))) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot else 1.0
    return lambda_z, float(r_squared), warnings


def calculate_nca(
    profile: pd.DataFrame,
    dose: float,
    route: str,
    method: str = "linear_up_log_down",
    n_terminal_points: int = 3,
    bioavailability: float | None = None,
) -> tuple[dict[str, float | str], list[str]]:
    """Calculate educational NCA metrics from a concentration-time profile."""
    if profile.empty:
        raise ValueError("Profile cannot be empty.")
    if dose <= 0:
        raise ValueError("Dose must be positive.")

    time = profile["time"].to_numpy(dtype=float)
    concentration = profile["concentration"].to_numpy(dtype=float)
    if np.any(np.diff(time) < 0):
        raise ValueError("Time values must be sorted.")

    warnings = []
    auc_last = (
        linear_up_log_down_auc(time, concentration)
        if method == "linear_up_log_down"
        else linear_trapezoidal_auc(time, concentration)
    )
    aumc_last = linear_trapezoidal_aumc(time, concentration)
    lambda_z, lambda_z_r2, terminal_warnings = estimate_lambda_z(
        time,
        concentration,
        n_points=n_terminal_points,
    )
    warnings.extend(terminal_warnings)

    last_positive_indices = np.where(concentration > 0)[0]
    if len(last_positive_indices) == 0:
        raise ValueError("At least one positive concentration is required.")
    last_index = int(last_positive_indices[-1])
    c_last = float(concentration[last_index])
    t_last = float(time[last_index])

    if math.isfinite(lambda_z):
        auc_extrapolated = c_last / lambda_z
        aumc_extrapolated = (c_last * t_last / lambda_z) + (c_last / lambda_z**2)
    else:
        auc_extrapolated = float("nan")
        aumc_extrapolated = float("nan")

    auc_inf = auc_last + auc_extrapolated if math.isfinite(auc_extrapolated) else float("nan")
    aumc_inf = (
        aumc_last + aumc_extrapolated if math.isfinite(aumc_extrapolated) else float("nan")
    )
    mrt = aumc_inf / auc_inf if auc_inf and math.isfinite(auc_inf) else float("nan")
    half_life = math.log(2) / lambda_z if math.isfinite(lambda_z) else float("nan")
    percent_auc_extrapolated = (
        100.0 * auc_extrapolated / auc_inf
        if auc_inf and math.isfinite(auc_inf)
        else float("nan")
    )

    if math.isfinite(percent_auc_extrapolated) and percent_auc_extrapolated > 20:
        warnings.append(
            "Percent extrapolated AUC is high; sampling duration may be insufficient."
        )

    cmax = float(np.max(concentration))
    tmax = float(time[int(np.argmax(concentration))])
    route_normalized = route.lower().strip()

    summary: dict[str, float | str] = {
        "route": route,
        "auc_last": float(auc_last),
        "auc_inf": float(auc_inf),
        "aumc_last": float(aumc_last),
        "aumc_inf": float(aumc_inf),
        "mrt": float(mrt),
        "lambda_z": float(lambda_z),
        "lambda_z_r2": float(lambda_z_r2),
        "half_life": float(half_life),
        "auc_extrapolated": float(auc_extrapolated),
        "percent_auc_extrapolated": float(percent_auc_extrapolated),
        "cmax": cmax,
        "tmax": tmax,
    }

    if route_normalized in {"iv bolus", "iv infusion"}:
        clearance = dose / auc_inf if auc_inf and math.isfinite(auc_inf) else float("nan")
        summary["clearance_label"] = "CL"
        summary["clearance"] = float(clearance)
        summary["vz"] = float(clearance / lambda_z) if math.isfinite(lambda_z) else float("nan")
        summary["vss"] = float(dose * aumc_inf / auc_inf**2) if auc_inf else float("nan")
    elif route_normalized == "oral":
        apparent_clearance = dose / auc_inf if auc_inf and math.isfinite(auc_inf) else float("nan")
        summary["clearance_label"] = "CL/F"
        summary["clearance"] = float(apparent_clearance)
        summary["vz"] = float("nan")
        summary["vss"] = float("nan")
        if bioavailability is None:
            warnings.append("Oral route reports apparent clearance CL/F, not true CL.")
            warnings.append("True Vss is not reported for oral dosing unless F and assumptions are explicit.")
        else:
            warnings.append("Oral route: CL/F is reported; true CL depends on assumed F.")
    else:
        raise ValueError("route must be one of: IV bolus, oral, IV infusion.")

    return summary, warnings
