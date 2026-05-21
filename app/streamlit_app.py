"""Streamlit application for the Explainable AI ADME-PK Platform."""

from __future__ import annotations

import sys
import random
from pathlib import Path

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
from adme_predictor.reporting import build_prediction_report, render_molecule_svg  # noqa: E402


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
        "vd": 25.0,
        "kel": 0.12,
        "ka": 1.8,
        "bioavailability": 0.75,
        "infusion_duration": 2.0,
        "duration": 24.0,
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
            padding-top: 1.7rem;
            padding-bottom: 2.5rem;
            max-width: 1220px;
        }
        .hero {
            border: 1px solid #d7dde8;
            border-radius: 8px;
            padding: 1.35rem 1.45rem;
            background: #f8fafc;
            margin-bottom: 1rem;
        }
        .hero h1 {
            font-size: 2.25rem;
            line-height: 1.1;
            margin-bottom: 0.45rem;
            letter-spacing: 0;
        }
        .hero p {
            color: #475569;
            font-size: 1.02rem;
            margin: 0;
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
        }
        div[data-testid="stMetricLabel"] {
            color: #475569;
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
                Caco-2 permeability screening, structure-based model interpretation,
                applicability-domain checks, and an educational PK/NCA simulator.
                The platform is designed for early discovery reasoning and teaching,
                not clinical or regulatory decision-making.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    workflow = st.columns(7)
    steps = [
        "SMILES",
        "RDKit descriptors",
        "Caco-2 ML model",
        "Confidence",
        "Applicability domain",
        "SHAP explanation",
        "PK/NCA simulator",
    ]
    for col, step in zip(workflow, steps):
        col.markdown(f"**{step}**")
        if step != steps[-1]:
            col.caption("then")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Public dataset", "Caco-2 Wang")
    metric_cols[1].metric("Validation", "Random + scaffold")
    metric_cols[2].metric("AI transparency", "SHAP + confidence")
    metric_cols[3].metric("PK education", "NCA simulator")


def _render_scientific_boundary() -> None:
    st.info(
        "Scientific boundary: predictions are median-threshold Caco-2 permeability classes from molecular structure. "
        "The PK/NCA module uses user-specified assumptions. This app does not provide validated human PK, PBPK, "
        "dose, safety, efficacy, or regulatory conclusions."
    )


def _render_learning_panel() -> None:
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

    st.markdown('<div class="section-note">Workflow: structure validation -> descriptors -> permeability model -> confidence -> applicability-domain review.</div>', unsafe_allow_html=True)

    top_cols = st.columns([1.05, 1.4, 1.2])
    with top_cols[0]:
        _render_molecule_structure(smiles)
    with top_cols[1]:
        st.subheader(selected_name)
        st.markdown(f'<div class="section-note">{teaching_note}</div>', unsafe_allow_html=True)
        st.caption("Canonical RDKit SMILES")
        st.code(canonical_smiles, language="text")
        st.caption("The canonical form is used for reproducible descriptor calculation.")
    with top_cols[2]:
        st.metric("Molecular weight", _metric_number(descriptors.get("molecular_weight"), 1))
        st.metric("LogP", _metric_number(descriptors.get("logp"), 2))
        st.metric("TPSA", _metric_number(descriptors.get("tpsa"), 1))

    workflow_tabs = st.tabs(
        [
            "Descriptors",
            "Permeability",
            "Confidence",
            "Applicability Domain",
            "Explainable AI",
            "Limits",
        ]
    )

    with workflow_tabs[0]:
        st.subheader("Descriptor and Rule-Based ADME Signals")
        st.dataframe(_descriptor_dataframe(descriptors), hide_index=True, use_container_width=True)
        st.bar_chart(
            pd.DataFrame(
                {
                    "Molecular weight": [float(descriptors["molecular_weight"])],
                    "TPSA": [float(descriptors["tpsa"])],
                    "LogP x 50": [float(descriptors["logp"]) * 50],
                },
                index=[selected_name],
            )
        )
        st.markdown("#### Lipinski / ADME interpretation")
        for message in _interpret_flags(flags):
            st.write(f"- {message}")

    with workflow_tabs[1]:
        st.subheader("Caco-2 Permeability Prediction")
        if prediction is not None:
            probability = float(prediction["high_permeability_probability"])
            cols = st.columns(3)
            cols[0].metric("Predicted class", str(prediction["predicted_label"]))
            cols[1].metric("High-class probability", f"{probability:.2f}")
            cols[2].metric("Source", str(prediction.get("prediction_source", "model")))
            st.progress(probability)
            if prediction.get("prediction_source") == "descriptor fallback":
                st.info(str(prediction.get("prediction_note")))
            st.markdown(
                "This is a relative Caco-2 permeability class from the processed benchmark. "
                "It should be used as a screening signal, not as a human absorption claim."
            )

    with workflow_tabs[2]:
        st.subheader("Confidence Score")
        if confidence is None:
            st.info("Prediction confidence is available after model prediction.")
        else:
            cols = st.columns(3)
            cols[0].metric("Category", str(confidence["confidence_category"]))
            cols[1].metric("Confidence", f"{float(confidence['confidence_score']):.2f}")
            cols[2].metric("Entropy", f"{float(confidence['prediction_entropy']):.2f}")
            st.markdown(
                "High confidence means the model probability is far from 0.5 and entropy is lower. "
                "It does not imply clinical certainty or external validation."
            )

    with workflow_tabs[3]:
        st.subheader("Applicability Domain")
        if applicability is None:
            st.warning("Applicability-domain analysis could not be loaded in this environment.")
        else:
            cols = st.columns(3)
            cols[0].metric("Domain category", str(applicability["applicability_category"]))
            cols[1].metric("Nearest similarity", f"{float(applicability['nearest_neighbor_similarity']):.2f}")
            cols[2].metric("Outside domain", str(bool(applicability["outside_applicability_domain"])))
            st.write(f"Nearest training SMILES: `{applicability['nearest_neighbor_smiles']}`")
            if applicability["applicability_warning"]:
                st.warning(str(applicability["applicability_warning"]))
            else:
                st.success("The molecule is reasonably similar to training chemistry.")

    with workflow_tabs[4]:
        st.subheader("Explainable AI Evidence")
        st.markdown(
            "SHAP and feature-importance outputs summarize how the trained model uses descriptors and fingerprints. "
            "Interpretation should stay qualitative: TPSA, HBD/HBA, molecular weight, logP, flexibility, and structural fingerprints can be chemically plausible signals, but they are not causal proof."
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
            st.info("SHAP figure files are not present. The app remains usable without these optional artifacts.")

    with workflow_tabs[5]:
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

    if prediction is not None and confidence is not None and applicability is not None:
        report_text = build_prediction_report(smiles, prediction, confidence, applicability)
        st.download_button(
            "Download ADME prediction report",
            report_text,
            file_name="adme_prediction_report.md",
            mime="text/markdown",
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
        rows.append(
            {
                "molecule": str(entry["name"]),
                "category": str(entry["category"]),
                "molecular_weight": float(descriptors["molecular_weight"]),
                "logp": float(descriptors["logp"]),
                "tpsa": float(descriptors["tpsa"]),
                "hbd": int(descriptors["hbd"]),
                "hba": int(descriptors["hba"]),
                "predicted_permeability": prediction["predicted_label"] if prediction else "model unavailable",
                "high_probability": float(prediction["high_permeability_probability"]) if prediction else None,
                "confidence": float(confidence["confidence_score"]) if confidence else None,
                "applicability_similarity": float(applicability["nearest_neighbor_similarity"]) if applicability else None,
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
        "Caffeine - Natural products/cannabinoids",
        "Aspirin - Analgesics/NSAIDs",
        "Propranolol - Cardiovascular drugs",
    ]
    available_defaults = [label for label in default_labels if label in filtered["label"].tolist()]
    selected = st.multiselect(
        "Molecules to compare",
        filtered["label"].tolist(),
        default=available_defaults[:3],
        max_selections=5,
    )
    if len(selected) < 2:
        st.info("Select at least two molecules to compare.")
        return

    comparison = _comparison_rows(selected)
    if comparison.empty:
        st.warning("No comparison rows could be calculated.")
        return

    st.dataframe(comparison, hide_index=True, use_container_width=True)

    chart_cols = st.columns(3)
    chart_data = comparison.set_index("molecule")
    with chart_cols[0]:
        st.markdown("#### Size")
        st.bar_chart(chart_data[["molecular_weight"]])
    with chart_cols[1]:
        st.markdown("#### Polarity")
        st.bar_chart(chart_data[["tpsa", "hbd", "hba"]])
    with chart_cols[2]:
        st.markdown("#### Model confidence")
        model_cols = [col for col in ["high_probability", "confidence", "applicability_similarity"] if comparison[col].notna().any()]
        if model_cols:
            st.bar_chart(chart_data[model_cols])
        else:
            st.info("Model artifacts are unavailable, so prediction bars are hidden.")

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
    st.warning(
        "This simulator is instructional. It does not convert Caco-2 permeability into validated human PK and must not be used for clinical, regulatory, safety, efficacy, or dose decisions."
    )

    preset_name = st.selectbox("Teaching preset", list(PK_PRESETS.keys()))
    preset = PK_PRESETS[preset_name]
    st.markdown(f'<div class="section-note">{preset["note"]}</div>', unsafe_allow_html=True)

    input_col, output_col = st.columns([0.95, 1.55])
    with input_col:
        st.markdown("#### Parameters")
        route = st.selectbox(
            "Route",
            ["IV bolus", "oral", "IV infusion"],
            index=["IV bolus", "oral", "IV infusion"].index(str(preset["route"])),
        )
        dose = st.number_input("Dose", min_value=0.001, value=float(preset["dose"]), step=10.0)
        dose_units = st.selectbox("Dose units", ["mg", "umol", "arbitrary units"])
        vd = st.number_input("Vd", min_value=0.001, value=float(preset["vd"]), step=1.0)
        kel = st.number_input("kel", min_value=0.0001, value=float(preset["kel"]), step=0.01, format="%.4f")

        ka = None
        bioavailability = 1.0
        infusion_duration = None
        if route == "oral":
            ka = st.number_input("ka", min_value=0.0001, value=float(preset["ka"]), step=0.05, format="%.4f")
            bioavailability = st.slider("F", min_value=0.01, max_value=1.0, value=float(preset["bioavailability"]), step=0.01)
        if route == "IV infusion":
            infusion_duration = st.number_input(
                "Infusion duration",
                min_value=0.001,
                value=float(preset["infusion_duration"]),
                step=0.5,
            )

        duration = st.number_input("Simulation duration", min_value=0.1, value=float(preset["duration"]), step=1.0)
        interval = st.number_input("Sampling interval", min_value=0.01, value=float(preset["interval"]), step=0.1)
        n_terminal_points = st.slider("Terminal points for lambda_z", 3, 6, int(preset["n_terminal_points"]))
        nca_method = st.selectbox(
            "AUC method",
            ["linear_up_log_down", "linear"],
            index=["linear_up_log_down", "linear"].index(str(preset["method"])),
        )

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

    with output_col:
        metric_cols = st.columns(4)
        metric_cols[0].metric("Cmax", _safe_float(nca_summary["cmax"]))
        metric_cols[1].metric("Tmax", _safe_float(nca_summary["tmax"]))
        metric_cols[2].metric("AUCinf", _safe_float(nca_summary["auc_inf"]))
        metric_cols[3].metric(str(nca_summary["clearance_label"]), _safe_float(nca_summary["clearance"]))

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
            st.markdown(
                """
                **AUC:** area under the concentration-time curve; a measure of total exposure.

                **AUMC:** area under the first moment curve; integrates time multiplied by concentration.

                **MRT / MBRT:** mean residence time, often estimated as AUMC/AUC under NCA assumptions.

                **CL:** for IV data, clearance is Dose/AUC when assumptions are appropriate.

                **CL/F:** for oral dosing, apparent clearance because bioavailability affects exposure.

                **Vss:** steady-state volume assumptions are meaningful mainly for IV settings; oral data alone cannot separate F, CL, and distribution.
                """
            )

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
            st.write("1. Pick a molecule or paste SMILES.")
            st.write("2. Review descriptors, prediction, confidence, and domain fit.")
            st.write("3. Compare 2-5 molecules for structure-property reasoning.")
            st.write("4. Use PK/NCA presets to learn exposure metrics.")
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
