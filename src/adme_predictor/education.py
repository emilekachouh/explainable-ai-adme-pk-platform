"""Educational PK/ADME interpretation and report helpers."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from adme_predictor.nca import calculate_nca
from adme_predictor.pk import simulate_pk_profile


WHAT_THIS_APP_DOES = (
    "This platform links molecular structure to explainable Caco-2 permeability prediction, "
    "then shows how permeability-related assumptions can influence educational oral PK simulations. "
    "It combines RDKit descriptors, a real-data ML permeability model, confidence scoring, "
    "applicability-domain checks, SHAP-style interpretation, molecule comparison, and PK/NCA teaching tools. "
    "It is intended for early ADME learning and hypothesis generation, not clinical PK prediction."
)

HOW_TO_USE_STEPS = (
    "Select an example molecule or paste a SMILES.",
    "Review molecular descriptors such as MW, logP, TPSA, and HBD/HBA.",
    "View the Caco-2 permeability prediction.",
    "Check confidence and applicability domain.",
    "Use comparison mode to compare molecules.",
    "Use the Permeability to PK Impact tool to see how F and ka assumptions affect oral PK curves.",
    "Download the report.",
)

PK_EQUATIONS_TEXT = """
IV bolus: C(t) = Dose / Vd × exp(-kel × t)
Places drug directly into systemic circulation under a one-compartment assumption.

Oral first-order absorption: C(t) = (F × Dose × ka) / [Vd × (ka - kel)] × [exp(-kel × t) - exp(-ka × t)]
Describes input through absorption and output through elimination when ka is not equal to kel.

Elimination: kel = CL / Vd
The elimination rate constant links systemic clearance and apparent volume.

IV AUC: AUC_IV = Dose / CL
For IV dosing under linear assumptions, exposure is directly related to dose and true systemic clearance.

Oral AUC: AUC_oral = F × Dose / CL
For oral dosing, exposure depends on bioavailability as well as true systemic clearance.

Apparent oral clearance: CL/F = Dose / AUC
Oral data estimate apparent clearance unless F is independently known.

NCA: MRT = AUMC / AUC
Mean residence time summarizes how long exposure is retained under NCA assumptions.

Half-life: t1/2 = ln(2) / lambda_z
Terminal half-life depends on the terminal slope estimated from late concentration-time data.

Vss for IV assumptions: Vss = Dose × AUMC / AUC²
Steady-state volume from NCA is mainly appropriate for IV assumptions.
""".strip()

IV_ORAL_EXPLANATION = """
IV bolus places drug directly into systemic circulation, so F = 1 by definition. For IV dosing under linear assumptions, clearance can be estimated as CL = Dose/AUC.

Oral dosing includes absorption and first-pass effects. For oral dosing, the observable clearance term is apparent clearance, CL/F, unless bioavailability is independently known. Permeability can inform absorption assumptions such as F and ka, but it does not by itself determine true systemic clearance.
""".strip()

IVIVE_EXPLANATION = """
IVIVE means in vitro-in vivo extrapolation. To move toward real human PK prediction, the platform would need experimentally measured or validated inputs such as in vitro intrinsic clearance, plasma protein binding, blood-to-plasma ratio, permeability and solubility data, transporter involvement, hepatic blood-flow assumptions, fraction absorbed, bioavailability, route/dose/formulation metadata, and external human PK validation.

