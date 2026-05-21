"""Streamlit application for the Explainable AI ADME-PK Platform."""

from __future__ import annotations

import sys
import random
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from adme_predictor.applicability import assess_applicability_domain  # noqa: E402
from adme_predictor.app_health import check_app_health, health_icon  # noqa: E402
from adme_predictor.demo_model import (  # noqa: E402
    prediction_confidence,
    predict_permeability_class_resilient,
)
from adme_predictor.education import (  # noqa: E402
    F_EDUCATIONAL_NOTE,
    F_MISMATCH_THRESHOLD,
    F_SCENARIO_DISCLAIMER,
    HOW_TO_USE_STEPS,
    IVIVE_EXPLANATION,
    IV_ORAL_EXPLANATION,
    MULTI_DRUG_COMPARISON_DISCLAIMER,
    PK_EQUATIONS_TEXT,
    REFERENCES,
    REVIEWER_SUMMARY,
    SCIENTIFIC_BOUNDARIES,
    WHAT_THIS_APP_DOES,
    build_downloadable_report,
    build_multi_drug_comparison_report,
    comparison_interpretations,
    experiment_recommendation,
    explanation_for_level,
    load_observed_pk_curve,
    multi_drug_pk_comparison,
    permeability_to_pk_assumptions,
    pk_impact_interpretations,
    pk_impact_profiles,
    pk_impact_table,
)
from adme_predictor.drug_pk_profiles import DRUG_PK_PROFILES  # noqa: E402
from adme_predictor.example_molecules import (  # noqa: E402
    EXAMPLE_CATEGORIES,
    EXAMPLE_MOLECULE_COUNT,
    EXAMPLE_MOLECULES,
)
from adme_predictor.features import (  # noqa: E402
    build_feature_vector,
    calculate_descriptors,
    calculate_lipinski_flags,
    canonicalize_smiles,
)
from adme_predictor.nca import calculate_nca  # noqa: E402
from adme_predictor.pk import simulate_pk_profile  # noqa: E402
from adme_predictor.pk_visualization import (  # noqa: E402
    plot_concentration_time,
    plot_semilog_concentration_time,
)
from adme_predictor.reporting import render_molecule_svg, svg_to_html_page  # noqa: E402


