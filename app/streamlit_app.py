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
    HOW_TO_USE_STEPS,
    IVIVE_EXPLANATION,
    IV_ORAL_EXPLANATION,
    PK_EQUATIONS_TEXT,
    REFERENCES,
    REVIEWER_SUMMARY,
    SCIENTIFIC_BOUNDARIES,
    WHAT_THIS_APP_DOES,
    build_downloadable_report,
    comparison_interpretations,
    explanation_for_level,
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
from adme_predictor.reporting import render_molecule_svg  # noqa: E402


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
            "suggested_f": "Suggested F",
            "suggested_ka": "Suggested ka (1/h)",
        }
    )
    numeric_cols = [
        "MW", "LogP", "TPSA",
        "High permeability probability", "Confidence", "Applicability similarity",
        "Suggested F", "Suggested ka (1/h)",
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
        components.html(svg, height=315)
        st.caption("2D molecular structure rendered as SVG")
    else:
        try:
            analysis = _analyze_smiles(smiles)
            descriptors = dict(analysis["descriptors"])
            st.markdown("#### Structure preview")
            st.code(str(analysis["canonical_smiles"]), language="text")
            st.caption(
                "Renderer unavailable here; descriptor summary remains available for interpretation."
            )
            st.metric("MW", _metric_number(descriptors.get("molecular_weight"), 1))
            st.metric("TPSA", _metric_number(descriptors.get("tpsa"), 1))
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

    workflow_tabs = st.tabs(
        [
            "Descriptors",
            "Permeability",
            "Confidence",
            "Applicability Domain",
            "Explainable AI",
            "PK Impact",
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
        st.markdown(_html_card("Global vs local explanation", "Global feature importance summarizes broad model behavior across samples. Local explanation asks which features are most relevant for a selected molecule. SHAP explains model behavior, not causal biology."), unsafe_allow_html=True)
        st.markdown("#### Descriptor driver table")
        st.dataframe(_feature_importance_table(descriptors), hide_index=True, use_container_width=True)
        st.markdown(
            _html_card(
                "What this suggests chemically",
                "High TPSA and hydrogen-bonding capacity usually reduce passive permeability; logP can support membrane partitioning but may introduce solubility issues; molecular weight and flexibility can reduce diffusion efficiency.",
            ),
            unsafe_allow_html=True,
        )
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
            st.info("The descriptor driver table above provides the lightweight interpretability view for this deployment. Optional saved SHAP figures can be generated offline for deeper model-audit materials.")

    with workflow_tabs[5]:
        st.subheader("Permeability to PK Impact — Centerpiece Analysis")
        if prediction is None:
            st.info("Run a permeability prediction first to see PK impact analysis.")
        else:
            probability = float(prediction["high_permeability_probability"])
            assumptions = permeability_to_pk_assumptions(probability)

            # --- Molecule summary banner ---
            conf_cat = str(confidence["confidence_category"]) if confidence else "N/A"
            dom_cat = str(applicability["applicability_category"]) if applicability else "N/A"
            st.markdown(
                _html_card(
                    f"Selected molecule: {selected_name}",
                    f"Predicted class: <strong>{prediction['predicted_label']}</strong> &nbsp;|&nbsp; "
                    f"Probability: <strong>{probability:.2f}</strong> &nbsp;|&nbsp; "
                    f"Confidence: <strong>{conf_cat}</strong> &nbsp;|&nbsp; "
                    f"Domain: <strong>{dom_cat}</strong>",
                ),
                unsafe_allow_html=True,
            )

            # --- Equation card ---
            eq_col, map_col = st.columns([1, 1.6])
            with eq_col:
                st.markdown(
                    _html_card(
                        "Core equations",
                        "AUC<sub>oral</sub> = F &times; Dose / CL<br>"
                        "CL/F = Dose / AUC<br>"
                        "k<sub>el</sub> = CL / Vd<br>"
                        "<small>True CL is held constant by design.</small>",
                    ),
                    unsafe_allow_html=True,
                )
            with map_col:
                st.markdown(
                    _html_card(
                        "Default assumption mapping",
                        f"Permeability probability <strong>{probability:.2f}</strong> &rarr; "
                        f"Adjusted F = <strong>{assumptions['adjusted_f']:.2f}</strong>, "
                        f"Adjusted ka = <strong>{assumptions['adjusted_ka']:.2f} h⁻¹</strong>. "
                        "Edit the parameters below to explore alternative scenarios.",
                    ),
                    unsafe_allow_html=True,
                )

            # --- Editable assumption parameters ---
            st.markdown("#### Editable scenario parameters")
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
                "Ref F", 0.01, 1.0, float(assumptions["reference_f"]), step=0.01, key=f"pki_rf_{_key}"
            )
            pk_ref_ka = pcols[4].number_input(
                "Ref ka (1/h)", 0.001, 20.0, float(assumptions["reference_ka"]),
                format="%.3f", step=0.1, key=f"pki_rka_{_key}"
            )
            pk_adj_f = pcols[5].slider(
                "Adj F", 0.01, 1.0, float(assumptions["adjusted_f"]), step=0.01, key=f"pki_af_{_key}"
            )
            pk_adj_ka = pcols[6].number_input(
                "Adj ka (1/h)", 0.001, 20.0, float(assumptions["adjusted_ka"]),
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

                # --- Metric cards ---
                st.markdown("#### Key exposure metrics")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("True CL (L/h)", f"{pk_cl:.2f}", help="Fixed by design; permeability does not change true systemic clearance.")
                    st.metric("Ref AUC", f"{_ref_auc:.2f}")
                    st.metric("Adj AUC", f"{_adj_auc:.2f}")
                with m2:
                    st.metric("AUC ratio", f"{_auc_ratio:.3f}", delta=f"{_auc_ratio - 1:.3f}")
                    st.metric("Cmax ratio", f"{_cmax_ratio:.3f}", delta=f"{_cmax_ratio - 1:.3f}")
                    st.metric("Tmax shift (h)", f"{_tmax_shift:.2f}")
                with m3:
                    st.metric("Ref CL/F", f"{_ref_clf:.2f}")
                    st.metric("Adj CL/F", f"{_adj_clf:.2f}")
                    st.metric("CL/F ratio", f"{_clf_ratio:.3f}", delta=f"{_clf_ratio - 1:.3f}")

                # --- Plots ---
                _curve_data = pd.merge(
                    _ref_prof.rename(columns={"concentration": "Reference"})[["time", "Reference"]],
                    _adj_prof.rename(columns={"concentration": "Permeability-adjusted"})[["time", "Permeability-adjusted"]],
                    on="time",
                )
                _curve_data = _curve_data.set_index("time")
                pk_plot_tabs = st.tabs(["Linear C-t curve", "Semi-log C-t curve", "Scenario table"])
                with pk_plot_tabs[0]:
                    st.line_chart(_curve_data)
                    st.caption("Concentration-time curves for reference vs permeability-adjusted absorption assumptions.")
                with pk_plot_tabs[1]:
                    _semi = _curve_data.copy()
                    for _c in _semi.columns:
                        _semi[_c] = np.log10(_semi[_c].clip(lower=1e-10))
                    st.line_chart(_semi)
                    st.caption("Semi-log scale (log10 concentration); reveals terminal slope more clearly.")
                with pk_plot_tabs[2]:
                    _scenario_table = pd.DataFrame({
                        "Parameter": ["F", "ka (1/h)", "AUC", "Cmax", "Tmax", "True CL", "CL/F"],
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
                    })
                    st.dataframe(_scenario_table, hide_index=True, use_container_width=True)

                # --- Interpretation cards ---
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

                # --- Warning banner ---
                st.warning(
                    "This is an educational scenario, not a validated human PK prediction. "
                    "F and ka are assumption-mapped from permeability class, not measured. "
                    "True CL remains fixed unless you edit it above. "
                    "Transporters, solubility, first-pass metabolism, protein binding, and formulation also matter."
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
        download_cols = st.columns(3)
        download_cols[0].download_button(
            "Download markdown report",
            report_text,
            file_name="adme_pk_interpretation_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
        download_cols[1].download_button(
            "Download descriptor CSV",
            _descriptor_dataframe(descriptors).to_csv(index=False),
            file_name="molecular_descriptors.csv",
            mime="text/csv",
            use_container_width=True,
        )
        download_cols[2].download_button(
            "Download PK impact CSV",
            pk_table.to_csv(index=False),
            file_name="permeability_pk_impact.csv",
            mime="text/csv",
            use_container_width=True,
        )

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
                "suggested_f": float(pk_assumptions["adjusted_f"]) if pk_assumptions else None,
                "suggested_ka": float(pk_assumptions["adjusted_ka"]) if pk_assumptions else None,
            }
        )
    return pd.DataFrame(rows)


def render_comparison_mode() -> None:
    """Render molecule comparison workflow."""
    st.header("Molecule Comparison Mode")
    st.caption("Select 2-5 examples and compare physicochemical descriptors, model output, confidence, and training-domain similarity.")

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

    display_table = _format_comparison_table(comparison)
    st.dataframe(
        display_table.style.applymap(
            lambda value: "background-color: #dcfce7; color: #166534;" if value == "high permeability class" else (
                "background-color: #fee2e2; color: #991b1b;" if value == "low permeability class" else ""
            ),
            subset=["Predicted class"],
        ),
        hide_index=True,
        use_container_width=True,
    )

    chart_data = comparison.set_index("molecule")
    chart_cols = st.columns(7)
    with chart_cols[0]:
        st.markdown("#### MW")
        st.bar_chart(chart_data[["molecular_weight"]])
    with chart_cols[1]:
        st.markdown("#### LogP")
        st.bar_chart(chart_data[["logp"]])
    with chart_cols[2]:
        st.markdown("#### TPSA")
        st.bar_chart(chart_data[["tpsa"]])
    with chart_cols[3]:
        st.markdown("#### Confidence")
        st.bar_chart(chart_data[["confidence"]])
    with chart_cols[4]:
        st.markdown("#### Domain sim.")
        st.bar_chart(chart_data[["applicability_similarity"]])
    with chart_cols[5]:
        if "suggested_f" in chart_data and chart_data["suggested_f"].notna().any():
            st.markdown("#### Suggested F")
            st.bar_chart(chart_data[["suggested_f"]])
        else:
            st.markdown("#### Suggested F")
            st.caption("N/A")
    with chart_cols[6]:
        if "suggested_ka" in chart_data and chart_data["suggested_ka"].notna().any():
            st.markdown("#### Suggested ka")
            st.bar_chart(chart_data[["suggested_ka"]])
        else:
            st.markdown("#### Suggested ka")
            st.caption("N/A")

    st.markdown("#### Short interpretation")
    most_polar = comparison.sort_values("tpsa", ascending=False).iloc[0]
    most_lipophilic = comparison.sort_values("logp", ascending=False).iloc[0]
    largest = comparison.sort_values("molecular_weight", ascending=False).iloc[0]
    st.write(
        f"- Highest TPSA: **{most_polar['molecule']}**, which may reduce passive diffusion if polarity is high."
    )
    st.write(
        f"- Highest logP: **{most_lipophilic['molecule']}**, suggesting greater lipophilicity but possible solubility tradeoffs."
    )
    st.write(
        f"- Largest molecule: **{largest['molecule']}**, which may face size-related permeability penalties."
    )
    if comparison["applicability_similarity"].notna().any():
        lowest_domain = comparison.sort_values("applicability_similarity", ascending=True).iloc[0]
        st.write(
            f"- Lowest nearest-neighbor similarity: **{lowest_domain['molecule']}**; treat extrapolated predictions more cautiously."
        )
    if {"Metformin", "Ibuprofen", "Aspirin"}.issubset(set(comparison["molecule"])):
        st.markdown(
            _html_card(
                "Automatic ADME triage interpretation",
                "Metformin is much more polar than ibuprofen and aspirin, with higher hydrogen-bonding burden and lower lipophilicity, which is consistent with lower passive permeability. Ibuprofen is more lipophilic and less polar, supporting higher passive diffusion potential. Aspirin sits in a moderate region where acidity, TPSA, and ionization context matter.",
            ),
            unsafe_allow_html=True,
        )
    favorable = comparison.assign(rank_score=comparison["high_probability"].fillna(0) + comparison["confidence"].fillna(0) - comparison["tpsa"] / 300)
    most_favorable = favorable.sort_values("rank_score", ascending=False).iloc[0]
    polarity_limited = comparison.sort_values("tpsa", ascending=False).iloc[0]
    highest_confidence = comparison.sort_values("confidence", ascending=False).iloc[0]
    ranking_cols = st.columns(4)
    ranking_cols[0].metric("Most permeability-favorable", str(most_favorable["molecule"]))
    ranking_cols[1].metric("Most polarity-limited", str(polarity_limited["molecule"]))
    ranking_cols[2].metric("Highest confidence", str(highest_confidence["molecule"]))
    if comparison["applicability_similarity"].notna().any():
        outside = comparison.sort_values("applicability_similarity", ascending=True).iloc[0]
        ranking_cols[3].metric("Most outside-domain", str(outside["molecule"]))
    interpretations = comparison_interpretations(comparison)
    st.markdown(_html_card("Beginner interpretation", interpretations["beginner"]), unsafe_allow_html=True)
    st.markdown(_html_card("Pharmaceutics / PhD-level interpretation", interpretations["phd"]), unsafe_allow_html=True)


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


def render_evidence_library() -> None:
    """Render project evidence and documentation summary."""
    st.header("Evidence, Documentation, and Responsible Use")
    st.markdown(
        """
        This page summarizes the project artifacts that support the demo: dataset documentation,
        model reports, scaffold split comparison, SHAP interpretation, outlier analysis, and PK/NCA methods.
        """
    )
    with st.expander("Reviewer Summary", expanded=True):
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
    with st.expander("External validation roadmap toward human PK", expanded=True):
        st.markdown(
            """
            A validated human PK predictor would require observed human PK endpoints including CL, Vd, half-life, Cmax, and AUC; route, dose, formulation, population, fed/fasted, and sampling metadata; IVIVE assumptions for clearance and permeability; an external test set; 2-fold or 3-fold prediction-error benchmarks; and prospective validation. This app intentionally stops at Caco-2 permeability risk and educational PK/NCA simulation.
            """
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
            ["ADME Workbench", "Molecule Comparison", "PK/NCA Simulator", "Evidence & Limits"],
        )
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
    elif page == "PK/NCA Simulator":
        render_pk_nca_simulator()
    else:
        render_evidence_library()


if __name__ == "__main__":
    main()