This app currently demonstrates permeability-informed educational absorption scenarios; it does not perform validated IVIVE.
""".strip()

SCIENTIFIC_BOUNDARIES = {
    "supports": [
        "Caco-2 permeability-related ML screening",
        "descriptor-based interpretation",
        "confidence and applicability-domain checks",
        "educational PK/NCA simulation",
        "permeability-to-F/ka assumption exploration",
    ],
    "does_not_support": [
        "validated human PK prediction",
        "clinical dose selection",
        "regulatory decisions",
        "safety or efficacy prediction",
        "true CL prediction from permeability alone",
    ],
}

REFERENCES = (
    {
        "name": "FDA CDER PBPK Program",
        "url": "https://www.fda.gov/about-fda/cder-offices-and-divisions/program-physiologically-based-pharmacokinetic-and-pharmacodynamic-modeling-pbpk-program",
        "note": "FDA describes PBPK models as integrating drug and physiology information and using predict-learn-confirm cycles.",
    },
    {
        "name": "FDA Physiologically Based Pharmacokinetic Analyses - Format and Content guidance",
        "url": "https://www.fda.gov/media/128793/download",
        "note": "Verify current FDA guidance metadata before publication.",
    },
    {
        "name": "FDA Bioavailability Studies Submitted in NDAs or INDs - General Considerations",
        "url": "https://www.fda.gov/media/121311/download",
        "note": "FDA guidance for BA information and systemic exposure study considerations.",
    },
    {
        "name": "EMA PBPK modelling and simulation reporting guideline",
        "url": "https://www.ema.europa.eu/en/reporting-physiologically-based-pharmacokinetic-pbpk-modelling-simulation-scientific-guideline",
        "note": "EMA describes expected PBPK report content and qualification documentation for regulatory submissions.",
    },
    {
        "name": "EMA clinical pharmacology and pharmacokinetics questions and answers",
        "url": "https://www.ema.europa.eu/en/human-regulatory-overview/research-development/scientific-guidelines/clinical-pharmacology-pharmacokinetics-guidelines/clinical-pharmacology-pharmacokinetics-questions-answers",
        "note": "Includes PK discussion of AUC, Cmax, CL/F, NCA, and extrapolated AUC principles.",
    },
    {
        "name": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics",
        "url": "citation needed",
        "note": "Standard PK textbook reference; verify edition details before publication.",
    },
    {
        "name": "Gibaldi & Perrier, Pharmacokinetics",
        "url": "citation needed",
        "note": "Classic PK textbook reference; verify edition details before publication.",
    },
    {
        "name": "Gabrielsson & Weiner, Pharmacokinetic and Pharmacodynamic Data Analysis",
        "url": "citation needed",
        "note": "Comprehensive PK/PD modeling reference; verify edition details before publication.",
    },
)

REVIEWER_SUMMARY = {
    "ai_ml_recruiter": (
        "This product demonstrates a complete AI health application: real public dataset ingestion, "
        "RDKit molecular featurization, trained classifier inference with graceful fallback, "
        "uncertainty quantification, applicability-domain checks, SHAP-style explainability, "
        "multi-molecule comparison workflow, cached Streamlit deployment, downloadable reports, "
        "unit-tested Python package structure, and molecule SVG rendering. "
        "Tests cover both scientific correctness (AUC ratios, CL/F invariance) and software correctness."
    ),
    "computational_pharmacology": (
        "The platform uses a public Caco-2 benchmark dataset (TDC Caco-2 Wang, ~906 compounds), "
        "RDKit descriptors and Morgan fingerprints, Random Forest and XGBoost classifiers, "
        "Bemis-Murcko scaffold-split validation, SHAP explainability, Tanimoto-based "
        "applicability-domain checks, binary entropy confidence scoring, and an explicit "
        "permeability-to-F/ka educational mapping. The scientific logic correctly holds true CL "
        "fixed when exploring absorption assumptions, and separates Caco-2 screening from validated human PK."
    ),
    "academic_pi": (
        "The platform demonstrates responsible scientific communication: "
        "it separates in vitro Caco-2 permeability screening from educational one-compartment PK simulation, "
        "explicitly tracks the boundary between model output and clinical inference, "
        "provides applicability-domain warnings for out-of-training chemistry, "
        "and documents the path toward validated human PK (IVIVE inputs, external PK endpoints, "
        "2-fold/3-fold prediction benchmarks, prospective validation). "
        "It does not overclaim. Suitable for ADME hypothesis generation and PK/NCA teaching."
    ),
}


def explanation_for_level(level: str) -> str:
    """Return reviewer-focused explanation text for the requested audience."""
    if level == "Beginner":
        return (
            "Start with a molecule, inspect simple properties, then read the permeability prediction as a screening clue. "
            "The PK tools show how assumed absorption changes a curve; they are not human PK predictions."
        )
    if level == "Pharmaceutics graduate student":
        return (
            "Use MW, logP, TPSA, HBD/HBA, F, ka, Vd, kel, AUC, Cmax, Tmax, and CL/F to connect molecular properties with simplified oral absorption assumptions. "
            "The oral model maps permeability-related hypotheses to F and ka while holding true CL constant."
        )
    if level == "PI / PK reviewer":
        return (
            "Review the explicit assumptions, model-domain similarity, confidence, and validation boundaries. "
            "External human PK validation would require observed CL, Vd, t1/2, AUC/Cmax, route/dose/formulation metadata, IVIVE assumptions, and prospective or external test-set evidence."
        )
    if level == "AI/ML recruiter":
        return (
            "The product demonstrates data ingestion, RDKit featurization, model inference, uncertainty, applicability-domain checks, explainability, cached deployment, reports, tests, and a user-facing scientific workflow."
        )
    return explanation_for_level("Beginner")


def permeability_to_pk_assumptions(high_probability: float) -> dict[str, float]:
    """Map permeability probability to transparent educational F/ka assumptions."""
    probability = min(max(float(high_probability), 0.0), 1.0)
    return {
        "reference_f": 0.80,
        "reference_ka": 1.20,
        "adjusted_f": round(0.30 + 0.65 * probability, 3),
        "adjusted_ka": round(0.20 + 1.60 * probability, 3),
        "true_cl": 6.0,
        "vd": 40.0,
        "dose": 100.0,
        "duration": 48.0,
        "interval": 0.5,
    }


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator and math.isfinite(denominator):
        return float(numerator / denominator)
    return float("nan")


def pk_impact_table(high_probability: float) -> pd.DataFrame:
    """Calculate reference vs adjusted oral PK metrics for teaching."""
    assumptions = permeability_to_pk_assumptions(high_probability)
    kel = assumptions["true_cl"] / assumptions["vd"]
    rows = []
    for scenario, f_value, ka_value in [
        ("Reference absorption", assumptions["reference_f"], assumptions["reference_ka"]),
        ("Permeability-adjusted absorption", assumptions["adjusted_f"], assumptions["adjusted_ka"]),
    ]:
        profile, _ = simulate_pk_profile(
            route="oral",
            dose=assumptions["dose"],
            vd=assumptions["vd"],
            kel=kel,
            duration=assumptions["duration"],
            interval=assumptions["interval"],
            ka=ka_value,
            bioavailability=f_value,
        )
        summary, _ = calculate_nca(
            profile,
            dose=assumptions["dose"],
            route="oral",
            bioavailability=f_value,
        )
        rows.append(
            {
                "scenario": scenario,
                "F": f_value,
                "ka": ka_value,
                "AUC": float(summary["auc_inf"]),
                "Cmax": float(summary["cmax"]),
                "Tmax": float(summary["tmax"]),
                "true_CL": assumptions["true_cl"],
                "CL/F": float(summary["clearance"]),
            }
        )
    table = pd.DataFrame(rows)
    reference = table.iloc[0]
    adjusted = table.iloc[1]
    table["AUC_ratio_vs_reference"] = [1.0, _safe_ratio(adjusted["AUC"], reference["AUC"])]
    table["Cmax_ratio_vs_reference"] = [1.0, _safe_ratio(adjusted["Cmax"], reference["Cmax"])]
    table["Tmax_shift_vs_reference"] = [0.0, float(adjusted["Tmax"] - reference["Tmax"])]
    table["CLF_ratio_vs_reference"] = [1.0, _safe_ratio(adjusted["CL/F"], reference["CL/F"])]
    return table


def pk_impact_profiles(high_probability: float) -> pd.DataFrame:
    """Return reference and permeability-adjusted concentration-time profiles."""
    assumptions = permeability_to_pk_assumptions(high_probability)
    kel = assumptions["true_cl"] / assumptions["vd"]
    profiles = []
    for scenario, f_value, ka_value in [
        ("Reference absorption", assumptions["reference_f"], assumptions["reference_ka"]),
        ("Permeability-adjusted absorption", assumptions["adjusted_f"], assumptions["adjusted_ka"]),
    ]:
        profile, _ = simulate_pk_profile(
            route="oral",
            dose=assumptions["dose"],
            vd=assumptions["vd"],
            kel=kel,
            duration=assumptions["duration"],
            interval=assumptions["interval"],
            ka=ka_value,
            bioavailability=f_value,
        )
        profile = profile.copy()
        profile["scenario"] = scenario
        profile["F"] = f_value
        profile["ka"] = ka_value
        profiles.append(profile)
    return pd.concat(profiles, ignore_index=True)


def comparison_interpretations(comparison: pd.DataFrame) -> dict[str, str]:
    """Generate beginner and advanced interpretation paragraphs for comparison mode."""
    if comparison.empty:
        return {"beginner": "", "phd": ""}
    most_polar = comparison.sort_values("tpsa", ascending=False).iloc[0]
    most_lipophilic = comparison.sort_values("logp", ascending=False).iloc[0]
    beginner = (
        f"{most_polar['molecule']} is the most polar molecule in this comparison, while "
        f"{most_lipophilic['molecule']} is the most lipophilic. Polar molecules often cross membranes less easily by passive diffusion, "
        "so lower permeability assumptions can reduce simulated oral AUC and Cmax in the educational PK scenario."
    )
    phd = (
        "Under the simplified oral one-compartment framework, permeability-related assumptions are mapped to F and ka rather than true systemic CL. "
        "Holding dose, Vd, and true CL constant, a reduction in F decreases AUC according to AUC_oral = F × Dose / CL. "
        "The apparent oral clearance CL/F increases because CL/F = Dose/AUC, even though intrinsic systemic clearance is unchanged. "
        "Changes in ka primarily alter absorption-rate-limited curve shape, affecting Cmax and Tmax."
    )
    return {"beginner": beginner, "phd": phd}


def pk_impact_interpretations(pk_table: pd.DataFrame) -> dict[str, str]:
    """Generate beginner and advanced PK impact interpretation paragraphs."""
    reference = pk_table.iloc[0]
    adjusted = pk_table.iloc[1]
    beginner = (
        f"The adjusted scenario changes F from {reference['F']:.2f} to {adjusted['F']:.2f} and ka from "
        f"{reference['ka']:.2f} to {adjusted['ka']:.2f}. In this educational oral model, those assumptions change exposure and peak shape, "
        "but they do not change true systemic clearance."
    )
    phd = (
        f"AUC ratio is {adjusted['AUC_ratio_vs_reference']:.2f}, Cmax ratio is {adjusted['Cmax_ratio_vs_reference']:.2f}, "
        f"and Tmax shift is {adjusted['Tmax_shift_vs_reference']:.2f} time units. CL/F changes inversely with AUC because "
        "CL/F = Dose/AUC, while true CL is held constant by design."
    )
    return {"beginner": beginner, "phd": phd}


def build_downloadable_report(
    molecule_name: str,
    category: str,
    smiles: str,
    canonical_smiles: str,
    descriptors: dict[str, Any],
    prediction: dict[str, Any],
    confidence: dict[str, Any],
    applicability: dict[str, Any],
    pk_table: pd.DataFrame,
) -> str:
    """Build a markdown report for the selected molecule."""
    descriptor_lines = [f"| {key} | {value} |" for key, value in descriptors.items()]
    pk = pk_table.iloc[1]
    pk_ref = pk_table.iloc[0]
    pk_interpretation = pk_impact_interpretations(pk_table)
    reference_lines = [f"- **{ref['name']}**: {ref['url']}  \n  {ref['note']}" for ref in REFERENCES]

    prob = float(prediction.get("high_permeability_probability", 0.0))
    conf = float(confidence.get("confidence_score", 0.0))
    sim = float(applicability.get("nearest_neighbor_similarity", 0.0))

    return "\n".join(
        [
            "# Explainable AI ADME-PK Platform — Molecule Screening Report",
            "",
            "> **Scientific boundary:** This report supports in vitro Caco-2 permeability screening and educational PK/NCA interpretation only. It is NOT a clinical, regulatory, safety, efficacy, dose-selection, PBPK, or validated human PK report.",
            "",
            "---",
            "",
            "## 1. Selected Molecule",
            "",
            f"| Field | Value |",
            f"|---|---|",
            f"| Name | {molecule_name} |",
            f"| Category | {category} |",
            f"| Input SMILES | `{smiles}` |",
            f"| Canonical SMILES | `{canonical_smiles}` |",
            "",
            "---",
            "",
            "## 2. Molecular Descriptor Summary",
            "",
            "| Descriptor | Value |",
            "|---|---|",
            *descriptor_lines,
            "",
            "---",
            "",
            "## 3. Caco-2 Permeability Prediction",
            "",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Predicted class | {prediction.get('predicted_label')} |",
            f"| High-class probability | {prob:.3f} |",
            f"| Prediction source | {prediction.get('prediction_source', 'model')} |",
            f"| Class threshold | Dataset median log(Papp) |",
            "",
            "**Biological interpretation:** A high Caco-2 class suggests descriptor/fingerprint "
            "patterns associated with higher in vitro epithelial permeability in the benchmark dataset. "
            "This is a screening signal, not validated human oral absorption.",
            "",
            "---",
            "",
            "## 4. Confidence and Reliability",
            "",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Confidence category | {confidence.get('confidence_category')} |",
            f"| Confidence score | {conf:.3f} |",
            f"| Prediction entropy | {confidence.get('prediction_entropy')} |",
            "",
            "Confidence increases when the classifier probability is far from the 0.5 decision boundary. "
            "High confidence indicates model decisiveness for this feature representation, "
            "not biological certainty.",
            "",
            "---",
            "",
            "## 5. Applicability Domain",
            "",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Domain category | {applicability.get('applicability_category')} |",
            f"| Nearest-neighbor similarity | {sim:.3f} |",
            f"| Applicability warning | {applicability.get('applicability_warning') or 'None'} |",
            "",
            "Applicability domain uses Morgan fingerprint Tanimoto similarity to the nearest "
            "training compound. Low similarity means the model may be extrapolating beyond "
            "its training chemistry and predictions should be treated as hypothesis-generating.",
            "",
            "---",
            "",
            "## 6. Feature Interpretation (SHAP-style)",
            "",
            "The following descriptors typically drive model behavior for Caco-2 permeability:",
            "",
            "| Feature | Chemical interpretation |",
            "|---|---|",
            "| TPSA | Higher polar surface area increases desolvation cost and often reduces passive permeability |",
            "| HBD/HBA | Hydrogen-bond donors and acceptors can increase desolvation penalty |",
            "| LogP | Moderate lipophilicity can support membrane partitioning; very high logP may hurt solubility |",
            "| Molecular weight | Larger molecules often diffuse less efficiently through membranes |",
            "| Rotatable bonds | Higher flexibility can add conformational cost |",
            "",
            "> SHAP explains model behavior, not causal biology.",
            "",
            "---",
            "",
            "## 7. Permeability-to-PK Impact Analysis",
            "",
            "The app maps the permeability prediction to oral absorption assumptions F and ka. "
            "Dose, Vd, and true systemic CL are held constant by design. "
            "Permeability does not change true systemic clearance.",
            "",
            "| Parameter | Reference scenario | Permeability-adjusted scenario |",
            "|---|---|---|",
            f"| F (bioavailability) | {pk_ref['F']:.3f} | {pk['F']:.3f} |",
            f"| ka (absorption rate, 1/h) | {pk_ref['ka']:.3f} | {pk['ka']:.3f} |",
            f"| AUC | {pk_ref['AUC']:.2f} | {pk['AUC']:.2f} |",
            f"| Cmax | {pk_ref['Cmax']:.2f} | {pk['Cmax']:.2f} |",
            f"| Tmax | {pk_ref['Tmax']:.2f} | {pk['Tmax']:.2f} |",
            f"| True CL | {pk['true_CL']:.2f} | {pk['true_CL']:.2f} (unchanged) |",
            f"| CL/F | {pk_ref['CL/F']:.2f} | {pk['CL/F']:.2f} |",
            "",
            "**Ratios (adjusted vs reference):**",
            "",
            f"| Ratio | Value |",
            f"|---|---|",
            f"| AUC ratio | {pk['AUC_ratio_vs_reference']:.3f} |",
            f"| Cmax ratio | {pk['Cmax_ratio_vs_reference']:.3f} |",
            f"| Tmax shift (h) | {pk['Tmax_shift_vs_reference']:.3f} |",
            f"| CL/F ratio | {pk['CLF_ratio_vs_reference']:.3f} |",
            "",
            "---",
            "",
            "## 8. Interpretation",
            "",
            "**Beginner:**",
            "",
            pk_interpretation["beginner"],
            "",
            "**Pharmaceutics / PhD level:**",
            "",
            pk_interpretation["phd"],
            "",
            "---",
            "",
            "## 9. Core PK Equations",
            "",
            "```",
            "AUC_oral = F × Dose / CL",
            "CL/F    = Dose / AUC",
            "kel      = CL / Vd",
            "t_1/2    = ln(2) / lambda_z",
            "MRT      = AUMC / AUC",
            "```",
            "",
            "---",
            "",
            "## 10. Scientific Limitations",
            "",
            "- Caco-2 permeability is an in vitro screening endpoint, not validated human oral absorption.",
            "- The binary class threshold is a dataset-derived median, not a clinical cutoff.",
            "- Permeability-related assumptions are mapped to F and ka, not true systemic CL.",
            "- True systemic CL remains unchanged unless explicitly edited by the user.",
            "- Scaffold split validation is stricter than random split but is not prospective external validation.",
            "- Solubility, transporters, metabolism, protein binding, dose, formulation, and physiology all influence real exposure.",
            "- The PK/NCA simulator is mechanistic education from assumed parameters, not PBPK prediction.",
            "- This app does NOT provide validated human PK, PBPK, dose selection, safety, efficacy, or regulatory conclusions.",
            "",
            "---",
            "",
            "## 11. References and Scientific Grounding",
            "",
            *reference_lines,
        ]
    )


# ---------------------------------------------------------------------------
# Observed PK curve loader (placeholder — no bundled observed data)
# ---------------------------------------------------------------------------

def load_observed_pk_curve(drug_name: str) -> None:
    """Return observed concentration-time data for a named drug, or None.

    No observed clinical PK data are bundled in this platform.  This function
    always returns None.  If real digitized time-concentration data with
    citations are added in the future, this function should return a dict with
    keys: time (list[float]), concentration (list[float]), source (str),
    dose (float), route (str), population (str), citation (str), and
    digitization_note (str).

    Callers must check for None and display:
    "No observed concentration-time data are bundled for this molecule.
    The displayed curves are educational simulations only."
    """
    return None  # No observed data bundled — always educational simulation


# ---------------------------------------------------------------------------
# Multi-drug PK comparison
# ---------------------------------------------------------------------------

def multi_drug_pk_comparison(
    entries: list[dict[str, object]],
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Compute reference vs permeability-adjusted PK for multiple drugs.

    Parameters
    ----------
    entries:
        List of dicts with keys: name (str), probability (float 0-1).

    Returns
    -------
    metrics : pd.DataFrame
        One row per drug with all exposure ratios.
    profiles : dict[str, pd.DataFrame]
        Map of drug name → merged reference/adjusted concentration-time profile.
    """
    rows: list[dict[str, object]] = []
    profiles: dict[str, pd.DataFrame] = {}

    for entry in entries:
        name = str(entry["name"])
        prob = float(entry["probability"])
        assumptions = permeability_to_pk_assumptions(prob)
        kel = assumptions["true_cl"] / assumptions["vd"]

        ref_auc = ref_cmax = ref_tmax = ref_clf = float("nan")
        adj_auc = adj_cmax = adj_tmax = adj_clf = float("nan")
        ref_profile = adj_profile = None

        for scenario, f_val, ka_val in [
            ("reference", assumptions["reference_f"], assumptions["reference_ka"]),
            ("adjusted", assumptions["adjusted_f"], assumptions["adjusted_ka"]),
        ]:
            try:
                profile, _ = simulate_pk_profile(
                    route="oral",
                    dose=assumptions["dose"],
                    vd=assumptions["vd"],
                    kel=kel,
                    duration=assumptions["duration"],
                    interval=assumptions["interval"],
                    ka=ka_val,
                    bioavailability=f_val,
                )
                nca, _ = calculate_nca(
                    profile, dose=assumptions["dose"], route="oral", bioavailability=f_val
                )
                if scenario == "reference":
                    ref_auc = float(nca["auc_inf"])
                    ref_cmax = float(nca["cmax"])
                    ref_tmax = float(nca["tmax"])
                    ref_clf = float(nca["clearance"])
                    ref_profile = profile
                else:
                    adj_auc = float(nca["auc_inf"])
                    adj_cmax = float(nca["cmax"])
                    adj_tmax = float(nca["tmax"])
                    adj_clf = float(nca["clearance"])
                    adj_profile = profile
            except Exception:
                pass

        auc_ratio = _safe_ratio(adj_auc, ref_auc)
        cmax_ratio = _safe_ratio(adj_cmax, ref_cmax)
        tmax_shift = adj_tmax - ref_tmax if math.isfinite(adj_tmax) and math.isfinite(ref_tmax) else float("nan")
        clf_ratio = _safe_ratio(adj_clf, ref_clf)

        rows.append(
            {
                "molecule": name,
                "probability": round(prob, 3),
                "suggested_f": assumptions["adjusted_f"],
                "suggested_ka": assumptions["adjusted_ka"],
                "true_cl": assumptions["true_cl"],
                "ref_auc": ref_auc,
                "adj_auc": adj_auc,
                "auc_ratio": auc_ratio,
                "ref_cmax": ref_cmax,
                "adj_cmax": adj_cmax,
                "cmax_ratio": cmax_ratio,
                "tmax_shift": tmax_shift,
                "ref_clf": ref_clf,
                "adj_clf": adj_clf,
                "clf_ratio": clf_ratio,
            }
        )

        if ref_profile is not None and adj_profile is not None:
            merged = pd.merge(
                ref_profile.rename(columns={"concentration": f"{name} (ref)"})[["time", f"{name} (ref)"]],
                adj_profile.rename(columns={"concentration": f"{name} (adj)"})[["time", f"{name} (adj)"]],
                on="time",
            )
            profiles[name] = merged

    return pd.DataFrame(rows), profiles