PK_PRESETS = {
    "IV bolus high clearance compound": {
        "route": "IV bolus",
        "dose": 100.0,
        "vd": 12.0,
        "kel": 0.55,
        "ka": 1.0,
        "bioavailability": 1.0,
        "infusion_duration": 2.0,
        "duration": 12.0,
        "interval": 0.25,
        "n_terminal_points": 3,
        "method": "linear_up_log_down",
        "note": "Fast elimination creates a steep terminal slope and lower exposure for the same dose.",
    },
    "IV bolus low clearance compound": {
        "route": "IV bolus",
        "dose": 100.0,
        "vd": 35.0,
        "kel": 0.035,
        "ka": 1.0,
        "bioavailability": 1.0,
        "infusion_duration": 2.0,
        "duration": 96.0,
        "interval": 4.0,
        "n_terminal_points": 4,
        "method": "linear",
        "note": "Slow elimination produces prolonged exposure and a long apparent half-life.",
    },
    "Oral fast absorption": {
        "route": "oral",
        "dose": 100.0,
        "vd": 40.0,
        "kel": 0.15,
        "ka": 1.2,
        "bioavailability": 0.80,
        "infusion_duration": 2.0,
        "duration": 48.0,
        "interval": 0.5,
        "n_terminal_points": 3,
        "method": "linear_up_log_down",
        "note": "Absorption is faster than elimination, so Tmax occurs early.",
    },
    "Oral slow absorption": {
        "route": "oral",
        "dose": 100.0,
        "vd": 25.0,
        "kel": 0.10,
        "ka": 0.22,
        "bioavailability": 0.65,
        "infusion_duration": 2.0,
        "duration": 48.0,
        "interval": 1.0,
        "n_terminal_points": 4,
        "method": "linear_up_log_down",
        "note": "Slower absorption delays Tmax and flattens the early curve.",
    },
    "Flip-flop kinetics example": {
        "route": "oral",
        "dose": 100.0,
        "vd": 25.0,
        "kel": 0.22,
        "ka": 0.045,
        "bioavailability": 0.70,
        "infusion_duration": 2.0,
        "duration": 96.0,
        "interval": 2.0,
        "n_terminal_points": 5,
        "method": "linear_up_log_down",
        "note": "ka is lower than kel, so the terminal slope can reflect absorption rather than elimination.",
    },
    "Insufficient sampling example": {
        "route": "oral",
        "dose": 100.0,
        "vd": 25.0,
        "kel": 0.12,
        "ka": 1.2,
        "bioavailability": 0.70,
        "infusion_duration": 2.0,
        "duration": 4.0,
        "interval": 1.0,
        "n_terminal_points": 3,
        "method": "linear_up_log_down",
        "note": "Short follow-up can make terminal extrapolation unreliable.",
    },
}


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2.25rem;
            max-width: 1280px;
        }
        .hero {
            border: 1px solid #d9e2ef;
            border-radius: 8px;
            padding: 1.55rem 1.65rem;
            background: linear-gradient(135deg, #ffffff 0%, #f5f8fc 100%);
            margin-bottom: 0.85rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
        }
        .hero h1 {
            font-size: 2.35rem;
            line-height: 1.1;
            margin-bottom: 0.45rem;
            letter-spacing: 0;
            color: #0f172a;
        }
        .hero p {
            color: #475569;
            font-size: 1.04rem;
            margin: 0;
            max-width: 980px;
        }
        .workflow-strip {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 0.65rem;
            margin: 0.85rem 0 0.9rem 0;
        }
        .workflow-card, .premium-card, .metric-card, .status-pill {
            border: 1px solid #e2e8f0;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.045);
        }
        .workflow-card {
            min-height: 112px;
            padding: 0.8rem 0.82rem;
        }
        .workflow-card .eyebrow {
            color: #2563eb;
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.3rem;
        }
        .workflow-card .title {
            color: #0f172a;
            font-size: 0.95rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.25rem;
        }
        .workflow-card .body {
            color: #64748b;
            font-size: 0.82rem;
            line-height: 1.32;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.65rem;
            margin: 0.6rem 0 1rem 0;
        }
        .metric-card {
            min-height: 92px;
            padding: 0.82rem 0.88rem;
        }
        .metric-card .value {
            color: #0f172a;
            font-size: 1.28rem;
            font-weight: 800;
            line-height: 1.15;
            white-space: normal;
            overflow-wrap: anywhere;
        }
        .metric-card .label {
            color: #64748b;
            font-size: 0.83rem;
            line-height: 1.25;
            margin-top: 0.25rem;
        }
        .premium-card {
            padding: 0.95rem 1rem;
            margin: 0.25rem 0 0.75rem 0;
        }
        .premium-card h3 {
            color: #0f172a;
            font-size: 1.02rem;
            margin: 0 0 0.35rem 0;
        }
        .premium-card p, .premium-card li {
            color: #475569;
            font-size: 0.92rem;
            line-height: 1.45;
        }
        .status-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0.4rem 0 0.8rem 0;
        }
        .status-pill {
            padding: 0.42rem 0.58rem;
            color: #334155;
            font-size: 0.84rem;
            font-weight: 650;
        }
        .status-good { border-color: #bbf7d0; background: #f0fdf4; color: #166534; }
        .status-warn { border-color: #fde68a; background: #fffbeb; color: #92400e; }
        .status-risk { border-color: #fecaca; background: #fef2f2; color: #991b1b; }
        .prob-track {
            height: 18px;
            border-radius: 999px;
            background: linear-gradient(90deg, #dbeafe 0%, #93c5fd 45%, #2563eb 100%);
            border: 1px solid #bfdbfe;
            margin: 0.45rem 0 0.15rem 0;
        }
        .prob-labels {
            display: flex;
            justify-content: space-between;
            color: #64748b;
            font-size: 0.82rem;
            margin-bottom: 0.8rem;
        }
        .section-note {
            border-left: 4px solid #2563eb;
            padding: 0.65rem 0.8rem;
            background: #eff6ff;
            color: #1e3a8a;
            border-radius: 4px;
            margin: 0.5rem 0 0.85rem 0;
        }
        .small-muted {
            color: #64748b;
            font-size: 0.9rem;
        }
        div[data-testid="stMetric"] {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0.7rem 0.8rem;
            background: #ffffff;
            min-height: 88px;
        }
        div[data-testid="stMetricLabel"] {
            color: #475569;
            white-space: normal;
            overflow-wrap: anywhere;
        }
        div[data-testid="stMetricValue"] {
            white-space: normal;
            overflow-wrap: anywhere;
            font-size: 1.25rem;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 0.85rem;
        }
        @media (max-width: 1100px) {
            .workflow-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 720px) {
            .workflow-strip, .metric-grid { grid-template-columns: 1fr; }
        }
        .decision-summary {
            border: 2px solid #2563eb;
            border-radius: 10px;
            padding: 1.05rem 1.15rem;
            background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
            margin: 0.65rem 0 0.9rem 0;
            box-shadow: 0 4px 16px rgba(37, 99, 235, 0.08);
        }
        .decision-summary h3 {
            color: #1e40af;
            font-size: 1.04rem;
            margin: 0 0 0.45rem 0;
            font-weight: 700;
        }
        .ds-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-bottom: 0.4rem;
        }
        .ds-badge {
            border-radius: 6px;
            padding: 0.26rem 0.52rem;
            font-size: 0.83rem;
            font-weight: 600;
            border: 1px solid #bfdbfe;
            background: #dbeafe;
            color: #1e40af;
            white-space: nowrap;
        }
        .ds-badge.high { background: #dcfce7; border-color: #bbf7d0; color: #166534; }
        .ds-badge.low  { background: #fee2e2; border-color: #fecaca; color: #991b1b; }
        .ds-badge.warn { background: #fffbeb; border-color: #fde68a; color: #92400e; }
        .formula-callout {
            border: 1px solid #c7d2fe;
            border-radius: 8px;
            background: #eef2ff;
            padding: 0.75rem 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.88rem;
            color: #312e81;
            margin: 0.45rem 0 0.75rem 0;
            line-height: 1.65;
        }
        .three-step {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.65rem;
            margin: 0.55rem 0 0.85rem 0;
        }
        .step-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background: #ffffff;
            padding: 0.7rem 0.85rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(15,23,42,0.04);
        }
        .step-num {
            font-size: 1.35rem;
            font-weight: 800;
            color: #2563eb;
            line-height: 1;
        }
        .step-arrow {
            font-size: 1.2rem;
            color: #93c5fd;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .step-title {
            font-size: 0.91rem;
            font-weight: 700;
            color: #0f172a;
            margin: 0.2rem 0 0.15rem 0;
        }
        .step-body {
            font-size: 0.81rem;
            color: #64748b;
            line-height: 1.3;
        }
        .report-preview {
            border: 1px solid #d1fae5;
            border-radius: 8px;
            background: #f0fdf4;
            padding: 0.85rem 1rem;
            margin: 0.5rem 0 0.65rem 0;
        }
        .report-preview h4 {
            color: #166534;
            font-size: 0.97rem;
            margin: 0 0 0.45rem 0;
        }
        .report-preview ul {
            margin: 0;
            padding-left: 1.25rem;
            color: #166534;
            font-size: 0.87rem;
            line-height: 1.65;
        }
        .big-metric {
            border: 2px solid #2563eb;
            border-radius: 10px;
            padding: 0.85rem 1rem;
            background: #eff6ff;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .big-metric .bm-value {
            font-size: 1.55rem;
            font-weight: 800;
            color: #1e40af;
            line-height: 1.1;
        }
        .big-metric .bm-label {
            font-size: 0.83rem;
            color: #3b82f6;
            margin-top: 0.2rem;
        }
        .compare-section-header {
            font-size: 1.0rem;
            font-weight: 700;
            color: #0f172a;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.35rem;
            margin: 1.0rem 0 0.55rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _example_table() -> pd.DataFrame:
    rows = []
    for entry in EXAMPLE_MOLECULES:
        rows.append(
            {
                "label": f"{entry['name']} - {entry['category']}",
                "name": entry["name"],
                "category": entry["category"],
                "smiles": entry["smiles"],
                "teaching_note": entry["teaching_note"],
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def _analyze_smiles(smiles: str) -> dict[str, object]:
    descriptors = calculate_descriptors(smiles)
    return {
        "canonical_smiles": canonicalize_smiles(smiles),
        "descriptors": descriptors,
        "flags": calculate_lipinski_flags(descriptors),
        "feature_vector": build_feature_vector(smiles),
    }


@st.cache_data(show_spinner=False)
def _cached_molecule_svg(smiles: str) -> str | None:
    try:
        return render_molecule_svg(smiles)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def _cached_prediction(smiles: str) -> dict[str, object]:
    return predict_permeability_class_resilient(smiles)


@st.cache_data(show_spinner=False)
def _cached_applicability(smiles: str) -> dict[str, object] | None:
    try:
        return assess_applicability_domain(smiles)
    except Exception:
        return None


def _safe_float(value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if numeric != numeric:
        return "Not reported"
    return f"{numeric:.4g}"


def _metric_number(value: object, digits: int = 2) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "Not available"


def _html_card(title: str, body: str) -> str:
    return f'<div class="premium-card"><h3>{title}</h3><p>{body}</p></div>'


def _hero_metric(value: str, label: str) -> str:
    return f'<div class="metric-card"><div class="value">{value}</div><div class="label">{label}</div></div>'


def _workflow_card(eyebrow: str, title: str, body: str) -> str:
    return (
        '<div class="workflow-card">'
        f'<div class="eyebrow">{eyebrow}</div>'
        f'<div class="title">{title}</div>'
        f'<div class="body">{body}</div>'
        '</div>'
    )


def _status_pill(text: str, level: str = "good") -> str:
    return f'<span class="status-pill status-{level}">{text}</span>'


def _descriptor_status(descriptors: dict[str, object], applicability: dict[str, object] | None) -> str:
    pills = []
    logp = float(descriptors["logp"])
    tpsa = float(descriptors["tpsa"])
    mw = float(descriptors["molecular_weight"])
    rotatable = int(descriptors["rotatable_bonds"])
    pills.append(_status_pill("Permeability-favorable logP" if 0.5 <= logp <= 4.5 else "LogP tradeoff", "good" if 0.5 <= logp <= 4.5 else "warn"))
    pills.append(_status_pill("Polarity acceptable" if tpsa <= 90 else "Polarity liability", "good" if tpsa <= 90 else "warn"))
    pills.append(_status_pill("Size/flexibility acceptable" if mw <= 500 and rotatable <= 10 else "Size/flexibility liability", "good" if mw <= 500 and rotatable <= 10 else "warn"))
    if applicability is not None:
        level = "risk" if bool(applicability["outside_applicability_domain"]) else "good"
        pills.append(_status_pill(str(applicability["applicability_category"]), level))
    return '<div class="status-row">' + "".join(pills) + "</div>"


def _driver_analysis(
    descriptors: dict[str, object],
    probability: float,
) -> tuple[list[str], list[str]]:
    """Return lists of descriptor signals that push the prediction high vs low."""
    tpsa = float(descriptors["tpsa"])
    hbd = float(descriptors["hbd"])
    hba = float(descriptors["hba"])
    logp = float(descriptors["logp"])
    mw = float(descriptors["molecular_weight"])
    rotatable = float(descriptors["rotatable_bonds"])

    high_drivers: list[str] = []
    low_drivers: list[str] = []

    if tpsa <= 60:
        high_drivers.append(f"Low TPSA ({tpsa:.1f}) reduces desolvation cost, supporting passive membrane crossing.")
    elif tpsa > 120:
        low_drivers.append(f"High TPSA ({tpsa:.1f}) is a strong polarity liability for passive permeability.")
    elif tpsa > 90:
        low_drivers.append(f"Elevated TPSA ({tpsa:.1f}) moderately increases polarity burden.")
    else:
        high_drivers.append(f"Moderate TPSA ({tpsa:.1f}) is in the acceptable passive-diffusion range.")

    if 0.5 <= logp <= 4.5:
        high_drivers.append(f"LogP {logp:.2f} is in the permeability-favorable window for membrane partitioning.")
    elif logp > 5.0:
        low_drivers.append(f"High LogP ({logp:.2f}) may raise assay-liability or solubility concerns despite lipophilicity.")
    else:
        low_drivers.append(f"Low LogP ({logp:.2f}) suggests hydrophilic character that can reduce membrane partitioning.")

    if hbd <= 2:
        high_drivers.append(f"Low HBD count ({int(hbd)}) reduces desolvation penalty for membrane crossing.")
    elif hbd > 3:
        low_drivers.append(f"High HBD count ({int(hbd)}) increases desolvation cost before membrane entry.")

    if hba > 7:
        low_drivers.append(f"High HBA count ({int(hba)}) adds to polarity and hydrogen-bonding burden.")

    if mw <= 400:
        high_drivers.append(f"Low molecular weight ({mw:.0f} Da) supports efficient membrane diffusion.")
    elif mw > 500:
        low_drivers.append(f"Molecular weight ({mw:.0f} Da) exceeds the common Lipinski threshold.")

    if rotatable > 7:
        low_drivers.append(f"High rotatable-bond count ({int(rotatable)}) can add conformational penalty.")
    elif rotatable <= 4:
        high_drivers.append(f"Low flexibility ({int(rotatable)} rotatable bonds) may reduce conformational cost.")

    if not high_drivers:
        high_drivers.append("No strong permeability-favorable descriptor signals identified for this query.")
    if not low_drivers:
        low_drivers.append("No strong permeability-liability descriptor signals identified for this query.")

    return high_drivers, low_drivers


def _render_decision_summary(
    name: str,
    category: str,
    prediction: dict[str, object],
    confidence: dict[str, object] | None,
    applicability: dict[str, object] | None,
    pk_table: pd.DataFrame,
) -> None:
    """Render a prominent decision-summary card above the workflow tabs."""
    prob = float(prediction["high_permeability_probability"])
    pred_label = str(prediction["predicted_label"])
    conf_cat = str(confidence["confidence_category"]) if confidence else "N/A"
    dom_cat = str(applicability["applicability_category"]) if applicability else "N/A"
    outside_domain = bool(applicability["outside_applicability_domain"]) if applicability else False

    assumptions = permeability_to_pk_assumptions(prob)
    adj_f = assumptions["scenario_f"]
    adj_ka = assumptions["scenario_ka"]

    if len(pk_table) >= 2:
        auc_ratio = float(pk_table.iloc[1]["AUC_ratio_vs_reference"])
        cmax_ratio = float(pk_table.iloc[1]["Cmax_ratio_vs_reference"])
        clf_ratio = float(pk_table.iloc[1]["CLF_ratio_vs_reference"])
    else:
        auc_ratio = cmax_ratio = clf_ratio = float("nan")

    class_badge = "high" if pred_label == "high permeability class" else "low"
    class_text = "High Caco-2 Permeability" if class_badge == "high" else "Low Caco-2 Permeability"

    conf_badge = "high" if "high" in conf_cat.lower() else ("warn" if "low" in conf_cat.lower() else "")
    domain_badge = "low" if outside_domain else ("warn" if "borderline" in dom_cat.lower() else "high")

    exposure_dir = "increases" if auc_ratio > 1 else "decreases"
    if outside_domain:
        narrative = (
            f"<strong>{name}</strong> is predicted as <em>{pred_label}</em> with {conf_cat.lower()} model confidence "
            f"but <strong>outside-domain</strong> applicability (training-set similarity is low). "
            f"Under the educational F/ka mapping, AUC ratio is <strong>{auc_ratio:.2f}x</strong> vs the reference scenario. "
            "Treat as highly hypothesis-generating; prioritize experimental Caco-2 or MDCK permeability follow-up."
        )
    else:
        narrative = (
            f"<strong>{name}</strong> is predicted as <em>{pred_label}</em> "
            f"(probability {prob:.2f}) with {conf_cat.lower()} model confidence and {dom_cat.lower()} "
            f"applicability-domain similarity. Under the educational F/ka mapping (F = {adj_f:.2f}, "
            f"ka = {adj_ka:.2f} h⁻¹), simulated exposure {exposure_dir} relative to the reference oral scenario "
            f"(AUC ratio <strong>{auc_ratio:.2f}x</strong>, Cmax ratio <strong>{cmax_ratio:.2f}x</strong>, "
            f"CL/F ratio <strong>{clf_ratio:.2f}x</strong>). "
            "This is hypothesis-generating and should be validated experimentally."
        )

    badges = (
        f'<span class="ds-badge {class_badge}">{class_text}</span>'
        f'<span class="ds-badge {conf_badge}">Confidence: {conf_cat}</span>'
        f'<span class="ds-badge {domain_badge}">Domain: {dom_cat}</span>'
        f'<span class="ds-badge">{category}</span>'
        f'<span class="ds-badge">p = {prob:.2f}</span>'
        f'<span class="ds-badge">Scenario F = {adj_f:.2f} (assumption)</span>'
        f'<span class="ds-badge">Scenario ka = {adj_ka:.2f} h⁻¹</span>'
        f'<span class="ds-badge">AUC sensitivity ratio {auc_ratio:.2f}×</span>'
        f'<span class="ds-badge">Cmax sensitivity ratio {cmax_ratio:.2f}×</span>'
        f'<span class="ds-badge">CL/F sensitivity ratio {clf_ratio:.2f}×</span>'
    )

    st.markdown(
        f'<div class="decision-summary">'
        f'<h3>Decision Summary — {name}</h3>'
        f'<div class="ds-row">{badges}</div>'
        f'<p style="color:#1e3a8a;font-size:0.925rem;margin:0.4rem 0 0.25rem 0;">{narrative}</p>'
        f'<p style="color:#64748b;font-size:0.82rem;margin:0;">'
        "Recommended follow-up: experimental Caco-2 or MDCK permeability measurement with solubility, "
        "ionization, and transporter context. True systemic CL is fixed by design; "
        "permeability maps to F/ka absorption assumptions only, not CL."
        f'</p></div>',
        unsafe_allow_html=True,
    )


def _safe_style(
    df: pd.DataFrame,
    style_fn: object,
    column: str,
) -> object:
    """Apply element-wise column styling with full pandas 1.x / 2.x / 3.x compatibility.

    Falls back to the unstyled DataFrame if styling raises any exception so that
    the comparison table never crashes on Streamlit Cloud.
    """
    try:
        # pandas >= 2.1 renamed applymap → map; try map first
        return df.style.map(style_fn, subset=[column])  # type: ignore[arg-type]
    except Exception:
        pass
    try:
        # pandas < 2.1 fallback
        return df.style.applymap(style_fn, subset=[column])  # type: ignore[attr-defined]
    except Exception:
        pass
    # If both fail (e.g. very old or very new pandas with API change) return plain df
    return df


def _render_molecule_card_html(
    name: str,
    smiles: str,
    category: str,
    pred_label: str = "",
    suggested_f: float | None = None,
    suggested_ka: float | None = None,
    svg_width: int = 260,
    svg_height: int = 180,
) -> str:
    """Return an HTML card with an inline SVG molecule structure.

    Safe for use inside st.components.v1.html or st.markdown(unsafe_allow_html=True).
    Falls back to a SMILES code block if SVG rendering fails.
    """
    svg_body = ""
    try:
        svg = _cached_molecule_svg(smiles)
        if svg:
            # Embed the SVG inline, stripped of XML declaration if present
            svg_clean = svg.replace('<?xml version=\'1.0\' encoding=\'iso-8859-1\'?>', "").strip()
            svg_body = f'<div style="text-align:center;margin-bottom:0.3rem;">{svg_clean}</div>'
    except Exception:
        pass

    if not svg_body:
        svg_body = (
            f'<div style="font-size:0.78rem;color:#64748b;background:#f8fafc;'
            f'border-radius:6px;padding:0.5rem;margin-bottom:0.3rem;word-break:break-all;">'
            f'{smiles}</div>'
        )

    class_color = "#166534" if "high" in pred_label.lower() else "#991b1b" if "low" in pred_label.lower() else "#475569"
    class_bg = "#dcfce7" if "high" in pred_label.lower() else "#fee2e2" if "low" in pred_label.lower() else "#f1f5f9"
    pred_badge = (
        f'<span style="background:{class_bg};color:{class_color};border-radius:4px;'
        f'padding:0.15rem 0.4rem;font-size:0.78rem;font-weight:600;">{pred_label}</span>'
        if pred_label else ""
    )
    pk_line = ""
    if suggested_f is not None and suggested_ka is not None:
        pk_line = (
            f'<div style="font-size:0.78rem;color:#64748b;margin-top:0.2rem;">'
            f'F = {suggested_f:.2f} &nbsp;|&nbsp; ka = {suggested_ka:.2f} h⁻¹</div>'
        )

    return (
        f'<div style="border:1px solid #e2e8f0;border-radius:8px;background:#ffffff;'
        f'padding:0.6rem 0.7rem;box-shadow:0 2px 8px rgba(15,23,42,0.04);min-width:0;">'
        f'<div style="font-weight:700;font-size:0.93rem;color:#0f172a;margin-bottom:0.2rem;">{name}</div>'
        f'<div style="font-size:0.78rem;color:#64748b;margin-bottom:0.35rem;">{category}</div>'
        f'{svg_body}'
        f'{pred_badge}'
        f'{pk_line}'
        f'</div>'
    )


def _medchem_interpretation(name: str, descriptors: dict[str, object]) -> str:
    mw = float(descriptors["molecular_weight"])
    logp = float(descriptors["logp"])
    tpsa = float(descriptors["tpsa"])
    hbd = int(descriptors["hbd"])
    hba = int(descriptors["hba"])
    rotatable = int(descriptors["rotatable_bonds"])
    polarity = "moderate polarity" if tpsa <= 90 else "high polarity"
    lipophilicity = "lipophilic" if logp >= 3 else "less lipophilic"
    size = "low-to-moderate molecular weight" if mw <= 450 else "larger molecular size"
    hb_note = "limited hydrogen bonding" if hbd <= 1 and hba <= 5 else "substantial hydrogen-bonding capacity"
    flex_note = "low flexibility" if rotatable <= 5 else "higher flexibility"
    return (
        f"{name} has {polarity}, {size}, {hb_note}, and {flex_note}. "
        f"Its logP of {logp:.2f} makes it {lipophilicity}, while TPSA of {tpsa:.1f} reflects the desolvation burden for passive diffusion. "
        "Together, these descriptors support a permeability-risk hypothesis that should be checked against model confidence and applicability-domain similarity."
    )


def _decision_support_text(name: str, probability: float, descriptors: dict[str, object]) -> str:
    tpsa = float(descriptors["tpsa"])
    logp = float(descriptors["logp"])
    if probability >= 0.65 and tpsa <= 100:
        priority = "reasonable to prioritize for permeability follow-up"
    elif probability < 0.45 or tpsa > 120:
        priority = "a permeability-liability candidate that should be investigated experimentally"
    else:
        priority = "a borderline molecule where experimental context matters"
    return (
        f"For {name}, the model output and descriptors make this {priority}. "
        f"A practical validation path would be Caco-2 or MDCK permeability measurement, ideally paired with solubility, ionization, and transporter-aware follow-up. "
        f"The logP ({logp:.2f}) and TPSA ({tpsa:.1f}) provide a quick medicinal-chemistry explanation for the model hypothesis."
    )


def _feature_importance_table(descriptors: dict[str, object]) -> pd.DataFrame:
    rows = [
        ("TPSA", float(descriptors["tpsa"]), "Higher polarity usually penalizes passive membrane diffusion."),
        ("HBD", float(descriptors["hbd"]), "Donors can increase desolvation cost before membrane crossing."),
        ("HBA", float(descriptors["hba"]), "Acceptors contribute to polarity and hydrogen-bonding burden."),
        ("LogP", float(descriptors["logp"]), "Lipophilicity can support membrane partitioning but may hurt solubility."),
        ("Molecular weight", float(descriptors["molecular_weight"]), "Larger molecules often diffuse less efficiently."),
        ("Rotatable bonds", float(descriptors["rotatable_bonds"]), "Flexibility can add conformational penalty."),
    ]
    return pd.DataFrame(rows, columns=["Feature", "Current value", "Chemical interpretation"])


def _format_comparison_table(comparison: pd.DataFrame) -> pd.DataFrame:
    table = comparison.rename(
        columns={
            "molecule": "Molecule",
            "category": "Category",
            "molecular_weight": "MW",
            "logp": "LogP",
            "tpsa": "TPSA",
            "hbd": "HBD",
            "hba": "HBA",
            "rotatable_bonds": "Rotatable bonds",
            "predicted_permeability": "Predicted class",
            "high_probability": "High permeability probability",
            "confidence": "Confidence",
            "applicability_similarity": "Applicability similarity",
            "suggested_f": "Scenario F (educational assumption)",
            "suggested_ka": "Scenario ka (educational assumption, 1/h)",
        }
    )
    numeric_cols = [
        "MW", "LogP", "TPSA",
        "High permeability probability", "Confidence", "Applicability similarity",
        "Scenario F (educational assumption)", "Scenario ka (1/h)",
    ]
    for col in numeric_cols:
        if col in table:
            table[col] = table[col].map(lambda value: None if pd.isna(value) else round(float(value), 3))
    return table


def _prediction_with_confidence(smiles: str) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    prediction = _cached_prediction(smiles)
    if prediction is None:
        return None, None
    return prediction, prediction_confidence(prediction)


def _select_example_molecule(location: str = "single") -> tuple[str, str, str]:
    examples = _example_table()
    categories = ["All categories", *EXAMPLE_CATEGORIES]
    category = st.selectbox("Therapeutic category", categories, key=f"{location}_category")
    query = st.text_input("Search molecule library", placeholder="Search by drug name", key=f"{location}_search")

    filtered = examples.copy()
    if category != "All categories":
        filtered = filtered[filtered["category"] == category]
    if query.strip():
        filtered = filtered[filtered["name"].str.contains(query.strip(), case=False, regex=False)]
    if filtered.empty:
        st.warning("No examples match that search. Clear the search or choose another category.")
        return "", "", ""

    if st.button("Random demo molecule", key=f"{location}_random", use_container_width=True):
        random_row = filtered.sample(n=1, random_state=random.randint(0, 1_000_000)).iloc[0]
        st.session_state[f"{location}_select"] = str(random_row["label"])

    options = filtered["label"].tolist()
    if st.session_state.get(f"{location}_select") not in options:
        st.session_state[f"{location}_select"] = options[0]
    label = st.selectbox(
        f"Example molecule ({len(filtered)} shown)",
        options,
        key=f"{location}_select",
    )
    selected = filtered[filtered["label"] == label].iloc[0]
    return str(selected["name"]), str(selected["smiles"]), str(selected["teaching_note"])


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>Explainable AI ADME-PK Platform</h1>
            <p>
                Real-data Caco-2 permeability prediction with explainability,
                applicability-domain checks, molecule comparison, and educational
                PK/NCA simulation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(_html_card("What this app does", WHAT_THIS_APP_DOES), unsafe_allow_html=True)
    workflow_cards = [
        _workflow_card("Input", "SMILES / molecule library", "Search 172 curated examples or paste a custom structure."),
        _workflow_card("Chemistry", "RDKit descriptors + fingerprints", "Calculate physicochemical and substructure features."),
        _workflow_card("Model", "Caco-2 permeability classifier", "Predict median-threshold permeability class."),
        _workflow_card("Trust", "Confidence + applicability domain", "Separate decisive predictions from extrapolation risk."),
        _workflow_card("Explanation", "SHAP / feature importance", "Translate model behavior into chemical hypotheses."),
        _workflow_card("Education", "PK/NCA simulator", "Teach exposure metrics from explicit assumptions."),
    ]
    st.markdown('<div class="workflow-strip">' + "".join(workflow_cards) + "</div>", unsafe_allow_html=True)
    metrics = [
        _hero_metric("906", "processed Caco-2 compounds"),
        _hero_metric(str(EXAMPLE_MOLECULE_COUNT), "validated example molecules"),
        _hero_metric("2 validation modes", "random + scaffold split"),
        _hero_metric("Explainability", "SHAP + uncertainty"),
        _hero_metric("PK/NCA", "educational simulation module"),
    ]
    st.markdown('<div class="metric-grid">' + "".join(metrics) + "</div>", unsafe_allow_html=True)


def _render_scientific_boundary() -> None:
    st.info(
        "Scientific boundary: predictions are median-threshold Caco-2 permeability classes from molecular structure. "
        "The PK/NCA module uses user-specified assumptions. This app does not provide validated human PK, PBPK, "
        "dose, safety, efficacy, or regulatory conclusions."
    )


def _render_learning_panel() -> None:
    with st.expander("How to use this app", expanded=False):
        for index, step in enumerate(HOW_TO_USE_STEPS, start=1):
            st.write(f"**Step {index}:** {step}")
    with st.expander("Scientific guide: what the ADME model is showing", expanded=False):
        st.markdown(
            """
            **Caco-2 permeability** uses intestinal epithelial cell monolayers as an in vitro proxy for how readily a compound crosses a cell barrier. It is useful for early screening, but it is not the same as human oral absorption.

            **Why permeability matters:** low permeability can limit absorption even when a molecule is potent. Permeability also interacts with solubility, ionization, transporters, metabolism, dose, and formulation.

            **SHAP interpretation:** SHAP is an explainability method that attributes a model prediction across input features. In this app, descriptor and fingerprint signals should be read as model behavior, not proof of biological mechanism.

            **Confidence score:** confidence is derived from probability margin and entropy. It tells you whether the classifier is decisive for this model, not whether a compound is clinically certain to behave a certain way.

            **Applicability domain:** nearest-neighbor similarity asks whether the query resembles training chemistry. Low similarity means the model is extrapolating and should be treated cautiously.

            **Scaffold split validation:** molecules are split by core chemical scaffold so close analogs do not leak across train/test sets. This is stricter than a random split and better reflects medicinal chemistry generalization.
            """
        )
    with st.expander("PK equations used in this educational simulator", expanded=False):
        st.markdown(PK_EQUATIONS_TEXT)
    with st.expander("IV bolus vs oral dosing", expanded=False):
        st.markdown(IV_ORAL_EXPLANATION)
    with st.expander("What IVIVE would require", expanded=False):
        st.markdown(IVIVE_EXPLANATION)
    with st.expander("References and scientific grounding", expanded=False):
        for reference in REFERENCES:
            st.write(f"- **{reference['name']}**: {reference['url']} — {reference['note']}")


def _render_molecule_structure(smiles: str) -> None:
    svg = _cached_molecule_svg(smiles)
    if svg:
        # Wrap in a full HTML document — raw SVG (starting with <?xml?>) does not
        # render reliably inside the st.components.v1.html iframe on all browsers.
        components.html(svg_to_html_page(svg), height=320)
        st.caption("2D molecular structure (RDKit SVG)")
    else:
        try:
            analysis = _analyze_smiles(smiles)
            descriptors = dict(analysis["descriptors"])
            canonical = str(analysis["canonical_smiles"])
            st.caption("SMILES (structure image not available in this environment)")
            st.code(canonical, language="text")
            col_mw, col_tpsa, col_logp = st.columns(3)
            col_mw.metric("MW", _metric_number(descriptors.get("molecular_weight"), 1))
            col_tpsa.metric("TPSA", _metric_number(descriptors.get("tpsa"), 1))
            col_logp.metric("LogP", _metric_number(descriptors.get("logp"), 2))
        except ValueError:
            st.info("Structure preview unavailable for this input.")


def _descriptor_dataframe(descriptors: dict[str, object]) -> pd.DataFrame:
    ordered = [
        ("molecular_weight", "Molecular weight"),
        ("logp", "LogP"),
        ("tpsa", "TPSA"),
        ("hbd", "HBD"),
        ("hba", "HBA"),
        ("rotatable_bonds", "Rotatable bonds"),
        ("ring_count", "Rings"),
        ("aromatic_ring_count", "Aromatic rings"),
        ("formal_charge", "Formal charge"),
        ("fraction_csp3", "Fraction Csp3"),
        ("heavy_atom_count", "Heavy atoms"),
        ("heteroatom_count", "Heteroatoms"),
        ("molar_refractivity", "Molar refractivity"),
    ]
    return pd.DataFrame(
        [{"descriptor": label, "value": descriptors[key]} for key, label in ordered if key in descriptors]
    )


def _interpret_flags(flags: dict[str, bool | int]) -> list[str]:
    messages = []
    if flags["lipinski_violations"] == 0:
        messages.append("No Lipinski rule-of-five violations were detected.")
    else:
        messages.append(f"{flags['lipinski_violations']} Lipinski rule-of-five violation(s) were detected.")
    if flags["high_tpsa_flag"]:
        messages.append("High TPSA can reduce passive membrane diffusion.")
    if flags["high_rotatable_bonds_flag"]:
        messages.append("High flexibility can increase conformational cost.")
    if flags["high_logp_flag"]:
        messages.append("High logP may increase lipophilicity while raising solubility or assay-liability concerns.")
    if flags["high_mw_flag"]:
        messages.append("Molecular weight is above the common Lipinski threshold.")
    messages.append("These are screening heuristics, not clinical predictions.")
    return messages


def render_adme_screening() -> None:
    """Render molecular descriptor, prediction, and explainability workflow."""
    st.header("ADME Screening Workbench")
    st.caption(f"Explore {EXAMPLE_MOLECULE_COUNT} RDKit-validated example molecules or paste a custom SMILES.")

    mode = st.segmented_control(
        "Input mode",
        ["Example library", "Custom SMILES"],
        default="Example library",
        key="adme_input_mode",
    )

    selected_name = "Custom molecule"
    teaching_note = "Custom molecule: descriptors and model-domain checks should be reviewed before interpretation."
    if mode == "Example library":
        selected_name, smiles, teaching_note = _select_example_molecule("single")
    else:
        smiles = st.text_area(
            "SMILES string",
            placeholder="Example: Cn1cnc2c1c(=O)n(C)c(=O)n2C",
            key="custom_smiles",
        )

    if not smiles.strip():
        st.info("Choose an example molecule or enter a SMILES string to run the screening workflow.")
        return

    try:
        analysis = _analyze_smiles(smiles)
    except ValueError as error:
        st.error(str(error))
        return

    canonical_smiles = str(analysis["canonical_smiles"])
    descriptors = dict(analysis["descriptors"])
    flags = dict(analysis["flags"])
    feature_vector = dict(analysis["feature_vector"])
    prediction, confidence = _prediction_with_confidence(smiles)
    applicability = _cached_applicability(smiles)

    st.markdown(
        '<div class="section-note">Structure validation -> molecular descriptors -> permeability model -> confidence -> applicability-domain review.</div>',
        unsafe_allow_html=True,
    )

    top_cols = st.columns([1.05, 1.4, 1.2])
    with top_cols[0]:
        _render_molecule_structure(smiles)
    with top_cols[1]:
        st.subheader(selected_name)
        selected_category = "Custom molecule"
        if mode == "Example library":
            selected_category = _example_table().set_index("name").loc[selected_name, "category"]
        st.caption(str(selected_category))
        st.markdown(f'<div class="section-note">{teaching_note}</div>', unsafe_allow_html=True)
        st.caption("Canonical RDKit SMILES")
        st.code(canonical_smiles, language="text")
        st.markdown(
            _html_card(
                "Why this molecule is interesting",
                _medchem_interpretation(selected_name, descriptors),
            ),
            unsafe_allow_html=True,
        )
    with top_cols[2]:
        st.markdown("#### Key properties")
        st.metric("MW", _metric_number(descriptors.get("molecular_weight"), 1))
        st.metric("LogP", _metric_number(descriptors.get("logp"), 2))
        st.metric("TPSA", _metric_number(descriptors.get("tpsa"), 1))
        st.metric("HBD / HBA", f"{descriptors.get('hbd')} / {descriptors.get('hba')}")
        st.metric("Rotatable bonds", str(descriptors.get("rotatable_bonds")))

    st.markdown(_descriptor_status(descriptors, applicability), unsafe_allow_html=True)

    if prediction is not None:
        _pk_table_for_summary = pk_impact_table(float(prediction["high_permeability_probability"]))
        _render_decision_summary(
            selected_name, selected_category, prediction, confidence, applicability, _pk_table_for_summary
        )

        # --- Experiment recommendation ---
        if confidence is not None and applicability is not None:
            _exp_rec = experiment_recommendation(
                name=selected_name,
                probability=float(prediction["high_permeability_probability"]),
                confidence_cat=str(confidence["confidence_category"]),
                domain_cat=str(applicability["applicability_category"]),
                outside_domain=bool(applicability["outside_applicability_domain"]),
                descriptors=descriptors,
            )
            with st.expander("Recommended next experiment", expanded=False):
                st.markdown(_html_card("Beginner recommendation", _exp_rec["beginner"]), unsafe_allow_html=True)
                st.markdown(_html_card("Pharmaceutics / PhD-level recommendation", _exp_rec["phd"]), unsafe_allow_html=True)

    workflow_tabs = st.tabs(
        [
            "Descriptors",
            "Permeability",
            "Confidence",
            "Applicability Domain",
            "Explainable AI",
            "Absorption Sensitivity",
            "Limits",
        ]
    )

    with workflow_tabs[0]:
        st.subheader("Descriptor and Rule-Based ADME Signals")
        desc_col, interp_col = st.columns([1.05, 1.2])
        with desc_col:
            st.dataframe(_descriptor_dataframe(descriptors), hide_index=True, use_container_width=True)
            st.bar_chart(
                pd.DataFrame(
                    {
                        "MW": [float(descriptors["molecular_weight"])],
                        "TPSA": [float(descriptors["tpsa"])],
                        "LogP x 50": [float(descriptors["logp"]) * 50],
                    },
                    index=[selected_name],
                )
            )
        with interp_col:
            descriptor_cards = [
                _html_card("MW: size and diffusion", "Lower molecular weight generally supports passive diffusion; very large molecules can face size and conformational penalties."),
                _html_card("LogP: membrane partitioning", "Moderate lipophilicity can support membrane entry, while very high logP can create solubility and assay-liability concerns."),
                _html_card("TPSA: polarity liability", "Higher polar surface area increases desolvation cost and often reduces passive permeability."),
                _html_card("HBD/HBA: hydrogen bonding", "Hydrogen-bond donors and acceptors can improve recognition but may penalize membrane crossing."),
                _html_card("Rotatable bonds: flexibility", "High flexibility can increase entropic cost and reduce permeability efficiency."),
            ]
            st.markdown("".join(descriptor_cards), unsafe_allow_html=True)
        st.markdown("#### Medicinal chemistry interpretation")
        st.write(_medchem_interpretation(selected_name, descriptors))
        st.markdown("#### Lipinski / Veber-style flags")
        for message in _interpret_flags(flags):
            st.write(f"- {message}")

    with workflow_tabs[1]:
        st.subheader("Caco-2 Permeability Prediction")
        if prediction is not None:
            probability = float(prediction["high_permeability_probability"])
            cols = st.columns(4)
            cols[0].metric("Predicted class", str(prediction["predicted_label"]))
            cols[1].metric("High-class probability", f"{probability:.2f}")
            cols[2].metric("Source", str(prediction.get("prediction_source", "model")))
            cols[3].metric("Class threshold", "Dataset median")
            st.markdown('<div class="prob-labels"><span>Low permeability class</span><span>High permeability class</span></div>', unsafe_allow_html=True)
            st.progress(probability)
            if prediction.get("prediction_source") == "descriptor fallback":
                st.info(str(prediction.get("prediction_note")))
            pred_cards = [
                _html_card("Biological interpretation", "A high Caco-2 class suggests the model sees descriptor/fingerprint patterns associated with higher in vitro epithelial permeability in the benchmark."),
                _html_card("What it does not mean", "This is not validated human oral absorption, clinical PK, dose selection, safety, efficacy, or regulatory evidence."),
                _html_card("Dataset context", "The classifier was trained on Caco2_Wang log(Papp), converted to a median-threshold class and evaluated with both random and scaffold split validation."),
                _html_card("Decision support interpretation", _decision_support_text(selected_name, probability, descriptors)),
            ]
            st.markdown("".join(pred_cards), unsafe_allow_html=True)

    with workflow_tabs[2]:
        st.subheader("Confidence Score")
        if confidence is None:
            st.info("Prediction confidence is available after model prediction.")
        else:
            cols = st.columns(3)
            cols[0].metric("Category", str(confidence["confidence_category"]))
            cols[1].metric("Confidence", f"{float(confidence['confidence_score']):.2f}")
            cols[2].metric("Entropy", f"{float(confidence['prediction_entropy']):.2f}")
            confidence_cards = [
                _html_card("Probability confidence", "Confidence increases when the classifier probability moves away from the 0.5 decision boundary."),
                _html_card("Entropy", "Entropy is higher when the model is uncertain between classes and lower when one class dominates."),
                _html_card("Local reliability statement", "This reliability statement is internal to the model and feature representation. It should be interpreted alongside applicability-domain similarity."),
                _html_card("Boundary", "Confidence is not clinical certainty and does not replace experimental permeability measurement."),
            ]
            st.markdown("".join(confidence_cards), unsafe_allow_html=True)

    with workflow_tabs[3]:
        st.subheader("Applicability Domain")
        if applicability is None:
            st.warning("Applicability-domain analysis could not be loaded in this environment.")
        else:
            similarity = float(applicability["nearest_neighbor_similarity"])
            cols = st.columns(3)
            cols[0].metric("Domain category", str(applicability["applicability_category"]))
            cols[1].metric("Nearest similarity", f"{similarity:.2f}")
            cols[2].metric("Outside domain", str(bool(applicability["outside_applicability_domain"])))
            st.progress(max(0.0, min(similarity, 1.0)))
            st.write(f"Nearest training SMILES: `{applicability['nearest_neighbor_smiles']}`")
            if applicability["applicability_warning"]:
                st.warning(str(applicability["applicability_warning"]))
            else:
                st.success("The molecule is reasonably similar to training chemistry.")
            domain_text = (
                "This molecule is being evaluated against training-set chemistry by Morgan-fingerprint Tanimoto similarity. "
                "If similarity is borderline or low, the prediction should be treated as hypothesis-generating and ideally validated with in vitro permeability data."
            )
            action_text = (
                "For outside-domain molecules, prioritize experimental Caco-2 or MDCK follow-up, inspect nearest neighbors, and avoid overinterpreting class probabilities."
            )
            st.markdown(_html_card("Why applicability domain matters", domain_text) + _html_card("What to do if outside domain", action_text), unsafe_allow_html=True)

    with workflow_tabs[4]:
        st.subheader("Explainable AI Evidence")

        high_drivers, low_drivers = _driver_analysis(descriptors, float(prediction["high_permeability_probability"]) if prediction else 0.5)

        _xai_col1, _xai_col2 = st.columns([1.1, 1.0])

        with _xai_col1:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            _feat_labels = ["TPSA", "HBD", "HBA", "LogP", "MW / 10", "Rotatable\nbonds"]
            _raw_vals = [
                float(descriptors["tpsa"]),
                float(descriptors["hbd"]),
                float(descriptors["hba"]),
                float(descriptors["logp"]),
                float(descriptors["molecular_weight"]) / 10.0,
                float(descriptors["rotatable_bonds"]),
            ]
            _thresholds = [90, 3, 7, 4.5, 50.0, 7]
            _colors = [
                "#16a34a" if _raw_vals[i] <= _thresholds[i] else "#dc2626"
                for i in range(len(_raw_vals))
            ]
            _fig, _ax = plt.subplots(figsize=(6, 3.8))
            _bars = _ax.barh(_feat_labels, _raw_vals, color=_colors, edgecolor="#e2e8f0", linewidth=0.6)
            _ax.set_xlabel("Value (MW scaled ÷ 10)", fontsize=8.5)
            _ax.set_title(f"Descriptor profile — {selected_name}", fontsize=9.5, fontweight="bold")
            _ax.tick_params(axis="both", labelsize=8)
            for bar, val in zip(_bars, _raw_vals):
                _ax.text(max(val + 0.3, 0.3), bar.get_y() + bar.get_height() / 2, f"{val:.1f}", va="center", fontsize=7.5, color="#334155")
            _ax.spines["top"].set_visible(False)
            _ax.spines["right"].set_visible(False)
            _fig.tight_layout()
            st.pyplot(_fig, clear_figure=True)
            plt.close(_fig)
            st.caption("Green = below threshold (permeability-favorable); Red = above threshold (potential liability). Thresholds: TPSA ≤ 90, HBD ≤ 3, HBA ≤ 7, LogP ≤ 4.5, MW/10 ≤ 50, RotBonds ≤ 7.")

        with _xai_col2:
            st.markdown(_html_card("Global vs local explanation", "Global feature importance summarizes model behavior across training samples. Local explanation (shown here) asks which descriptor signals are most relevant for <em>this</em> molecule. SHAP explains model behavior, not causal biology."), unsafe_allow_html=True)
            st.markdown(
                _html_card(
                    "What pushed this prediction toward high permeability",
                    "<ul style='margin:0;padding-left:1.2rem;'>" + "".join(f"<li>{d}</li>" for d in high_drivers) + "</ul>",
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                _html_card(
                    "What pushed this prediction toward low permeability",
                    "<ul style='margin:0;padding-left:1.2rem;'>" + "".join(f"<li>{d}</li>" for d in low_drivers) + "</ul>",
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                _html_card(
                    "What SHAP cannot prove",
                    "SHAP attribution explains model behavior, not causal biology. A feature ranked as important by SHAP does not mean that descriptor is the biological rate-limiting factor for permeability in vivo. Transporter involvement, solubility, ionization state, and first-pass metabolism are not captured here.",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("#### Descriptor driver table")
        st.dataframe(_feature_importance_table(descriptors), hide_index=True, use_container_width=True)

        shap_dir = PROJECT_ROOT / "reports" / "figures" / "shap"
        local_candidates = [
            shap_dir / "local_aspirin_classifier.png",
            shap_dir / "local_caffeine_classifier.png",
            shap_dir / "classifier_bar_importance.png",
            shap_dir / "classifier_summary.png",
        ]
        shown = False
        for path in local_candidates:
            if path.exists():
                st.image(str(path), caption=path.name)
                shown = True
        if not shown:
            st.caption("Optional saved SHAP figures can be generated offline for deeper model-audit materials. The descriptor driver profile above provides the lightweight XAI view.")

    with workflow_tabs[5]:
        st.subheader("Absorption Sensitivity Simulator")
        if prediction is None:
            st.info("Run a permeability prediction first to see the absorption sensitivity simulator.")
        else:
            probability = float(prediction["high_permeability_probability"])
            assumptions = permeability_to_pk_assumptions(probability)

            # --- Top-of-section scientific disclaimer ---
            st.warning(
                "**Scientific boundary:** "
                + F_SCENARIO_DISCLAIMER
                + " The F and ka values below are **user-editable educational scenario assumptions** — "
                "they are illustrative starting points, not model predictions. "
                "Edit them freely to explore sensitivity."
            )

            # --- Literature F comparison if drug is known ---
            _lit_f_profile = None
            _mol_key_lower = selected_name.lower().replace(" ", "_")
            if _mol_key_lower in DRUG_PK_PROFILES:
                _lit_f_profile = DRUG_PK_PROFILES[_mol_key_lower]
            else:
                for _k, _p in DRUG_PK_PROFILES.items():
                    if _p["name"].lower() == selected_name.lower():
                        _lit_f_profile = _p
                        break

            if _lit_f_profile and _lit_f_profile.get("f_literature") is not None:
                _lit_f = float(_lit_f_profile["f_literature"])
                _scen_f = float(assumptions["scenario_f"])
                _mismatch = abs(_scen_f - _lit_f)
                _f_range = _lit_f_profile.get("f_literature_range", f"~{_lit_f:.2f}")
                _f_note = _lit_f_profile.get("f_literature_note", "")

                _f_col1, _f_col2 = st.columns([1, 1.4])
                with _f_col1:
                    st.metric("Literature teaching F", f"{_lit_f:.2f}", help=f"Range: {_f_range}")
                    st.metric("Default scenario F", f"{_scen_f:.2f}", help="Illustrative starting assumption, not a prediction")
                with _f_col2:
                    if _f_note:
                        st.markdown(_html_card("Literature teaching note", _f_note), unsafe_allow_html=True)

                if _mismatch > F_MISMATCH_THRESHOLD:
                    st.warning(
                        f"**F mismatch:** The default scenario F ({_scen_f:.2f}) differs from the literature "
                        f"teaching F ({_lit_f:.2f}) by {_mismatch:.2f}. This is expected — the app does not "
                        "predict human bioavailability. F depends on permeability, solubility, formulation, "
                        "metabolism, transporters, and first-pass extraction. "
                        "Adjust the scenario F below to match literature values if appropriate."
                    )

            # --- 3-step workflow strip ---
            st.markdown(
                '<div class="three-step">'
                '<div class="step-card"><div class="step-num">1</div>'
                '<div class="step-title">Caco-2 Prediction</div>'
                '<div class="step-body">ML model predicts Caco-2 permeability class and probability</div></div>'
                '<div class="step-card"><div class="step-num">&#8594;</div>'
                '<div class="step-title">Absorption Hypothesis</div>'
                '<div class="step-body">Permeability class informs a <em>hypothesis</em> about absorption favorability</div></div>'
                '<div class="step-card"><div class="step-num">3</div>'
                '<div class="step-title">Sensitivity Simulation</div>'
                '<div class="step-body">User edits F and ka assumptions; simulated PK curve shows how exposure changes</div></div>'
                '</div>',
                unsafe_allow_html=True,
            )

            # --- Formula callout + assumption mapping ---
            formula_col, map_col = st.columns([1.0, 1.5])
            with formula_col:
                st.markdown(
                    '<div class="formula-callout">'
                    "AUC<sub>oral</sub> = F &times; Dose / CL<br>"
                    "CL/F &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= Dose / AUC<br>"
                    "k<sub>el</sub> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= CL / Vd<br>"
                    "<hr style='margin:0.35rem 0;border-color:#c7d2fe;'>"
                    "<strong>True CL is fixed by design.</strong> When F &uarr;, AUC &uarr; and apparent CL/F &darr;."
                    '</div>',
                    unsafe_allow_html=True,
                )
            with map_col:
                st.markdown(
                    _html_card(
                        "Default scenario assumption (illustrative, not a prediction)",
                        f"Caco-2 probability <strong>{probability:.2f}</strong> &rarr; "
                        f"Default scenario F = <strong>{assumptions['scenario_f']:.2f}</strong> &nbsp;|&nbsp; "
                        f"Default scenario ka = <strong>{assumptions['scenario_ka']:.2f} h⁻¹</strong>.<br>"
                        f"Reference F = {assumptions['reference_f']:.2f} &nbsp;|&nbsp; "
                        f"Reference ka = {assumptions['reference_ka']:.2f} h⁻¹.<br>"
                        "<em>Edit the sliders below to change the sensitivity scenario.</em>",
                    ),
                    unsafe_allow_html=True,
                )

            # --- Editable assumption parameters ---
            st.markdown(
                "#### User-editable sensitivity scenario parameters",
                help="These are educational sensitivity inputs. Changing F changes simulated AUC. True CL is fixed unless you edit it.",
            )
            st.caption(F_EDUCATIONAL_NOTE)
            _key = str(abs(hash(canonical_smiles)) % 10_000_000)
            pcols = st.columns(7)
            pk_dose = pcols[0].number_input(
                "Dose", 0.001, 10_000.0, float(assumptions["dose"]), step=10.0, key=f"pki_dose_{_key}"
            )
            pk_vd = pcols[1].number_input(
                "Vd (L)", 0.001, 1000.0, float(assumptions["vd"]), step=1.0, key=f"pki_vd_{_key}"
            )
            pk_cl = pcols[2].number_input(
                "True CL (L/h)", 0.001, 500.0, float(assumptions["true_cl"]), step=0.5, key=f"pki_cl_{_key}"
            )
            pk_ref_f = pcols[3].slider(
                "Ref scenario F", 0.01, 1.0, float(assumptions["reference_f"]), step=0.01, key=f"pki_rf_{_key}"
            )
            pk_ref_ka = pcols[4].number_input(
                "Ref ka (1/h)", 0.001, 20.0, float(assumptions["reference_ka"]),
                format="%.3f", step=0.1, key=f"pki_rka_{_key}"
            )
            pk_adj_f = pcols[5].slider(
                "Scenario F", 0.01, 1.0, float(assumptions["scenario_f"]), step=0.01, key=f"pki_af_{_key}"
            )
            pk_adj_ka = pcols[6].number_input(
                "Scenario ka (1/h)", 0.001, 20.0, float(assumptions["scenario_ka"]),
                format="%.3f", step=0.1, key=f"pki_aka_{_key}"
            )

            # --- Compute profiles ---
            _kel = pk_cl / pk_vd
            _dur, _ivl = float(assumptions["duration"]), float(assumptions["interval"])
            try:
                _ref_prof, _ = simulate_pk_profile(
                    route="oral", dose=pk_dose, vd=pk_vd, kel=_kel,
                    duration=_dur, interval=_ivl, ka=pk_ref_ka, bioavailability=pk_ref_f,
                )
                _adj_prof, _ = simulate_pk_profile(
                    route="oral", dose=pk_dose, vd=pk_vd, kel=_kel,
                    duration=_dur, interval=_ivl, ka=pk_adj_ka, bioavailability=pk_adj_f,
                )
                _ref_nca, _ = calculate_nca(_ref_prof, dose=pk_dose, route="oral", bioavailability=pk_ref_f)
                _adj_nca, _ = calculate_nca(_adj_prof, dose=pk_dose, route="oral", bioavailability=pk_adj_f)
            except Exception as _pke:
                st.error(f"PK simulation error: {_pke}")
                _ref_prof = _adj_prof = _ref_nca = _adj_nca = None

            if _ref_nca and _adj_nca:
                _ref_auc = float(_ref_nca["auc_inf"])
                _adj_auc = float(_adj_nca["auc_inf"])
                _ref_cmax = float(_ref_nca["cmax"])
                _adj_cmax = float(_adj_nca["cmax"])
                _ref_tmax = float(_ref_nca["tmax"])
                _adj_tmax = float(_adj_nca["tmax"])
                _ref_clf = float(_ref_nca["clearance"])
                _adj_clf = float(_adj_nca["clearance"])
                _auc_ratio = _adj_auc / _ref_auc if _ref_auc else float("nan")
                _cmax_ratio = _adj_cmax / _ref_cmax if _ref_cmax else float("nan")
                _tmax_shift = _adj_tmax - _ref_tmax
                _clf_ratio = _adj_clf / _ref_clf if _ref_clf else float("nan")

                # --- Interpretation cards BEFORE plots ---
                _pk_table_local = pk_impact_table(probability)
                _interps = pk_impact_interpretations(_pk_table_local)
                st.markdown(
                    _html_card("Beginner interpretation", _interps["beginner"]),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    _html_card("Pharmaceutics / PhD-level interpretation", _interps["phd"]),
                    unsafe_allow_html=True,
                )

                # --- Prominent metric cards ---
                st.markdown("#### Key exposure metrics")
                _mc = st.columns(4)
                _mc[0].markdown(
                    f'<div class="big-metric"><div class="bm-value">{_auc_ratio:.3f}×</div><div class="bm-label">AUC ratio (adj / ref)</div></div>',
                    unsafe_allow_html=True,
                )
                _mc[1].markdown(
                    f'<div class="big-metric"><div class="bm-value">{_cmax_ratio:.3f}×</div><div class="bm-label">Cmax ratio (adj / ref)</div></div>',
                    unsafe_allow_html=True,
                )
                _mc[2].markdown(
                    f'<div class="big-metric"><div class="bm-value">{_tmax_shift:+.2f} h</div><div class="bm-label">Tmax shift (adj − ref)</div></div>',
                    unsafe_allow_html=True,
                )
                _mc[3].markdown(
                    f'<div class="big-metric"><div class="bm-value">{_clf_ratio:.3f}×</div><div class="bm-label">CL/F ratio (adj / ref)</div></div>',
                    unsafe_allow_html=True,
                )

                # Secondary metrics row
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("True CL (L/h)", f"{pk_cl:.2f}", help="Fixed by design; permeability does not change true systemic clearance.")
                with m2:
                    st.metric("Ref AUC → Adj AUC", f"{_ref_auc:.1f} → {_adj_auc:.1f}")
                with m3:
                    st.metric("Ref CL/F → Adj CL/F", f"{_ref_clf:.1f} → {_adj_clf:.1f}")

                # --- Plots ---
                _curve_data = pd.merge(
                    _ref_prof.rename(columns={"concentration": "Reference"})[["time", "Reference"]],
                    _adj_prof.rename(columns={"concentration": "Permeability-adjusted"})[["time", "Permeability-adjusted"]],
                    on="time",
                )
                _curve_data = _curve_data.set_index("time")
                pk_plot_tabs = st.tabs(["Linear C-t overlay", "Semi-log C-t overlay", "Scenario table"])
                with pk_plot_tabs[0]:
                    st.line_chart(_curve_data)
                    st.caption("Concentration-time curves: reference (blue) vs permeability-adjusted (orange) absorption assumptions. AUC ratio reflects F change only; true CL is unchanged.")
                with pk_plot_tabs[1]:
                    _semi = _curve_data.copy()
                    for _c in _semi.columns:
                        _semi[_c] = np.log10(_semi[_c].clip(lower=1e-10))
                    st.line_chart(_semi)
                    st.caption("Semi-log scale (log₁₀ concentration). Parallel terminal slopes confirm true CL is identical in both scenarios.")
                with pk_plot_tabs[2]:
                    _scenario_table = pd.DataFrame({
                        "Parameter": ["F", "ka (1/h)", "AUC", "Cmax", "Tmax", "True CL (fixed)", "CL/F"],
                        "Reference scenario": [
                            f"{pk_ref_f:.3f}", f"{pk_ref_ka:.3f}",
                            f"{_ref_auc:.2f}", f"{_ref_cmax:.2f}", f"{_ref_tmax:.2f}",
                            f"{pk_cl:.2f}", f"{_ref_clf:.2f}",
                        ],
                        "Permeability-adjusted": [
                            f"{pk_adj_f:.3f}", f"{pk_adj_ka:.3f}",
                            f"{_adj_auc:.2f}", f"{_adj_cmax:.2f}", f"{_adj_tmax:.2f}",
                            f"{pk_cl:.2f} (unchanged)", f"{_adj_clf:.2f}",
                        ],
                        "Ratio (adj / ref)": [
                            f"{pk_adj_f / pk_ref_f:.3f}", f"{pk_adj_ka / pk_ref_ka:.3f}",
                            f"{_auc_ratio:.3f}", f"{_cmax_ratio:.3f}",
                            f"{_adj_tmax / _ref_tmax:.3f}" if _ref_tmax else "N/A",
                            "1.000", f"{_clf_ratio:.3f}",
                        ],
                    })
                    st.dataframe(_scenario_table, hide_index=True, use_container_width=True)

                # --- Warning banner ---
                st.warning(
                    "Educational scenario only. F and ka are mapped from permeability probability — not measured. "
                    "True CL is fixed by design. Transporters, solubility, first-pass metabolism, protein binding, and formulation also influence real exposure."
                )

    with workflow_tabs[6]:
        st.subheader("Scientific Limits")
        st.markdown(
            """
            - Caco-2 permeability is an in vitro endpoint, not validated human PK.
            - The binary class threshold is dataset-derived and not a clinical cutoff.
            - Scaffold split validation is stronger than random split validation, but still not prospective external validation.
            - Permeability does not determine exposure by itself; solubility, dose, transporters, metabolism, protein binding, formulation, and physiology also matter.
            - The PK/NCA simulator is mechanistic education from assumed parameters, not PBPK prediction.
            """
        )
        st.markdown("#### Scientific boundaries")
        boundary_cols = st.columns(2)
        with boundary_cols[0]:
            st.markdown("**What the app supports**")
            for item in SCIENTIFIC_BOUNDARIES["supports"]:
                st.write(f"- {item}")
        with boundary_cols[1]:
            st.markdown("**What the app does not support**")
            for item in SCIENTIFIC_BOUNDARIES["does_not_support"]:
                st.write(f"- {item}")
        with st.expander("What would be needed for validated human PK prediction?", expanded=True):
            st.markdown(
                """
                A validated human PK model would require observed human PK endpoints such as CL, Vd, half-life, Cmax, and AUC; route, dose, formulation, fed/fasted, and sampling metadata; IVIVE assumptions for clearance and permeability; external test sets; 2-fold or 3-fold prediction-error benchmarks; and prospective validation.
                """
            )

    if prediction is not None and confidence is not None and applicability is not None:
        selected_category_for_report = "Custom molecule"
        if mode == "Example library":
            selected_category_for_report = str(_example_table().set_index("name").loc[selected_name, "category"])
        pk_table = pk_impact_table(float(prediction["high_permeability_probability"]))
        report_text = build_downloadable_report(
            selected_name,
            selected_category_for_report,
            smiles,
            canonical_smiles,
            descriptors,
            prediction,
            confidence,
            applicability,
            pk_table,
        )

        st.markdown("---")
        st.subheader("Report Download")
        rp_col, dl_col = st.columns([1.3, 1.0])
        with rp_col:
            st.markdown(
                '<div class="report-preview">'
                '<h4>Report contents</h4>'
                '<ul>'
                "<li>Molecule identity (name, category, SMILES)</li>"
                "<li>Molecular descriptors (MW, LogP, TPSA, HBD, HBA, rings, Csp3, …)</li>"
                "<li>Caco-2 permeability prediction and class probability</li>"
                "<li>Confidence score and entropy</li>"
                "<li>Applicability-domain category and nearest-neighbor similarity</li>"
                "<li>Explainability summary (descriptor drivers and SHAP interpretation)</li>"
                "<li>Permeability-to-PK impact: F, ka, AUC, Cmax, Tmax, CL/F assumptions</li>"
                "<li>AUC ratio, Cmax ratio, Tmax shift, CL/F ratio (adjusted vs reference)</li>"
                "<li>Core PK equations (AUC = F × Dose / CL; CL/F = Dose / AUC; kel = CL / Vd)</li>"
                "<li>Scientific limitations and model boundaries</li>"
                "<li>References and scientific grounding</li>"
                "</ul>"
                "</div>",
                unsafe_allow_html=True,
            )
        with dl_col:
            st.markdown("#### Download files")
            st.download_button(
                "Download full markdown report",
                report_text,
                file_name="adme_pk_interpretation_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.download_button(
                "Download descriptor CSV",
                _descriptor_dataframe(descriptors).to_csv(index=False),
                file_name="molecular_descriptors.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "Download PK impact CSV",
                pk_table.to_csv(index=False),
                file_name="permeability_pk_impact.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.caption("Reports are generated locally from your session. No data is sent to any server.")

    with st.expander("Feature vector preview"):
        st.json(feature_vector)


def _comparison_rows(selected_labels: list[str]) -> pd.DataFrame:
    examples = _example_table().set_index("label")
    rows = []
    for label in selected_labels:
        entry = examples.loc[label]
        smiles = str(entry["smiles"])
        try:
            analysis = _analyze_smiles(smiles)
        except ValueError:
            continue
        descriptors = dict(analysis["descriptors"])
        prediction, confidence = _prediction_with_confidence(smiles)
        applicability = _cached_applicability(smiles)
        pk_assumptions = None
        if prediction:
            pk_assumptions = permeability_to_pk_assumptions(float(prediction["high_permeability_probability"]))
        rows.append(
            {
                "molecule": str(entry["name"]),
                "category": str(entry["category"]),
                "molecular_weight": float(descriptors["molecular_weight"]),
                "logp": float(descriptors["logp"]),
                "tpsa": float(descriptors["tpsa"]),
                "hbd": int(descriptors["hbd"]),
                "hba": int(descriptors["hba"]),
                "rotatable_bonds": int(descriptors["rotatable_bonds"]),
                "predicted_permeability": prediction["predicted_label"] if prediction else "model unavailable",
                "high_probability": float(prediction["high_permeability_probability"]) if prediction else None,
                "confidence": float(confidence["confidence_score"]) if confidence else None,
                "applicability_similarity": float(applicability["nearest_neighbor_similarity"]) if applicability else None,
                "suggested_f": float(pk_assumptions["scenario_f"]) if pk_assumptions else None,
                "suggested_ka": float(pk_assumptions["scenario_ka"]) if pk_assumptions else None,
            }
        )
    return pd.DataFrame(rows)


def render_comparison_mode() -> None:
    """Render molecule comparison workflow."""
    st.header("Molecule Comparison Mode")
    st.caption("Select 2–5 examples and compare physicochemical descriptors, model output, confidence, and training-domain similarity.")

    examples = _example_table()
    query = st.text_input("Filter comparison library", placeholder="Example: statin, caffeine, warfarin", key="compare_search")
    filtered = examples.copy()
    if query.strip():
        filtered = filtered[filtered["name"].str.contains(query.strip(), case=False, regex=False)]

    default_labels = [
        "Aspirin - Analgesics/NSAIDs",
        "Caffeine - Natural products/cannabinoids",
        "Ibuprofen - Analgesics/NSAIDs",
        "Metformin - PK teaching examples",
        "Propranolol - Cardiovascular drugs",
    ]
    available_defaults = [label for label in default_labels if label in filtered["label"].tolist()]
    selected = st.multiselect(
        "Molecules to compare",
        filtered["label"].tolist(),
        default=available_defaults[:5],
        max_selections=5,
    )
    if len(selected) < 2:
        st.info("Select at least two molecules to compare.")
        return

    comparison = _comparison_rows(selected)
    if comparison.empty:
        st.warning("No comparison rows could be calculated.")
        return

    # --- Summary cards row ---
    favorable = comparison.assign(
        rank_score=comparison["high_probability"].fillna(0) + comparison["confidence"].fillna(0) - comparison["tpsa"] / 300
    )
    most_favorable = favorable.sort_values("rank_score", ascending=False).iloc[0]
    polarity_limited = comparison.sort_values("tpsa", ascending=False).iloc[0]
    highest_confidence = comparison.sort_values("confidence", ascending=False).iloc[0]
    largest_f = comparison.sort_values("suggested_f", ascending=False).iloc[0] if "suggested_f" in comparison and comparison["suggested_f"].notna().any() else None
    largest_ka = comparison.sort_values("suggested_ka", ascending=False).iloc[0] if "suggested_ka" in comparison and comparison["suggested_ka"].notna().any() else None

    sc = st.columns(5)
    sc[0].metric("Most permeability-favorable", str(most_favorable["molecule"]), help="Highest combined score: high probability + confidence − polarity penalty")
    sc[1].metric("Most polarity-limited", str(polarity_limited["molecule"]), help="Highest TPSA — largest polarity-related permeability burden")
    sc[2].metric("Highest model confidence", str(highest_confidence["molecule"]), help="Most decisive prediction from the classifier")
    if comparison["applicability_similarity"].notna().any():
        outside = comparison.sort_values("applicability_similarity", ascending=True).iloc[0]
        sc[3].metric("Lowest domain similarity", str(outside["molecule"]), help="Most distant from training-set chemistry; treat predictions with extra caution")
    if largest_f is not None:
        sc[4].metric("Largest scenario F (educational assumption)", f"{largest_f['molecule']} ({largest_f['suggested_f']:.2f})", help="Highest permeability-mapped oral bioavailability assumption")

    interpretations = comparison_interpretations(comparison)
    st.markdown(_html_card("Beginner interpretation", interpretations["beginner"]), unsafe_allow_html=True)
    st.markdown(_html_card("Pharmaceutics / PhD-level interpretation", interpretations["phd"]), unsafe_allow_html=True)

    if {"Metformin", "Ibuprofen", "Aspirin"}.issubset(set(comparison["molecule"])):
        st.markdown(
            _html_card(
                "ADME triage insight",
                "Metformin is much more polar than ibuprofen and aspirin, with higher hydrogen-bonding burden and lower lipophilicity — consistent with lower passive permeability. "
                "Ibuprofen is more lipophilic and less polar, supporting higher passive diffusion potential. "
                "Aspirin sits in a moderate region where acidity, TPSA, and ionization context matter.",
            ),
            unsafe_allow_html=True,
        )

    # Pre-compute display table once so all tabs and the structure grid can use it
    display_table = _format_comparison_table(comparison)

    # --- Molecule structure grid ---
    st.markdown("#### Selected molecule structures")
    _examples_idx = _example_table().set_index("label")
    _struct_cols = st.columns(min(len(selected), 5))
    for _si, (_label, _col) in enumerate(zip(selected, _struct_cols)):
        try:
            _row = _examples_idx.loc[_label]
            _mol_name = str(_row["name"])
            _mol_smiles = str(_row["smiles"])
            _mol_cat = str(_row["category"])
            _comp_row = comparison[comparison["molecule"] == _mol_name]
            _pred_lbl = str(_comp_row["predicted_permeability"].iloc[0]) if not _comp_row.empty else ""
            _sug_f = float(_comp_row["suggested_f"].iloc[0]) if not _comp_row.empty and _comp_row["suggested_f"].notna().any() else None
            _sug_ka = float(_comp_row["suggested_ka"].iloc[0]) if not _comp_row.empty and _comp_row["suggested_ka"].notna().any() else None
            _card_html = _render_molecule_card_html(
                _mol_name, _mol_smiles, _mol_cat, _pred_lbl, _sug_f, _sug_ka,
                svg_width=240, svg_height=165,
            )
            with _col:
                st.markdown(_card_html, unsafe_allow_html=True)
        except Exception:
            _struct_cols[_si].caption(f"Card unavailable for {_label}")

    comp_tabs = st.tabs(["A. Physicochemical", "B. Model & Trust", "C. PK Assumptions"])

    with comp_tabs[0]:
        st.markdown('<div class="compare-section-header">A. Physicochemical Comparison</div>', unsafe_allow_html=True)
        phys_cols = ["Molecule", "Category", "MW", "LogP", "TPSA", "HBD", "HBA", "Rotatable bonds"]
        phys_avail = [c for c in phys_cols if c in display_table.columns]
        st.dataframe(display_table[phys_avail], hide_index=True, use_container_width=True)
        chart_data = comparison.set_index("molecule")
        phys_chart_cols = st.columns(4)
        with phys_chart_cols[0]:
            st.caption("MW")
            st.bar_chart(chart_data[["molecular_weight"]])
        with phys_chart_cols[1]:
            st.caption("LogP")
            st.bar_chart(chart_data[["logp"]])
        with phys_chart_cols[2]:
            st.caption("TPSA")
            st.bar_chart(chart_data[["tpsa"]])
        with phys_chart_cols[3]:
            st.caption("HBD")
            st.bar_chart(chart_data[["hbd"]])

        most_polar = comparison.sort_values("tpsa", ascending=False).iloc[0]
        most_lipophilic = comparison.sort_values("logp", ascending=False).iloc[0]
        largest = comparison.sort_values("molecular_weight", ascending=False).iloc[0]
        phys_notes = [
            f"Highest TPSA: **{most_polar['molecule']}** ({most_polar['tpsa']:.1f}) — largest polarity-related permeability burden.",
            f"Highest LogP: **{most_lipophilic['molecule']}** ({most_lipophilic['logp']:.2f}) — most lipophilic; consider solubility tradeoffs.",
            f"Largest MW: **{largest['molecule']}** ({largest['molecular_weight']:.1f} Da) — possible size-related diffusion penalty.",
        ]
        for note in phys_notes:
            st.write(f"- {note}")

    with comp_tabs[1]:
        st.markdown('<div class="compare-section-header">B. Model and Trust Comparison</div>', unsafe_allow_html=True)
        trust_cols = ["Molecule", "Predicted class", "High permeability probability", "Confidence", "Applicability similarity"]
        trust_avail = [c for c in trust_cols if c in display_table.columns]
        _style_fn = lambda value: (
            "background-color: #dcfce7; color: #166534;" if value == "high permeability class"
            else ("background-color: #fee2e2; color: #991b1b;" if value == "low permeability class" else "")
        )
        _styled = _safe_style(display_table[trust_avail], _style_fn, "Predicted class")
        st.dataframe(_styled, hide_index=True, use_container_width=True)
        trust_chart_cols = st.columns(3)
        chart_data = comparison.set_index("molecule")
        with trust_chart_cols[0]:
            st.caption("High-class probability")
            st.bar_chart(chart_data[["high_probability"]])
        with trust_chart_cols[1]:
            st.caption("Confidence score")
            st.bar_chart(chart_data[["confidence"]])
        with trust_chart_cols[2]:
            if "applicability_similarity" in chart_data and chart_data["applicability_similarity"].notna().any():
                st.caption("Domain similarity")
                st.bar_chart(chart_data[["applicability_similarity"]])
        if comparison["applicability_similarity"].notna().any():
            lowest_domain = comparison.sort_values("applicability_similarity", ascending=True).iloc[0]
            st.write(
                f"- Lowest domain similarity: **{lowest_domain['molecule']}** ({lowest_domain['applicability_similarity']:.3f}) — treat this prediction with extra caution."
            )

    with comp_tabs[2]:
        st.markdown('<div class="compare-section-header">C. PK Assumption Comparison</div>', unsafe_allow_html=True)
        st.caption("F and ka are mapped from permeability probability under the educational assumption model. True CL is held constant by design.")
        pk_cols = ["Molecule", "Predicted class", "High permeability probability", "Scenario F (educational assumption)", "Scenario ka (1/h)"]
        pk_avail = [c for c in pk_cols if c in display_table.columns]
        st.dataframe(display_table[pk_avail], hide_index=True, use_container_width=True)
        pk_chart_cols = st.columns(2)
        chart_data = comparison.set_index("molecule")
        with pk_chart_cols[0]:
            if "suggested_f" in chart_data and chart_data["suggested_f"].notna().any():
                st.caption("Scenario F (educational assumption)")
                st.bar_chart(chart_data[["suggested_f"]])
        with pk_chart_cols[1]:
            if "suggested_ka" in chart_data and chart_data["suggested_ka"].notna().any():
                st.caption("Suggested ka (absorption rate assumption)")
                st.bar_chart(chart_data[["suggested_ka"]])
        if largest_f is not None:
            st.write(f"- Largest scenario F (educational assumption): **{largest_f['molecule']}** ({largest_f['suggested_f']:.2f}) — highest educational F scenario assumption.")
        if largest_ka is not None:
            st.write(f"- Largest scenario ka (educational assumption): **{largest_ka['molecule']}** ({largest_ka['suggested_ka']:.2f} h⁻¹) — fastest absorption-rate assumption.")
        st.markdown(
            _html_card(
                "How to read this table",
                "Scenario F and ka are illustrative starting assumptions, NOT model-predicted bioavailability values. "
                "They are not measured values. A higher F maps to higher simulated AUC and lower apparent CL/F, "
                "while true CL is unchanged. Higher ka primarily shifts Cmax timing (Tmax) and curve shape.",
            ),
            unsafe_allow_html=True,
        )


def _build_pk_report(
    route: str,
    parameters: dict[str, float | str],
    nca_summary: dict[str, float | str],
    warnings: list[str],
) -> str:
    parameter_lines = [f"- {key}: {value}" for key, value in parameters.items()]
    summary_lines = [f"- {key}: {value}" for key, value in nca_summary.items()]
    warning_lines = [f"- {warning}" for warning in warnings] or ["- None"]
    return "\n".join(
        [
            "# Educational PK/NCA Simulation Report",
            "",
            "This report demonstrates PK/NCA calculations under explicit assumed parameters. It is not validated human PK, PBPK, clinical, regulatory, safety, efficacy, or dose prediction.",
            "",
            f"Route: {route}",
            "",
            "## Assumed Parameters",
            "",
            *parameter_lines,
            "",
            "## NCA Summary",
            "",
            *summary_lines,
            "",
            "## Warnings and Assumptions",
            "",
            *warning_lines,
            "",
            "## Interpretation",
            "",
            "AUC summarizes exposure, AUMC supports MRT/MBRT, and clearance labels depend on route. Oral dosing reports CL/F because bioavailability separates apparent from true systemic clearance.",
        ]
    )


def render_pk_nca_simulator() -> None:
    """Render educational PK/NCA simulator."""
    st.header("Educational PK/NCA Simulator")
    st.caption("One-compartment concentration-time simulation with noncompartmental exposure metrics.")
    st.markdown(
        _html_card(
            "Educational framing",
            "This mini-tool demonstrates how concentration-time profiles and NCA metrics respond to explicit assumptions. It does not convert Caco-2 permeability into validated human PK and must not be used for clinical, regulatory, safety, efficacy, or dose decisions.",
        ),
        unsafe_allow_html=True,
    )

    preset_options = [
        "Oral fast absorption",
        "IV bolus high clearance compound",
        "IV bolus low clearance compound",
        "Oral slow absorption",
        "Flip-flop kinetics example",
        "Insufficient sampling example",
    ]
    preset_col, drug_col = st.columns([1.4, 1])
    with preset_col:
        preset_name = st.selectbox("Teaching preset", preset_options)
    with drug_col:
        drug_options = ["None (use preset)"] + [v["name"] for v in DRUG_PK_PROFILES.values()]
        drug_choice = st.selectbox(
            "Load literature drug profile",
            drug_options,
            help="Loads approximate literature teaching values. NOT a model prediction. Verify before scientific use.",
        )
    preset = PK_PRESETS[preset_name]
    if drug_choice != "None (use preset)":
        _dkey = next(k for k, v in DRUG_PK_PROFILES.items() if v["name"] == drug_choice)
        _dp = DRUG_PK_PROFILES[_dkey]
        st.markdown(
            _html_card(
                f"Literature teaching profile: {_dp['name']}",
                f"Route: {_dp['route']} &nbsp;|&nbsp; Dose: {_dp['teaching_dose_mg']} mg &nbsp;|&nbsp; "
                f"Approx. F: {_dp['approximate_f']} &nbsp;|&nbsp; "
                f"Approx. t½: {_dp['approximate_half_life_h']} h &nbsp;|&nbsp; "
                f"Approx. Vd: {_dp['approximate_vd_l_kg']} L/kg &nbsp;|&nbsp; "
                f"Source: {_dp['source_note']}",
            ),
            unsafe_allow_html=True,
        )
        for _w in _dp["warning_notes"]:
            st.info(f"Teaching note: {_w}")
        preset = {
            "route": _dp["route"],
            "dose": _dp["teaching_dose_mg"],
            "vd": _dp["approximate_vd_l_kg"] * 70.0,
            "kel": _dp["approximate_kel_per_h"],
            "ka": _dp["approximate_ka_per_h"],
            "bioavailability": _dp["approximate_f"],
            "infusion_duration": 1.0,
            "duration": max(24.0, _dp["approximate_half_life_h"] * 6.0),
            "interval": max(0.25, _dp["approximate_half_life_h"] / 20.0),
            "n_terminal_points": 4,
            "method": "linear_up_log_down",
            "note": f"Literature teaching values for {_dp['name']}. {_dp['source_note']}",
        }
    st.markdown(f'<div class="section-note">{preset["note"]}</div>', unsafe_allow_html=True)

    param_cols = st.columns(7)
    with param_cols[0]:
        route = st.selectbox("Route", ["IV bolus", "oral", "IV infusion"], index=["IV bolus", "oral", "IV infusion"].index(str(preset["route"])))
    with param_cols[1]:
        dose = st.number_input("Dose", min_value=0.001, value=float(preset["dose"]), step=10.0)
    with param_cols[2]:
        dose_units = st.selectbox("Units", ["mg", "umol", "arbitrary units"])
    with param_cols[3]:
        vd = st.number_input("Vd", min_value=0.001, value=float(preset["vd"]), step=1.0)
    with param_cols[4]:
        kel = st.number_input("kel", min_value=0.0001, value=float(preset["kel"]), step=0.01, format="%.4f")
    ka = None
    bioavailability = 1.0
    infusion_duration = None
    with param_cols[5]:
        if route == "oral":
            ka = st.number_input("ka", min_value=0.0001, value=float(preset["ka"]), step=0.05, format="%.4f")
        elif route == "IV infusion":
            infusion_duration = st.number_input("Infusion", min_value=0.001, value=float(preset["infusion_duration"]), step=0.5)
        else:
            st.metric("ka", "N/A")
    with param_cols[6]:
        if route == "oral":
            bioavailability = st.slider("F", min_value=0.01, max_value=1.0, value=float(preset["bioavailability"]), step=0.01)
        else:
            st.metric("F", "1.00")
    advanced_cols = st.columns(3)
    duration = advanced_cols[0].number_input("Simulation duration", min_value=0.1, value=float(preset["duration"]), step=1.0)
    interval = advanced_cols[1].number_input("Sampling interval", min_value=0.01, value=float(preset["interval"]), step=0.1)
    n_terminal_points = advanced_cols[2].slider("Terminal points for lambda_z", 3, 6, int(preset["n_terminal_points"]))
    nca_method = st.selectbox("AUC method", ["linear_up_log_down", "linear"], index=["linear_up_log_down", "linear"].index(str(preset["method"])))

    try:
        profile, pk_warnings = simulate_pk_profile(
            route=route,
            dose=dose,
            vd=vd,
            kel=kel,
            duration=duration,
            interval=interval,
            ka=ka,
            bioavailability=bioavailability,
            infusion_duration=infusion_duration,
        )
        nca_summary, nca_warnings = calculate_nca(
            profile,
            dose=dose,
            route=route,
            method=nca_method,
            n_terminal_points=n_terminal_points,
            bioavailability=bioavailability if route == "oral" else None,
        )
    except ValueError as error:
        st.error(str(error))
        return

    warnings = pk_warnings + nca_warnings
    parameters = {
        "route": route,
        "dose": f"{dose} {dose_units}",
        "Vd": vd,
        "kel": kel,
        "ka": ka if ka is not None else "not applicable",
        "F": bioavailability if route == "oral" else "not applicable",
        "infusion_duration": infusion_duration if infusion_duration is not None else "not applicable",
        "duration": duration,
        "interval": interval,
    }

    metric_cols = st.columns(7)
    metric_cols[0].metric("Cmax", _safe_float(nca_summary["cmax"]))
    metric_cols[1].metric("Tmax", _safe_float(nca_summary["tmax"]))
    metric_cols[2].metric("AUCinf", _safe_float(nca_summary["auc_inf"]))
    metric_cols[3].metric("Half-life", _safe_float(nca_summary["half_life"]))
    metric_cols[4].metric("MRT", _safe_float(nca_summary["mrt"]))
    metric_cols[5].metric(str(nca_summary["clearance_label"]), _safe_float(nca_summary["clearance"]))
    metric_cols[6].metric("Vss", _safe_float(nca_summary.get("vss", "N/A")))

    plot_tabs = st.tabs(["Linear plot", "Semi-log plot", "Animated buildup", "Tables", "Equations"])
    with plot_tabs[0]:
        st.pyplot(plot_concentration_time(profile), clear_figure=True)
    with plot_tabs[1]:
        st.pyplot(plot_semilog_concentration_time(profile), clear_figure=True)
    with plot_tabs[2]:
        points = st.slider("Show first N samples", 2, len(profile), min(len(profile), 10))
        st.line_chart(profile.iloc[:points].set_index("time")["concentration"])
        st.caption("Use the slider to build the concentration-time curve step by step.")
    with plot_tabs[3]:
        st.markdown("##### Concentration-time table")
        st.dataframe(profile, hide_index=True, use_container_width=True)
        st.markdown("##### NCA summary")
        st.dataframe(
            pd.DataFrame([{"metric": key, "value": value} for key, value in nca_summary.items()]),
            hide_index=True,
            use_container_width=True,
        )
    with plot_tabs[4]:
        for title, body in [
            ("AUC", "Area under the concentration-time curve; a summary of total exposure in the simulated profile."),
            ("AUMC", "Area under the first moment curve; concentration is weighted by time."),
            ("MRT / MBRT", "Residence-time summaries estimated from AUMC/AUC relationships under NCA assumptions."),
            ("CL vs CL/F", "IV profiles can report CL; oral profiles report apparent CL/F because bioavailability affects exposure."),
            ("Vss assumptions", "Vss is meaningful mainly for IV settings; oral data alone cannot separate F, CL, and distribution."),
            ("Terminal lambda_z", "The terminal slope is estimated from late positive concentrations and drives half-life and extrapolated AUC."),
            ("Percent extrapolated", "High extrapolated AUC means the sampling window may be too short for reliable NCA."),
            ("NCA vs compartmental model", "The simulator generates a compartmental profile, then NCA calculates exposure metrics without refitting that model."),
        ]:
            with st.expander(title):
                st.write(body)

    if warnings:
        st.markdown("#### Interpretation warnings")
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("No major simulation or NCA warnings for these settings.")

    st.markdown("#### Beginner-friendly interpretation")
    st.write(
        "AUC summarizes total simulated exposure. AUMC weights that exposure by time, which supports residence-time calculations. "
        "The terminal slope depends on late samples, so sparse or short sampling can distort half-life and extrapolated AUC."
    )
    if route == "oral":
        st.write("For oral dosing, the app reports CL/F because observed exposure combines systemic clearance and bioavailability.")

    concentration_csv = profile.to_csv(index=False)
    nca_csv = pd.DataFrame([nca_summary]).to_csv(index=False)
    report_text = _build_pk_report(route, parameters, nca_summary, warnings)
    download_cols = st.columns(3)
    download_cols[0].download_button(
        "Download concentration CSV",
        concentration_csv,
        file_name="pk_concentration_time.csv",
        mime="text/csv",
        use_container_width=True,
    )
    download_cols[1].download_button(
        "Download NCA summary CSV",
        nca_csv,
        file_name="nca_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )
    download_cols[2].download_button(
        "Download PK/NCA report",
        report_text,
        file_name="pk_nca_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

    # -----------------------------------------------------------------------
    # Multi-Drug PK Curve Comparison (2–5 drugs on one plot)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.subheader("Compare 2–5 Drugs on PK Curves")
    st.caption(
        "Overlay concentration-time curves for 2–5 drugs using the educational assumption framework. "
        "No observed clinical data are bundled — all curves are educational simulations."
    )

    _mdpk_drug_options = [v["name"] for v in DRUG_PK_PROFILES.values()]
    _mdpk_col1, _mdpk_col2 = st.columns([1.3, 1])
    with _mdpk_col1:
        _mdpk_selected = st.multiselect(
            "Select 2–5 drugs for comparison",
            _mdpk_drug_options,
            default=_mdpk_drug_options[:3],
            max_selections=5,
            key="pknca_mdpk_select",
        )
    with _mdpk_col2:
        _mdpk_mode = st.radio(
            "Curve mode",
            ["A: Permeability-derived F/ka", "B: Literature teaching preset", "C: Common preset parameters"],
            key="pknca_mdpk_mode",
        )
        if _mdpk_selected:
            _mdpk_ref = st.selectbox("Reference drug for ratios", _mdpk_selected, key="pknca_mdpk_ref")
        else:
            _mdpk_ref = None

    if len(_mdpk_selected) >= 2 and _mdpk_ref:
        # Common parameters for mode A/C
        _mdpk_common_dose = 100.0
        _mdpk_common_vd = 40.0
        _mdpk_common_cl = 6.0

        _mdpk_profiles: dict[str, pd.DataFrame] = {}
        _mdpk_rows: list[dict] = []

        for _drug_name in _mdpk_selected:
            _dkey = next((k for k, v in DRUG_PK_PROFILES.items() if v["name"] == _drug_name), None)
            if _dkey is None:
                continue
            _dp = DRUG_PK_PROFILES[_dkey]

            if "B" in _mdpk_mode:
                _f = float(_dp["approximate_f"])
                _ka = float(_dp["approximate_ka_per_h"])
                _vd = float(_dp["approximate_vd_l_kg"]) * 70.0
                _kel = float(_dp["approximate_kel_per_h"])
                _dose = float(_dp["teaching_dose_mg"])
                _cl = _kel * _vd
                _label = f"{_drug_name} (lit.)"
            elif "A" in _mdpk_mode:
                _smi = _dp.get("smiles", "")
                _pred_tmp, _ = _prediction_with_confidence(_smi) if _smi else (None, None)
                _prob_tmp = float(_pred_tmp["high_permeability_probability"]) if _pred_tmp else 0.5
                _assumptions_tmp = permeability_to_pk_assumptions(_prob_tmp)
                _f = _assumptions_tmp["adjusted_f"]
                _ka = _assumptions_tmp["adjusted_ka"]
                _vd = _mdpk_common_vd
                _cl = _mdpk_common_cl
                _kel = _cl / _vd
                _dose = _mdpk_common_dose
                _label = f"{_drug_name} (perm.)"
            else:
                _f = _dp.get("approximate_f", 0.7)
                _ka = _dp.get("approximate_ka_per_h", 1.0)
                _vd = _mdpk_common_vd
                _cl = _mdpk_common_cl
                _kel = _cl / _vd
                _dose = _mdpk_common_dose
                _label = f"{_drug_name} (common)"

            try:
                _p, _ = simulate_pk_profile(
                    route="oral", dose=_dose, vd=_vd, kel=_kel,
                    duration=48.0, interval=0.5, ka=_ka, bioavailability=_f,
                )
                _n, _ = calculate_nca(_p, dose=_dose, route="oral", bioavailability=_f)
                _mdpk_profiles[_label] = _p.set_index("time")["concentration"].rename(_label)
                _mdpk_rows.append({
                    "drug": _drug_name, "mode": _mdpk_mode[0],
                    "F": _f, "ka": _ka, "Vd": _vd, "true_CL": _cl,
                    "auc": float(_n["auc_inf"]), "cmax": float(_n["cmax"]),
                    "tmax": float(_n["tmax"]), "clf": float(_n["clearance"]),
                    "half_life": float(_n["half_life"]),
                })
            except Exception:
                pass

        if _mdpk_profiles and _mdpk_rows:
            from adme_predictor.fold_change import compute_drug_ratios, multi_drug_interpretation  # noqa: PLC0415

            _mdpk_df = pd.DataFrame(_mdpk_rows).rename(columns={"drug": "molecule"})
            _mdpk_df = compute_drug_ratios(_mdpk_df, _mdpk_ref)

            # Overlay plots
            _overlay_df = pd.DataFrame(_mdpk_profiles)
            _overlay_df.index.name = "time (h)"
            _pk_tabs = st.tabs(["Linear C-t overlay", "Semi-log C-t overlay", "Parameters", "Ratios vs reference"])
            with _pk_tabs[0]:
                st.line_chart(_overlay_df)
                st.caption(
                    f"Mode: {_mdpk_mode[0]}. "
                    "All curves are educational simulations — not observed clinical PK data. "
                    + ("Literature teaching preset values are approximate; verify before scientific use." if "B" in _mdpk_mode else "")
                )
            with _pk_tabs[1]:
                _semi_df = np.log10(_overlay_df.clip(lower=1e-10))
                st.line_chart(_semi_df)
                st.caption("Semi-log scale (log₁₀ concentration). Parallel terminal slopes = same true CL by design (Mode A/C).")
            with _pk_tabs[2]:
                _param_disp = _mdpk_df[["molecule", "mode", "F", "ka", "Vd", "true_CL", "auc", "cmax", "tmax", "clf", "half_life"]].rename(columns={
                    "molecule": "Drug", "mode": "Mode", "auc": "AUC", "cmax": "Cmax",
                    "tmax": "Tmax", "clf": "CL/F", "half_life": "t½ (h)", "true_CL": "True CL",
                })
                for col in ["F", "ka", "Vd", "True CL", "AUC", "Cmax", "Tmax", "CL/F", "t½ (h)"]:
                    if col in _param_disp:
                        _param_disp[col] = _param_disp[col].map(lambda v: round(float(v), 3) if pd.notna(v) else None)
                st.dataframe(_param_disp, hide_index=True, use_container_width=True)
                st.warning("True CL is fixed across drugs in Mode A and C. Differences in AUC reflect F only.")
            with _pk_tabs[3]:
                _ratio_cols = ["molecule", "F", "ka", "auc_ratio", "cmax_ratio", "tmax_shift", "clf_ratio"]
                _ratio_avail = [c for c in _ratio_cols if c in _mdpk_df.columns]
                _ratio_disp = _mdpk_df[_ratio_avail].rename(columns={
                    "molecule": "Drug", "auc_ratio": "AUC ratio", "cmax_ratio": "Cmax ratio",
                    "tmax_shift": "Tmax shift (h)", "clf_ratio": "CL/F ratio",
                })
                for col in ["F", "ka", "AUC ratio", "Cmax ratio", "Tmax shift (h)", "CL/F ratio"]:
                    if col in _ratio_disp:
                        _ratio_disp[col] = _ratio_disp[col].map(lambda v: round(float(v), 3) if pd.notna(v) else None)
                st.dataframe(_ratio_disp, hide_index=True, use_container_width=True)
                st.caption(f"All ratios vs reference drug: {_mdpk_ref}. AUC_ratio = F_drug/F_ref under fixed dose/Vd/CL.")

            _interps = multi_drug_interpretation(_mdpk_df, _mdpk_ref)
            st.markdown(_html_card("Beginner interpretation", _interps["beginner"]), unsafe_allow_html=True)
            st.markdown(_html_card("Pharmaceutics / PhD-level interpretation", _interps["phd"]), unsafe_allow_html=True)

    elif len(_mdpk_selected) < 2:
        st.info("Select at least 2 drugs to enable the overlay comparison.")


_MULTI_DRUG_DEFAULTS = [
    "Aspirin - Analgesics/NSAIDs",
    "Ibuprofen - Analgesics/NSAIDs",
    "Metformin - PK teaching examples",
    "Propranolol - Cardiovascular drugs",
    "Caffeine - Natural products/cannabinoids",
]


def render_multi_drug_pk_comparison() -> None:
    """Render multi-drug PK impact comparison page."""
    st.header("Multi-Drug PK Impact Comparison")
    st.caption(
        "Select 2–5 molecules to compare permeability-informed oral PK curve shifts side-by-side. "
        "All curves are educational simulations — not observed clinical PK data."
    )

    st.markdown(
        _html_card(
            "Scientific framing",
            "For each selected molecule, the ML Caco-2 probability maps to adjusted F and ka under the "
            "educational assumption model. Dose, Vd, and true CL are held constant. "
            "Differences in AUC across drugs are driven entirely by assumed F "
            "(AUC<sub>oral</sub> = F &times; Dose / CL). "
            "Differences in Cmax and Tmax are driven by ka."
            "<br><strong>No observed clinical PK data are bundled. All curves are educational.</strong>",
        ),
        unsafe_allow_html=True,
    )

    examples = _example_table()
    query = st.text_input("Filter molecule library", placeholder="aspirin, metformin, warfarin …", key="mdpk_search")
    filtered = examples.copy()
    if query.strip():
        filtered = filtered[filtered["name"].str.contains(query.strip(), case=False, regex=False)]

    available_defaults = [lbl for lbl in _MULTI_DRUG_DEFAULTS if lbl in filtered["label"].tolist()]
    selected = st.multiselect(
        "Molecules to compare",
        filtered["label"].tolist(),
        default=available_defaults[:4],
        max_selections=5,
        key="mdpk_select",
    )
    if len(selected) < 2:
        st.info("Select at least 2 molecules to start the comparison.")
        return

    # Build entries list
    examples_idx = _example_table().set_index("label")
    entries = []
    lit_profile_names = []
    for label in selected:
        try:
            row = examples_idx.loc[label]
            mol_name = str(row["name"])
            smiles = str(row["smiles"])
            pred, _conf = _prediction_with_confidence(smiles)
            prob = float(pred["high_permeability_probability"]) if pred else 0.5
            entries.append({"name": mol_name, "probability": prob})
            if mol_name.lower() in {k.lower() for k in DRUG_PK_PROFILES}:
                lit_profile_names.append(mol_name)
        except Exception:
            continue

    if not entries:
        st.warning("Could not compute predictions for selected molecules.")
        return

    with st.spinner("Computing PK profiles …"):
        metrics, profiles = multi_drug_pk_comparison(entries)

    if metrics.empty:
        st.warning("PK comparison returned no results.")
        return

    # --- Heatmap-style summary table ---
    st.markdown("#### Exposure ratio summary")
    _scen_f_col = "scenario_f" if "scenario_f" in metrics.columns else "suggested_f"
    _scen_ka_col = "scenario_ka" if "scenario_ka" in metrics.columns else "suggested_ka"
    _avail_cols = [c for c in ["molecule", "probability", _scen_f_col, _scen_ka_col,
         "auc_ratio", "cmax_ratio", "tmax_shift", "clf_ratio", "true_cl"] if c in metrics.columns]
    display_metrics = metrics[_avail_cols].rename(columns={
        "molecule": "Molecule", "probability": "Probability",
        _scen_f_col: "Scenario F (educational assumption)", _scen_ka_col: "Scenario ka (h⁻¹)",
        "auc_ratio": "AUC sensitivity ratio", "cmax_ratio": "Cmax sensitivity ratio",
        "tmax_shift": "Tmax shift (h)", "clf_ratio": "CL/F sensitivity ratio",
        "true_cl": "True CL (fixed)",
    })
    for col in ["Probability", "Scenario F (educational assumption)", "Scenario ka (h⁻¹)",
                "AUC sensitivity ratio", "Cmax sensitivity ratio", "Tmax shift (h)", "CL/F sensitivity ratio"]:
        if col in display_metrics:
            display_metrics[col] = display_metrics[col].map(
                lambda v: None if pd.isna(v) else round(float(v), 3)
            )
    st.dataframe(display_metrics, hide_index=True, use_container_width=True)

    # --- Ratio bar charts ---
    ratio_cols = st.columns(3)
    chart_data = metrics.set_index("molecule")
    with ratio_cols[0]:
        st.caption("AUC ratio (adj / ref)")
        st.bar_chart(chart_data[["auc_ratio"]])
    with ratio_cols[1]:
        st.caption("Cmax ratio (adj / ref)")
        st.bar_chart(chart_data[["cmax_ratio"]])
    with ratio_cols[2]:
        st.caption("CL/F ratio (adj / ref)")
        st.bar_chart(chart_data[["clf_ratio"]])

    # --- Overlay concentration-time curves ---
    if profiles:
        st.markdown("#### Overlay concentration-time curves")
        overlay_tabs = st.tabs(["All drugs — reference overlay", "All drugs — adjusted overlay"])
        ref_curves = {}
        adj_curves = {}
        for name, merged in profiles.items():
            ref_col = f"{name} (ref)"
            adj_col = f"{name} (adj)"
            if ref_col in merged.columns:
                ref_curves[name] = merged.set_index("time")[ref_col]
            if adj_col in merged.columns:
                adj_curves[name] = merged.set_index("time")[adj_col]

        with overlay_tabs[0]:
            if ref_curves:
                ref_df = pd.DataFrame(ref_curves)
                ref_df.index.name = "time"
                st.line_chart(ref_df)
                st.caption("Reference educational scenario for all selected drugs (F = 0.80, ka = 1.20 h⁻¹).")
        with overlay_tabs[1]:
            if adj_curves:
                adj_df = pd.DataFrame(adj_curves)
                adj_df.index.name = "time"
                st.line_chart(adj_df)
                st.caption("Permeability-adjusted educational scenario (F and ka scaled from model probability).")

    # --- Literature teaching preset note ---
    if lit_profile_names:
        st.markdown(
            _html_card(
                "Literature teaching presets available",
                f"<strong>{', '.join(lit_profile_names)}</strong> have curated approximate literature teaching "
                "profiles in this platform. Switch to the PK/NCA Simulator and select a drug profile to load "
                "those approximate values. They are labeled as teaching presets and are NOT observed clinical PK data.",
            ),
            unsafe_allow_html=True,
        )

    # --- Observed data notice ---
    st.info(
        "No observed concentration-time data are bundled for any molecule. "
        "All curves shown are educational simulations from permeability-mapped F/ka assumptions. "
        "For drugs where literature teaching presets exist, use the PK/NCA Simulator to load those approximate values."
    )

    # --- Interpretations ---
    st.markdown(
        _html_card(
            "Beginner interpretation",
            "Drugs with higher assumed F have higher simulated AUC because more of the oral dose reaches "
            "systemic circulation. Drugs with faster ka rise earlier and may reach a higher peak concentration. "
            "True systemic CL is the same for all drugs in this comparison by design.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        _html_card(
            "Pharmaceutics / PhD-level interpretation",
            "Under fixed dose, Vd, and true CL, differences in AUC are driven primarily by F "
            "(AUC<sub>oral</sub> = F &times; Dose / CL). Differences in ka alter absorption-rate-limited "
            "curve shape, influencing Cmax and Tmax. Apparent CL/F varies inversely with AUC, while true CL "
            "remains fixed unless explicitly changed. The F and ka values here are hypothesis-mapped from "
            "Caco-2 probability and are not measured or validated.",
        ),
        unsafe_allow_html=True,
    )

    # --- Per-drug experiment recommendations ---
    with st.expander("Per-drug experiment recommendations", expanded=False):
        for entry in entries:
            mol_name = str(entry["name"])
            try:
                mol_row = examples_idx.loc[[lbl for lbl in selected if mol_name in lbl][0]]
                mol_smiles = str(mol_row["smiles"])
                mol_pred, mol_conf = _prediction_with_confidence(mol_smiles)
                mol_appl = _cached_applicability(mol_smiles)
                mol_analysis = _analyze_smiles(mol_smiles)
                mol_desc = dict(mol_analysis["descriptors"])
                if mol_pred and mol_conf and mol_appl:
                    rec = experiment_recommendation(
                        name=mol_name,
                        probability=float(mol_pred["high_permeability_probability"]),
                        confidence_cat=str(mol_conf["confidence_category"]),
                        domain_cat=str(mol_appl["applicability_category"]),
                        outside_domain=bool(mol_appl["outside_applicability_domain"]),
                        descriptors=mol_desc,
                    )
                    st.markdown(f"**{mol_name}**")
                    st.write(f"Beginner: {rec['beginner']}")
                    st.caption(f"PhD level: {rec['phd']}")
            except Exception:
                st.caption(f"Recommendation unavailable for {mol_name}")

    # --- Report download ---
    st.markdown("---")
    report_md = build_multi_drug_comparison_report(metrics, lit_profile_names)
    st.download_button(
        "Download multi-drug comparison report (markdown)",
        report_md,
        file_name="multi_drug_pk_comparison.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.download_button(
        "Download metrics CSV",
        metrics.drop(columns=["molecule"], errors="ignore").to_csv(index=True),
        file_name="multi_drug_pk_metrics.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.caption(MULTI_DRUG_COMPARISON_DISCLAIMER)


def render_evidence_library() -> None:
    """Render project evidence and documentation summary."""
    st.header("Evidence, Documentation, and Responsible Use")
    st.markdown(
        "This page summarizes project artifacts: dataset documentation, model reports, "
        "scaffold split comparison, SHAP interpretation, outlier analysis, and PK/NCA methods."
    )

    # --- AI recruiter / product summary ---
    with st.expander("Why this project matters for AI-health and pharma AI", expanded=True):
        recruiter_items = [
            ("Real biomedical data", "Caco-2 Wang public benchmark — 906 experimentally measured molecules"),
            ("Molecular featurization", "RDKit descriptors (MW, logP, TPSA, HBD/HBA, rotatable bonds, rings, Csp3) + Morgan fingerprints"),
            ("ML prediction", "Random Forest and XGBoost classifiers with probability output"),
            ("Validation beyond random split", "Bemis-Murcko scaffold split — test molecules have chemically distinct cores from training"),
            ("Uncertainty quantification", "Binary entropy confidence scoring + probability margin"),
            ("Applicability-domain checks", "Morgan/Tanimoto nearest-neighbor similarity to training set with explicit warnings"),
            ("Explainable AI", "Descriptor driver analysis, SHAP-style interpretation, local driver bar charts"),
            ("Multi-drug comparison", "Select 2-5 molecules, compare AUC/Cmax/CL-F ratios under permeability-informed assumptions"),
            ("Experiment recommendation engine", "Rule-based per-molecule follow-up guidance for Caco-2, solubility, transporter assays"),
            ("Scientific safety boundaries", "No clinical, PBPK, dose, safety, or regulatory claim; explicit educational framing throughout"),
            ("Deployed UI", "Streamlit Cloud deployment with professional pharma-style interface"),
            ("Report generation", "Downloadable markdown + CSV reports per molecule and multi-drug comparison"),
            ("Educational PK simulation", "One-compartment NCA + permeability-to-PK impact with editable assumptions"),
            ("Modular Python package", f"Tested: 90+ unit tests covering scientific correctness and software correctness"),
        ]
        r_col1, r_col2 = st.columns(2)
        for i, (title, detail) in enumerate(recruiter_items):
            col = r_col1 if i % 2 == 0 else r_col2
            col.markdown(
                f'<div class="premium-card" style="margin-bottom:0.4rem;">'
                f'<h3 style="font-size:0.92rem;margin:0 0 0.2rem 0;">{title}</h3>'
                f'<p style="font-size:0.84rem;margin:0;">{detail}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # --- Model Trust & Engineering panel ---
    with st.expander("Model Trust and Engineering", expanded=True):
        trust_rows = [
            ("Dataset", "TDC Caco-2 Wang benchmark, 906 processed molecules, experimentally measured log(Papp)"),
            ("Model type", "Trained XGBoost / Random Forest classifier and regressor"),
            ("Validation", "Random split AND Bemis-Murcko scaffold split — two modes reported side by side"),
            ("Explainability", "SHAP global + local feature attribution; descriptor driver bar chart"),
            ("Uncertainty", "Classifier probability confidence (margin from 0.5) + prediction entropy"),
            ("Applicability domain", "Morgan fingerprint Tanimoto similarity to nearest training neighbor"),
            ("Class threshold", "Dataset median log(Papp) — not a clinical cutoff"),
            ("Deployment", "Streamlit Cloud — cached inference, SVG molecule rendering, downloadable reports"),
            ("Testing", f"90+ automated pytest tests — scientific correctness + software correctness"),
            ("Report export", "Markdown report + descriptor CSV + PK impact CSV per molecule"),
            ("Limitations", "Caco-2 only; no validated human PK, PBPK, clinical, regulatory, or dose claim"),
        ]
        _t1, _t2 = st.columns(2)
        for i, (k, v) in enumerate(trust_rows):
            (_t1 if i % 2 == 0 else _t2).markdown(
                f'<div class="premium-card" style="margin-bottom:0.35rem;">'
                f'<h3 style="font-size:0.9rem;margin:0 0 0.15rem 0;">{k}</h3>'
                f'<p style="font-size:0.82rem;margin:0;">{v}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with st.expander("Reviewer Summary", expanded=False):
        reviewer_cols = st.columns(3)
        reviewer_cols[0].markdown(
            _html_card("AI/ML recruiter", REVIEWER_SUMMARY["ai_ml_recruiter"]),
            unsafe_allow_html=True,
        )
        reviewer_cols[1].markdown(
            _html_card("Computational pharmacology scientist", REVIEWER_SUMMARY["computational_pharmacology"]),
            unsafe_allow_html=True,
        )
        reviewer_cols[2].markdown(
            _html_card("Academic PI / PK reviewer", REVIEWER_SUMMARY["academic_pi"]),
            unsafe_allow_html=True,
        )
    with st.expander("External validation roadmap toward human PK", expanded=False):
        st.markdown(
            "A validated human PK predictor would require observed human PK endpoints including CL, Vd, "
            "half-life, Cmax, and AUC; route, dose, formulation, population, fed/fasted, and sampling metadata; "
            "IVIVE assumptions for clearance and permeability; an external test set; 2-fold or 3-fold "
            "prediction-error benchmarks; and prospective validation. "
            "This app intentionally stops at Caco-2 permeability screening and educational PK/NCA simulation."
        )
    docs = [
        ("Architecture", PROJECT_ROOT / "docs" / "architecture.md"),
        ("Beginner usage guide", PROJECT_ROOT / "docs" / "beginner_usage_guide.md"),
        ("Model card", PROJECT_ROOT / "docs" / "model_card.md"),
        ("Technical report", PROJECT_ROOT / "reports" / "technical_report.md"),
        ("Scaffold split comparison", PROJECT_ROOT / "reports" / "scaffold_split_comparison.md"),
        ("SHAP interpretation", PROJECT_ROOT / "reports" / "shap_interpretation.md"),
        ("PK/NCA methods", PROJECT_ROOT / "reports" / "pk_nca_methods.md"),
    ]
    for title, path in docs:
        with st.expander(title):
            if path.exists():
                text = path.read_text(encoding="utf-8")
                st.markdown(text[:5000])
                if len(text) > 5000:
                    st.caption("Preview truncated in the app; full file is available in the repository.")
            else:
                st.info(f"{path.name} is not available in this checkout.")


def main() -> None:
    """Render the app."""
    st.set_page_config(
        page_title="Explainable AI ADME-PK Platform",
        page_icon="🧬",
        layout="wide",
    )
    _inject_css()

    with st.sidebar:
        st.title("ADME-PK Platform")
        st.caption("Explainable screening and PK/NCA education")
        with st.expander("How to use this app", expanded=True):
            for index, step in enumerate(HOW_TO_USE_STEPS, start=1):
                st.write(f"{index}. {step}")
        explanation_level = st.selectbox(
            "Explanation level",
            ["Beginner", "Pharmaceutics graduate student", "PI / PK reviewer", "AI/ML recruiter"],
        )
        st.caption(explanation_for_level(explanation_level))
        page = st.radio(
            "Navigate",
            [
                "ADME Workbench",
                "Molecule Comparison",
                "Multi-Drug PK",
                "PK/NCA Simulator",
                "Evidence & Limits",
            ],
        )
        st.divider()
        st.markdown("#### Model Trust")
        st.caption("Dataset: Caco-2 Wang, 906 mol")
        st.caption("Validation: random + scaffold split")
        st.caption("Explainability: SHAP / descriptor drivers")
        st.caption("Domain check: Morgan/Tanimoto similarity")
        st.caption("Tests: 90+ automated")
        st.divider()
        st.markdown("#### App health")
        for item in check_app_health().values():
            st.write(f"{health_icon(item['level'])} {item['message']}")
        st.divider()
        st.metric("Example molecules", EXAMPLE_MOLECULE_COUNT)
        st.metric("Example categories", len(EXAMPLE_CATEGORIES))
        st.caption("All examples are stored as RDKit-canonicalized SMILES.")

    _render_hero()
    _render_scientific_boundary()
    _render_learning_panel()

    if page == "ADME Workbench":
        render_adme_screening()
    elif page == "Molecule Comparison":
        render_comparison_mode()
    elif page == "Multi-Drug PK":
        render_multi_drug_pk_comparison()
    elif page == "PK/NCA Simulator":
        render_pk_nca_simulator()
    else:
        render_evidence_library()


if __name__ == "__main__":
    main()
