"""Streamlit application for AI-PBPK / ADME Predictor."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from adme_predictor.applicability import assess_applicability_domain  # noqa: E402
from adme_predictor.features import (  # noqa: E402
    build_feature_vector,
    calculate_descriptors,
    calculate_lipinski_flags,
    canonicalize_smiles,
)
from adme_predictor.modeling import predict_permeability_class  # noqa: E402
from adme_predictor.nca import calculate_nca  # noqa: E402
from adme_predictor.pk import simulate_pk_profile  # noqa: E402
from adme_predictor.pk_visualization import (  # noqa: E402
    plot_concentration_time,
    plot_semilog_concentration_time,
)
from adme_predictor.reporting import build_prediction_report, render_molecule_svg  # noqa: E402
from adme_predictor.uncertainty import confidence_from_probability  # noqa: E402


EXAMPLE_MOLECULES = {
    "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "Caffeine": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "Ethanol": "CCO",
}


def _interpret_flags(flags: dict[str, bool | int]) -> list[str]:
    messages = []
    if flags["lipinski_violations"] == 0:
        messages.append("No Lipinski rule-of-five violations were detected.")
    else:
        messages.append(
            f"{flags['lipinski_violations']} Lipinski rule-of-five violation(s) were detected."
        )

    if flags["high_tpsa_flag"]:
        messages.append("High TPSA can reduce passive permeability.")
    if flags["high_rotatable_bonds_flag"]:
        messages.append("High flexibility may reduce oral drug-likeness.")
    if flags["high_logp_flag"]:
        messages.append("High logP suggests elevated lipophilicity and possible solubility risk.")
    if flags["high_mw_flag"]:
        messages.append("Molecular weight is above the common Lipinski threshold.")

    messages.append("These are screening descriptors, not clinical predictions.")
    return messages


def _safe_float(value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if numeric != numeric:
        return "Not reported"
    return f"{numeric:.4g}"


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


def render_adme_screening() -> None:
    """Render molecular descriptor, prediction, and explainability workflow."""
    st.subheader("Explainable Molecular ADME Screening")
    st.caption("Caco-2 permeability risk from molecular structure. Not clinical PK prediction.")

    workflow_tabs = st.tabs(
        [
            "Molecule Input",
            "Descriptor Summary",
            "Permeability Prediction",
            "Confidence",
            "Applicability Domain",
            "Explainable AI",
            "Scientific Limitations",
        ]
    )

    with workflow_tabs[0]:
        example_name = st.selectbox("Example molecules", ["Custom", *EXAMPLE_MOLECULES.keys()])
        default_smiles = "" if example_name == "Custom" else EXAMPLE_MOLECULES[example_name]
        smiles = st.text_area(
            "SMILES string",
            value=default_smiles,
            placeholder="Example: Cn1cnc2c1c(=O)n(C)c(=O)n2C",
        )

    if not smiles.strip():
        st.info("Enter a SMILES string or choose an example molecule to run ADME screening.")
        return

    try:
        canonical_smiles = canonicalize_smiles(smiles)
        descriptors = calculate_descriptors(smiles)
        flags = calculate_lipinski_flags(descriptors)
        feature_vector = build_feature_vector(smiles)
    except ValueError as error:
        st.error(str(error))
        return

    molecule_svg = None
    try:
        molecule_svg = render_molecule_svg(smiles)
    except Exception:
        molecule_svg = None

    prediction = None
    confidence = None
    applicability = None

    with workflow_tabs[0]:
        col_structure, col_smiles = st.columns([1, 2])
        with col_structure:
            if molecule_svg:
                components.html(molecule_svg, height=320)
                st.caption("2D molecular structure")
            else:
                st.warning("Molecule image could not be rendered in this environment.")
        with col_smiles:
            st.subheader("Canonical SMILES")
            st.code(canonical_smiles, language="text")

    with workflow_tabs[1]:
        descriptor_table = pd.DataFrame(
            [{"descriptor": key, "value": value} for key, value in descriptors.items()]
        )
        st.dataframe(descriptor_table, hide_index=True, use_container_width=True)
        st.subheader("Lipinski / ADME Flags")
        st.dataframe(
            pd.DataFrame([{"flag": key, "value": value} for key, value in flags.items()]),
            hide_index=True,
            use_container_width=True,
        )
        for message in _interpret_flags(flags):
            st.write(f"- {message}")

    with workflow_tabs[2]:
        try:
            prediction = predict_permeability_class(smiles)
            probability = prediction["high_permeability_probability"]
            st.metric("Predicted class", str(prediction["predicted_label"]))
            if probability == probability:
                st.metric("High-permeability probability", f"{probability:.2f}")
                st.progress(float(probability))
            st.caption(
                "The class threshold is the processed dataset median Caco-2 log(Papp), "
                "not a clinical cutoff."
            )
        except FileNotFoundError:
            st.warning("Baseline model artifact not found. Run the training pipeline first.")

    with workflow_tabs[3]:
        if prediction is not None:
            confidence = confidence_from_probability(
                float(prediction["high_permeability_probability"])
            )
            st.metric("Confidence category", str(confidence["confidence_category"]))
            st.metric("Confidence score", f"{confidence['confidence_score']:.2f}")
            st.metric("Prediction entropy", f"{confidence['prediction_entropy']:.2f}")
            st.caption(
                "Confidence is based on probability margin and entropy. It is not a "
                "calibrated clinical certainty estimate."
            )
        else:
            st.info("Train or load the baseline model to display prediction confidence.")

    with workflow_tabs[4]:
        applicability = assess_applicability_domain(smiles)
        st.metric("Applicability category", str(applicability["applicability_category"]))
        st.metric(
            "Nearest-neighbor similarity",
            f"{applicability['nearest_neighbor_similarity']:.2f}",
        )
        st.write(f"Nearest training SMILES: `{applicability['nearest_neighbor_smiles']}`")
        if applicability["applicability_warning"]:
            st.warning(str(applicability["applicability_warning"]))
        else:
            st.success("The molecule is reasonably similar to training chemistry.")

    with workflow_tabs[5]:
        st.subheader("Explainable AI Interpretation")
        st.write(
            "Global SHAP analysis is generated in `reports/figures/shap/`. Descriptor "
            "signals should be interpreted chemically: TPSA and HBD/HBA reflect polarity, "
            "logP reflects lipophilicity, molecular weight captures size, and Morgan "
            "fingerprints capture scaffold and substituent patterns."
        )
        shap_dir = PROJECT_ROOT / "reports" / "figures" / "shap"
        local_candidates = [
            shap_dir / "local_aspirin_classifier.png",
            shap_dir / "local_caffeine_classifier.png",
            shap_dir / "classifier_bar_importance.png",
        ]
        shown = False
        for path in local_candidates:
            if path.exists():
                st.image(str(path), caption=path.name)
                shown = True
        if not shown:
            st.info("Run SHAP generation to display saved explanation figures.")

    with workflow_tabs[6]:
        st.write(
            "The model was evaluated using both random and scaffold split validation. "
            "Scaffold split is stricter because it evaluates performance on chemically "
            "distinct structures."
        )
        st.write(
            "This platform predicts permeability-related screening risk from molecular "
            "structure. It does not provide validated clinical PK, PBPK, safety, efficacy, "
            "dose, or regulatory conclusions."
        )
        st.write(
            "Caco-2 permeability is an in vitro proxy. Oral absorption also depends on "
            "solubility, transporters, metabolism, formulation, dose, and physiology."
        )

    if prediction is not None and confidence is not None and applicability is not None:
        report_text = build_prediction_report(smiles, prediction, confidence, applicability)
        st.download_button(
            "Download ADME prediction report",
            report_text,
            file_name="adme_prediction_report.md",
            mime="text/markdown",
        )

    with st.expander("Feature vector preview"):
        st.json(feature_vector)


def render_pk_nca_simulator() -> None:
    """Render educational PK/NCA simulator."""
    st.subheader("PK/NCA Simulator")
    st.caption(
        "Educational one-compartment simulation and noncompartmental analysis under explicit assumptions."
    )
    st.warning(
        "This module is mechanistic and educational. It does not convert Caco-2 permeability "
        "into validated human PK and must not be used for clinical, regulatory, safety, "
        "efficacy, or dose decisions."
    )

    input_col, output_col = st.columns([0.9, 1.4])
    with input_col:
        st.markdown("#### Parameter Input")
        route = st.selectbox("Route", ["IV bolus", "oral", "IV infusion"])
        dose = st.number_input("Dose", min_value=0.001, value=100.0, step=10.0)
        dose_units = st.selectbox("Dose units", ["mg", "umol", "arbitrary units"])
        vd = st.number_input("Vd", min_value=0.001, value=20.0, step=1.0)
        kel = st.number_input("kel", min_value=0.0001, value=0.15, step=0.01, format="%.4f")

        ka = None
        bioavailability = 1.0
        infusion_duration = None
        if route == "oral":
            ka = st.number_input("ka", min_value=0.0001, value=1.0, step=0.05, format="%.4f")
            bioavailability = st.slider("F", min_value=0.01, max_value=1.0, value=0.7, step=0.01)
        if route == "IV infusion":
            infusion_duration = st.number_input(
                "Infusion duration",
                min_value=0.001,
                value=2.0,
                step=0.5,
            )

        duration = st.number_input("Simulation duration", min_value=0.1, value=24.0, step=1.0)
        interval = st.number_input("Sampling interval", min_value=0.01, value=0.5, step=0.1)
        n_terminal_points = st.slider("Terminal points for lambda_z", 3, 6, 3)
        nca_method = st.selectbox("AUC method", ["linear_up_log_down", "linear"])

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

        plot_tabs = st.tabs(["Linear Plot", "Semi-Log Plot", "Tables", "Assumptions"])
        with plot_tabs[0]:
            st.pyplot(plot_concentration_time(profile), clear_figure=True)
        with plot_tabs[1]:
            st.pyplot(plot_semilog_concentration_time(profile), clear_figure=True)
        with plot_tabs[2]:
            st.markdown("##### Concentration-Time Table")
            st.dataframe(profile, hide_index=True, use_container_width=True)
            st.markdown("##### NCA Summary")
            nca_table = pd.DataFrame(
                [{"metric": key, "value": value} for key, value in nca_summary.items()]
            )
            st.dataframe(nca_table, hide_index=True, use_container_width=True)
        with plot_tabs[3]:
            st.write("- One-compartment model with first-order elimination.")
            st.write("- NCA is calculated from simulated concentration-time data.")
            st.write("- IV routes may report CL and model-dependent Vss assumptions.")
            st.write("- Oral route reports CL/F because true bioavailability separates apparent from true clearance.")
            if warnings:
                for warning in warnings:
                    st.warning(warning)
            else:
                st.success("No major simulation or NCA warnings for these settings.")

    st.markdown("#### Interpretation")
    st.write(
        "AUC summarizes total concentration-time exposure. AUMC weights exposure by time, "
        "supporting MRT/MBRT. Terminal lambda_z and half-life depend on the final sampled "
        "points, so insufficient late sampling can inflate extrapolated AUC."
    )
    if route == "oral":
        st.write(
            "For oral dosing, clearance is reported as CL/F because observed exposure reflects "
            "both systemic clearance and bioavailability."
        )

    with st.expander("Academic learning mode"):
        st.markdown(
            """
