"""Tests for multi-drug PK comparison, experiment recommendations, and observed-data placeholder."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from adme_predictor.education import (
    MULTI_DRUG_COMPARISON_DISCLAIMER,
    build_multi_drug_comparison_report,
    experiment_recommendation,
    load_observed_pk_curve,
    multi_drug_pk_comparison,
)


# ---------------------------------------------------------------------------
# load_observed_pk_curve — must always return None (no bundled observed data)
# ---------------------------------------------------------------------------


def test_load_observed_pk_curve_returns_none_for_aspirin():
    result = load_observed_pk_curve("aspirin")
    assert result is None


def test_load_observed_pk_curve_returns_none_for_unknown_drug():
    result = load_observed_pk_curve("unknown_drug_xyz")
    assert result is None


def test_load_observed_pk_curve_returns_none_for_empty_string():
    result = load_observed_pk_curve("")
    assert result is None


# ---------------------------------------------------------------------------
# multi_drug_pk_comparison — correctness
# ---------------------------------------------------------------------------

THREE_MOLECULES = [
    {"name": "Aspirin", "probability": 0.72},
    {"name": "Metformin", "probability": 0.31},
    {"name": "Ibuprofen", "probability": 0.85},
]

FIVE_MOLECULES = [
    {"name": "Aspirin", "probability": 0.72},
    {"name": "Caffeine", "probability": 0.80},
    {"name": "Metformin", "probability": 0.31},
    {"name": "Propranolol", "probability": 0.68},
    {"name": "Ibuprofen", "probability": 0.85},
]


def test_multi_drug_comparison_returns_results_for_three_molecules():
    metrics, profiles = multi_drug_pk_comparison(THREE_MOLECULES)
    assert len(metrics) == 3
    assert set(metrics["molecule"].tolist()) == {"Aspirin", "Metformin", "Ibuprofen"}


def test_multi_drug_comparison_auc_ratio_table_generated():
    metrics, _ = multi_drug_pk_comparison(THREE_MOLECULES)
    assert "auc_ratio" in metrics.columns
    finite_ratios = [v for v in metrics["auc_ratio"] if math.isfinite(v)]
    assert len(finite_ratios) == 3, "Expected 3 finite AUC ratios"


def test_multi_drug_comparison_cmax_ratio_table_generated():
    metrics, _ = multi_drug_pk_comparison(THREE_MOLECULES)
    assert "cmax_ratio" in metrics.columns
    finite_ratios = [v for v in metrics["cmax_ratio"] if math.isfinite(v)]
    assert len(finite_ratios) == 3


def test_multi_drug_comparison_clf_ratio_table_generated():
    metrics, _ = multi_drug_pk_comparison(THREE_MOLECULES)
    assert "clf_ratio" in metrics.columns
    finite_ratios = [v for v in metrics["clf_ratio"] if math.isfinite(v)]
    assert len(finite_ratios) == 3


def test_multi_drug_comparison_true_cl_fixed():
    """True CL must be the same for all drugs — only absorption changes."""
    metrics, _ = multi_drug_pk_comparison(FIVE_MOLECULES)
    assert "true_cl" in metrics.columns
    cl_values = metrics["true_cl"].dropna().unique()
    assert len(cl_values) == 1, f"True CL must be fixed; got multiple values: {cl_values}"


def test_multi_drug_comparison_auc_ratio_positive_for_high_probability():
    """High-probability drug should have AUC ratio > 1 (adjusted > reference)."""
    metrics, _ = multi_drug_pk_comparison([{"name": "Ibuprofen", "probability": 0.95}])
    row = metrics.iloc[0]
    assert row["auc_ratio"] > 1.0, "High probability should map to higher adjusted F and AUC > reference"


def test_multi_drug_comparison_auc_ratio_less_than_one_for_low_probability():
    """Low-probability drug should have AUC ratio < 1 (adjusted < reference)."""
    metrics, _ = multi_drug_pk_comparison([{"name": "Metformin", "probability": 0.05}])
    row = metrics.iloc[0]
    assert row["auc_ratio"] < 1.0, "Low probability should map to lower adjusted F and AUC < reference"


def test_multi_drug_comparison_profiles_returned():
    metrics, profiles = multi_drug_pk_comparison(THREE_MOLECULES)
    assert len(profiles) == 3
    for name in ["Aspirin", "Metformin", "Ibuprofen"]:
        assert name in profiles
        p = profiles[name]
        assert "time" in p.columns or p.index.name == "time"


# ---------------------------------------------------------------------------
# experiment_recommendation
# ---------------------------------------------------------------------------

_BASE_DESCRIPTORS = {"tpsa": 80, "hbd": 2, "hba": 4, "logp": 2.5, "molecular_weight": 300}


def test_experiment_recommendation_returns_beginner_and_phd_keys():
    rec = experiment_recommendation(
        name="Aspirin", probability=0.72, confidence_cat="high confidence",
        domain_cat="within domain", outside_domain=False,
        descriptors=_BASE_DESCRIPTORS,
    )
    assert "beginner" in rec
    assert "phd" in rec
    assert len(rec["beginner"]) > 20
    assert len(rec["phd"]) > 20


def test_experiment_recommendation_outside_domain_mentions_measurement():
    rec = experiment_recommendation(
        name="Unknown", probability=0.50, confidence_cat="moderate confidence",
        domain_cat="outside domain", outside_domain=True,
        descriptors=_BASE_DESCRIPTORS,
    )
    assert "experimental" in rec["beginner"].lower() or "measurement" in rec["beginner"].lower()


def test_experiment_recommendation_metformin_mentions_transporter():
    rec = experiment_recommendation(
        name="Metformin", probability=0.30, confidence_cat="low confidence",
        domain_cat="within domain", outside_domain=False,
        descriptors={"tpsa": 105, "hbd": 5, "hba": 6, "logp": -1.4, "molecular_weight": 129},
    )
    combined = rec["beginner"] + rec["phd"]
    assert "transporter" in combined.lower() or "OCT" in combined


def test_experiment_recommendation_high_tpsa_mentions_polarity():
    rec = experiment_recommendation(
        name="HighPolarMol", probability=0.25, confidence_cat="moderate confidence",
        domain_cat="within domain", outside_domain=False,
        descriptors={"tpsa": 140, "hbd": 4, "hba": 7, "logp": 0.5, "molecular_weight": 350},
    )
    combined = rec["beginner"] + rec["phd"]
    assert "tpsa" in combined.lower() or "polarity" in combined.lower() or "transporter" in combined.lower()


# ---------------------------------------------------------------------------
# build_multi_drug_comparison_report
# ---------------------------------------------------------------------------


def test_build_multi_drug_report_contains_molecule_names():
    metrics, _ = multi_drug_pk_comparison(THREE_MOLECULES)
    report = build_multi_drug_comparison_report(metrics, had_literature_profiles=[])
    for name in ["Aspirin", "Metformin", "Ibuprofen"]:
        assert name in report


def test_build_multi_drug_report_does_not_say_observed():
    """Report must not describe simulated curves as 'observed'."""
    metrics, _ = multi_drug_pk_comparison(THREE_MOLECULES)
    report = build_multi_drug_comparison_report(metrics, had_literature_profiles=[])
    # 'observed' is only allowed in the context of 'No observed data are bundled'
    observed_occurrences = [
        line for line in report.splitlines()
        if "observed" in line.lower() and "no observed" not in line.lower()
    ]
    assert not observed_occurrences, (
        "Report uses 'observed' in a positive claim context:\n"
        + "\n".join(observed_occurrences)
    )


def test_build_multi_drug_report_includes_disclaimer():
    metrics, _ = multi_drug_pk_comparison(THREE_MOLECULES)
    report = build_multi_drug_comparison_report(metrics, had_literature_profiles=[])
    assert "educational" in report.lower()
    assert "not validated" in report.lower() or MULTI_DRUG_COMPARISON_DISCLAIMER[:30] in report


def test_build_multi_drug_report_labels_literature_as_approximate():
    metrics, _ = multi_drug_pk_comparison([{"name": "Aspirin", "probability": 0.72}])
    report = build_multi_drug_comparison_report(metrics, had_literature_profiles=["Aspirin"])
    assert "approximate" in report.lower() or "teaching" in report.lower()
    assert "NOT observed" in report or "not observed" in report.lower()


# ---------------------------------------------------------------------------
# App source text safety checks
# ---------------------------------------------------------------------------


def test_app_does_not_label_simulated_curves_as_observed():
    """Streamlit app source must not positively assert that simulated curves are real observed data.

    Disclaimers that say 'No observed ...', 'not observed ...' or 'NOT observed ...' are fine.
    Only lines that make a positive claim (e.g. 'these are observed clinical curves') are flagged.
    """
    source = Path("app/streamlit_app.py").read_text(encoding="utf-8")
    # Patterns that would mislead — but only if the line does NOT also contain a negation
    bad_patterns = [
        "observed clinical pk",
        "observed concentration-time data are available",
        "observed pk curve is shown",
    ]
    suspicious = [
        line.strip() for line in source.splitlines()
        if any(pat in line.lower() for pat in bad_patterns)
        and not line.strip().startswith("#")
        and "not" not in line.lower()
        and "no " not in line.lower()
    ]
    assert not suspicious, (
        "App makes a misleading positive 'observed' claim:\n" + "\n".join(suspicious[:5])
    )


def test_literature_teaching_preset_labeled_as_approximate():
    source = Path("app/streamlit_app.py").read_text(encoding="utf-8")
    assert "approximate" in source.lower() or "teaching preset" in source.lower(), (
        "Literature profiles must be labeled as approximate / teaching preset"
    )
