"""Safe fold-change and ratio metrics for multi-drug PK comparison.

All ratios follow the convention: drug_value / reference_value.
Handles zero denominators, NaN, None, and non-finite floats gracefully.
"""

from __future__ import annotations

import math

import pandas as pd


def safe_ratio(
    numerator: float | None,
    denominator: float | None,
    fallback: float = float("nan"),
) -> float:
    """Return numerator / denominator safely.

    Returns `fallback` when denominator is zero, None, NaN, or non-finite.
    """
    if numerator is None or denominator is None:
        return fallback
    try:
        n = float(numerator)
        d = float(denominator)
    except (TypeError, ValueError):
        return fallback
    if not math.isfinite(n) or not math.isfinite(d) or d == 0.0:
        return fallback
    return n / d


def safe_diff(
    value: float | None,
    reference: float | None,
    fallback: float = float("nan"),
) -> float:
    """Return value - reference safely."""
    if value is None or reference is None:
        return fallback
    try:
        v = float(value)
        r = float(reference)
    except (TypeError, ValueError):
        return fallback
    if not math.isfinite(v) or not math.isfinite(r):
        return fallback
    return v - r


def compute_drug_ratios(
    metrics: pd.DataFrame,
    reference_molecule: str,
) -> pd.DataFrame:
    """Add fold-change columns to a multi-drug metrics DataFrame.

    Parameters
    ----------
    metrics:
        Must contain columns: molecule, auc, cmax, tmax, clf.
        Optional: f, ka, prob.
    reference_molecule:
        Name of the reference drug (must match a row in metrics["molecule"]).

    Returns
    -------
    Copy of metrics with added ratio/shift columns.
    """
    out = metrics.copy()
    ref_rows = out[out["molecule"] == reference_molecule]
    if ref_rows.empty:
        for col in ["auc_ratio", "cmax_ratio", "tmax_shift", "clf_ratio", "f_ratio", "ka_ratio"]:
            out[col] = float("nan")
        return out

    ref = ref_rows.iloc[0]
    out["auc_ratio"] = [safe_ratio(r, ref.get("auc")) for r in out.get("auc", [])]
    out["cmax_ratio"] = [safe_ratio(r, ref.get("cmax")) for r in out.get("cmax", [])]
    out["tmax_shift"] = [safe_diff(r, ref.get("tmax")) for r in out.get("tmax", [])]
    out["clf_ratio"] = [safe_ratio(r, ref.get("clf")) for r in out.get("clf", [])]
    if "f" in out.columns:
        out["f_ratio"] = [safe_ratio(r, ref.get("f")) for r in out["f"]]
    if "ka" in out.columns:
        out["ka_ratio"] = [safe_ratio(r, ref.get("ka")) for r in out["ka"]]
    if "prob" in out.columns:
        out["prob_diff"] = [safe_diff(r, ref.get("prob")) for r in out["prob"]]

    return out


def interpret_ratio(
    metric: str,
    ratio: float,
    drug_name: str,
    reference_name: str,
) -> dict[str, str]:
    """Return beginner and PhD interpretation for a single ratio metric.

    Parameters
    ----------
    metric : str
        One of: 'auc', 'cmax', 'tmax', 'clf'.
    ratio : float
        Computed ratio (drug / reference).
    drug_name, reference_name : str
        Names used in the interpretation text.
    """
    if not math.isfinite(ratio):
        msg = f"Ratio could not be computed for {drug_name} vs {reference_name} (zero denominator or missing data)."
        return {"beginner": msg, "phd": msg}

    direction = "higher" if ratio > 1 else "lower"
    fold = f"{ratio:.2f}×"

    if metric == "auc":
        beginner = (
            f"{drug_name} has {fold} simulated AUC compared to {reference_name}. "
            f"This means {direction} total drug exposure under these educational assumptions."
        )
        phd = (
            f"AUC ratio = {ratio:.3f}. Under AUC_oral = F × Dose / CL with fixed dose and true CL, "
            f"this difference is driven by {'higher' if ratio > 1 else 'lower'} assigned F. "
            "True CL is unchanged by design."
        )
    elif metric == "cmax":
        beginner = (
            f"{drug_name} has {fold} simulated Cmax compared to {reference_name}. "
            f"This means a {'higher' if ratio > 1 else 'lower'} peak concentration under these assumptions."
        )
        phd = (
            f"Cmax ratio = {ratio:.3f}. Cmax is jointly influenced by F and ka. "
            "Higher ka can increase Cmax and shift Tmax earlier even without changing AUC."
        )
    elif metric == "clf":
        beginner = (
            f"{drug_name} has {fold} apparent oral clearance (CL/F) compared to {reference_name}. "
            "Higher apparent clearance means lower simulated AUC."
        )
        phd = (
            f"CL/F ratio = {ratio:.3f}. Because CL/F = Dose / AUC, the CL/F ratio is the inverse of the "
            "AUC ratio when dose is fixed. Higher apparent clearance does not indicate higher intrinsic CL."
        )
    else:
        beginner = f"{metric} ratio vs {reference_name}: {fold}."
        phd = beginner

    return {"beginner": beginner, "phd": phd}


def multi_drug_interpretation(
    metrics: pd.DataFrame,
    reference_molecule: str,
) -> dict[str, str]:
    """Generate aggregate beginner and PhD interpretation for multi-drug comparison."""
    if metrics.empty:
        return {"beginner": "", "phd": ""}

    # Find extremes
    auc_col = "auc_ratio" if "auc_ratio" in metrics.columns else "auc"
    cmax_col = "cmax_ratio" if "cmax_ratio" in metrics.columns else "cmax"
    clf_col = "clf_ratio" if "clf_ratio" in metrics.columns else "clf"

    finite_auc = metrics[metrics[auc_col].apply(lambda v: math.isfinite(float(v)) if v is not None else False)]
    if finite_auc.empty:
        return {"beginner": "No finite AUC ratios computed.", "phd": "See parameter table."}

    max_auc_row = finite_auc.sort_values(auc_col, ascending=False).iloc[0]
    min_auc_row = finite_auc.sort_values(auc_col, ascending=True).iloc[0]

    beginner = (
        f"Compared with {reference_molecule}, {max_auc_row['molecule']} has the highest simulated AUC ratio "
        f"({max_auc_row[auc_col]:.2f}×) and {min_auc_row['molecule']} has the lowest "
        f"({min_auc_row[auc_col]:.2f}×). "
        "Drugs with higher assumed F have higher simulated AUC because more of the oral dose reaches "
        "systemic circulation. Faster ka shifts the curve earlier and may increase Cmax. "
        "True systemic CL is the same for all drugs in educational default mode."
    )
    phd = (
        "Under fixed dose, Vd, and true CL in educational default mode, inter-drug differences in AUC are "
        "driven by F according to AUC_oral = F × Dose / CL. Differences in ka alter the absorption phase "
        "and influence Cmax and Tmax. Apparent CL/F = Dose / AUC varies inversely with AUC and should not "
        "be interpreted as intrinsic clearance change. "
        f"Reference: {reference_molecule}. "
        f"Highest AUC ratio: {max_auc_row['molecule']} ({max_auc_row[auc_col]:.3f}). "
        f"Lowest AUC ratio: {min_auc_row['molecule']} ({min_auc_row[auc_col]:.3f})."
    )
    return {"beginner": beginner, "phd": phd}