**What is AUC?** Area under the concentration-time curve; a summary of systemic exposure in the simulated profile.

**What is AUMC?** Area under the first moment curve, calculated from time multiplied by concentration.

**What is MRT/MBRT?** Mean residence time or mean body residence time, calculated as AUMC/AUC under NCA assumptions.

**What is clearance?** For IV data, CL = Dose/AUC when assumptions are appropriate. It describes apparent volume cleared per unit time.

**Why does oral dosing give CL/F?** Oral exposure combines clearance and bioavailability, so Dose/AUC estimates apparent clearance, not true systemic clearance.

**Why do Vss assumptions matter?** Vss from NCA relies on IV assumptions and AUMC/AUC relationships. It should not be reported casually for oral simulations.

**NCA vs compartmental simulation.** The simulator generates data from a compartmental equation; NCA then calculates exposure metrics from the generated profile without refitting the same model.

**Why permeability does not equal exposure.** Caco-2 permeability is one in vitro property. Human exposure also depends on solubility, dissolution, transporters, metabolism, plasma binding, physiology, and formulation.
"""
        )

    concentration_csv = profile.to_csv(index=False)
    nca_csv = pd.DataFrame([nca_summary]).to_csv(index=False)
    report_text = _build_pk_report(route, parameters, nca_summary, warnings)
    download_cols = st.columns(3)
    download_cols[0].download_button(
        "Download concentration CSV",
        concentration_csv,
        file_name="pk_concentration_time.csv",
        mime="text/csv",
    )
    download_cols[1].download_button(
        "Download NCA summary CSV",
        nca_csv,
        file_name="nca_summary.csv",
        mime="text/csv",
    )
    download_cols[2].download_button(
        "Download PK/NCA report",
        report_text,
        file_name="pk_nca_report.md",
        mime="text/markdown",
    )


def main() -> None:
    """Render the app."""
    st.set_page_config(
        page_title="AI-PBPK / ADME Predictor",
        page_icon="AI",
        layout="wide",
    )

    st.title("AI-PBPK / ADME Predictor")
    st.caption(
        "Explainable AI-assisted ADME screening plus educational PK/NCA simulation. "
        "No clinical or regulatory claims."
    )
    st.info(
        "The ML model estimates Caco-2 permeability-related risk from molecular structure. "
        "The PK/NCA simulator demonstrates exposure calculations under assumed parameters; "
        "it is not validated human PK or PBPK prediction."
    )

    main_tabs = st.tabs(["ADME Screening", "PK/NCA Simulator"])
    with main_tabs[0]:
        render_adme_screening()
    with main_tabs[1]:
        render_pk_nca_simulator()


if __name__ == "__main__":
    main()