# ---------------------------------------------------------------------------
# Experiment recommendation engine
# ---------------------------------------------------------------------------

def experiment_recommendation(
    name: str,
    probability: float,
    confidence_cat: str,
    domain_cat: str,
    outside_domain: bool,
    descriptors: dict[str, object],
) -> dict[str, str]:
    """Return beginner and PhD-level next-experiment recommendations.

    Parameters are derived from the model prediction and descriptor analysis.
    All recommendations are hypothesis-generating, not clinical guidance.
    """
    tpsa = float(descriptors.get("tpsa", 90))
    hbd = int(descriptors.get("hbd", 2))
    logp = float(descriptors.get("logp", 2))
    conf_high = "high" in confidence_cat.lower()
    conf_low = "low" in confidence_cat.lower()
    name_lower = name.lower()

    beginner: list[str] = []
    phd: list[str] = []

    if outside_domain or "outside" in domain_cat.lower():
        beginner.append(
            f"The model is extrapolating for {name} — it has low similarity to its training chemistry. "
            "Prioritize experimental Caco-2 or MDCK permeability measurement before relying on this prediction."
        )
        phd.append(
            f"Tanimoto nearest-neighbor similarity is below the applicability-domain threshold for {name}. "
            "Prediction uncertainty is elevated beyond what the probability score communicates; "
            "experimental follow-up is strongly recommended before any decision-critical use."
        )
    elif conf_high and probability >= 0.65:
        beginner.append(
            f"The model gives a confident high-permeability signal for {name}. "
            "If the decision is critical, confirm with an in vitro Caco-2 or PAMPA assay."
        )
        phd.append(
            "High classifier confidence reduces decision-boundary uncertainty. "
            "Recommended follow-up: Caco-2 bidirectional Papp (A→B and B→A) to identify active efflux, "
            "paired with kinetic solubility at physiological pH."
        )
    elif conf_low or probability < 0.45:
        beginner.append(
            f"The model predicts low permeability for {name}. "
            "Check solubility, ionization, formulation options, and consider whether transporters might help."
        )
        phd.append(
            "Low permeability class: consider high polarity, hydrogen-bonding burden, or size penalty. "
            "Evaluate efflux transporter expression (P-gp/BCRP), passive vs active permeability, "
            "solubility-limited absorption scenarios, and pH-partition effects."
        )
    else:
        beginner.append(
            f"{name} is borderline — the model is not decisive. "
            "Experimental permeability data will be more informative than model output here."
        )
        phd.append(
            "Borderline probability (near 0.5) indicates low model decisiveness. "
            "Consider Caco-2 at multiple pH values, transcellular vs paracellular contribution "
            "assessment, and ionization-state profiling."
        )

    if tpsa > 120 or hbd > 3:
        beginner.append(
            "High polarity and hydrogen bonding detected. "
            "Consider whether transporter-mediated uptake might support absorption."
        )
        phd.append(
            f"TPSA = {tpsa:.1f} Å², HBD = {hbd}: high desolvation cost limits passive transcellular diffusion. "
            "Evaluate OCT/OAT/OATP transporter substrate potential, especially for polar zwitterions or amines."
        )

    if logp > 5:
        beginner.append(
            "High lipophilicity may improve membrane crossing but can hurt water solubility."
        )
        phd.append(
            f"LogP = {logp:.2f} raises solubility-limited absorption and assay-binding concerns. "
            "Combine FaSSIF/FeSSIF solubility measurement with Caco-2 to separate permeability from solubility effects."
        )

    if "metformin" in name_lower or (tpsa > 140 and hbd >= 4):
        beginner.append(
            "This looks like a highly polar compound. "
            "For drugs like metformin, transporters are more important than passive permeability alone."
        )
        phd.append(
            "For metformin-class compounds (biguanides, high TPSA/HBD): passive permeability prediction "
            "is insufficient. OCT1 hepatic uptake and OCT2/MATE1 renal secretion dominate disposition. "
            "The Caco-2 model cannot capture transporter-mediated absorption."
        )

    return {
        "beginner": " ".join(beginner),
        "phd": " ".join(phd),
    }


# ---------------------------------------------------------------------------
# Multi-drug report section builder
# ---------------------------------------------------------------------------

MULTI_DRUG_COMPARISON_DISCLAIMER = (
    "All curves are educational simulations generated from permeability-mapped F and ka assumptions. "
    "No observed concentration-time data are bundled. "
    "True systemic CL is fixed by design; only absorption assumptions change between scenarios. "
    "This is hypothesis-generating, not validated human PK."
)


def build_multi_drug_comparison_report(
    metrics: pd.DataFrame,
    had_literature_profiles: list[str],
) -> str:
    """Build a downloadable markdown section for multi-drug PK comparison."""
    mol_list = ", ".join(str(m) for m in metrics["molecule"].tolist())
    metric_lines = []
    for _, row in metrics.iterrows():
        metric_lines.append(
            f"| {row['molecule']} | {row['probability']:.3f} | "
            f"{row['suggested_f']:.3f} | {row['suggested_ka']:.3f} | "
            f"{row['auc_ratio']:.3f} | {row['cmax_ratio']:.3f} | "
            f"{row['clf_ratio']:.3f} |"
        )

    lit_note = (
        f"Literature teaching presets were available for: {', '.join(had_literature_profiles)}. "
        "These are approximate educational values and are NOT observed clinical PK data."
        if had_literature_profiles
        else "No literature teaching presets were loaded for this comparison."
    )

    return "\n".join(
        [
            "## Multi-Drug PK Impact Comparison",
            "",
            f"Molecules compared: {mol_list}",
            "",
            "| Molecule | Probability | Suggested F | Suggested ka | AUC ratio | Cmax ratio | CL/F ratio |",
            "|---|---|---|---|---|---|---|",
            *metric_lines,
            "",
            f"**Literature teaching presets:** {lit_note}",
            "",
            "**Observed data:** No observed concentration-time data are bundled for any molecule. "
            "All curves are educational simulations.",
            "",
            f"**Disclaimer:** {MULTI_DRUG_COMPARISON_DISCLAIMER}",
        ]
    )
