import pandas as pd
import pytest

from adme_predictor.education import (
    PK_EQUATIONS_TEXT,
    SCIENTIFIC_BOUNDARIES,
    WHAT_THIS_APP_DOES,
    build_downloadable_report,
    comparison_interpretations,
    permeability_to_pk_assumptions,
    pk_impact_interpretations,
    pk_impact_profiles,
    pk_impact_table,
)


# ---------------------------------------------------------------------------
# Existing tests (preserved)
# ---------------------------------------------------------------------------


def test_downloadable_report_includes_prediction_auc_ratio_and_clf_explanation():
    pk_table = pk_impact_table(0.8)
    report = build_downloadable_report(
        molecule_name="Aspirin",
        category="Analgesics/NSAIDs",
        smiles="CC(=O)Oc1ccccc1C(=O)O",
        canonical_smiles="CC(=O)Oc1ccccc1C(=O)O",
        descriptors={"molecular_weight": 180.16, "logp": 1.2, "tpsa": 63.6},
        prediction={"predicted_label": "high permeability class", "high_permeability_probability": 0.9},
        confidence={"confidence_category": "High confidence", "confidence_score": 0.8, "prediction_entropy": 0.4},
        applicability={"applicability_category": "In domain", "nearest_neighbor_similarity": 0.7, "applicability_warning": ""},
        pk_table=pk_table,
    )

    assert "Aspirin" in report
    assert "high permeability class" in report
    assert "AUC ratio" in report
    assert "CL/F" in report
    assert "Permeability-related assumptions are mapped to F and ka, not true systemic CL" in report


def test_comparison_interpretations_have_beginner_and_phd_versions():
    comparison = pd.DataFrame(
        [
            {"molecule": "Metformin", "tpsa": 88.9, "logp": -1.0},
            {"molecule": "Ibuprofen", "tpsa": 37.3, "logp": 3.5},
        ]
    )
    text = comparison_interpretations(comparison)

    assert "Polar molecules often cross membranes less easily" in text["beginner"]
    assert "AUC_oral = F × Dose / CL" in text["phd"]
    assert "true systemic CL" in text["phd"]


def test_equations_include_oral_auc_and_do_not_overclaim():
    assert "AUC_oral = F × Dose / CL" in PK_EQUATIONS_TEXT
    assert "Permeability changes true CL" not in PK_EQUATIONS_TEXT
    assert "validated human PK prediction" not in PK_EQUATIONS_TEXT


def test_pk_impact_profiles_include_reference_and_sensitivity_curves():
    profiles = pk_impact_profiles(0.8)
    scenarios = set(profiles["scenario"])
    assert any("Reference" in s for s in scenarios), f"Missing reference scenario in: {scenarios}"
    assert any("Sensitivity" in s or "scenario" in s.lower() for s in scenarios), (
        f"Missing sensitivity scenario in: {scenarios}"
    )
    assert {"time", "concentration", "F", "ka"}.issubset(profiles.columns)


# ---------------------------------------------------------------------------
# New tests (Part 21)
# ---------------------------------------------------------------------------


def test_high_permeability_maps_to_higher_f_and_ka_than_low():
    high = permeability_to_pk_assumptions(0.9)
    low = permeability_to_pk_assumptions(0.1)
    assert high["adjusted_f"] > low["adjusted_f"]
    assert high["adjusted_ka"] > low["adjusted_ka"]


def test_decreasing_f_decreases_auc_when_dose_and_cl_fixed():
    table_high = pk_impact_table(0.95)
    table_low = pk_impact_table(0.05)
    # adjusted_f is lower for low probability => adjusted AUC should be lower
    auc_high = float(table_high.iloc[1]["AUC"])
    auc_low = float(table_low.iloc[1]["AUC"])
    assert auc_high > auc_low


def test_true_cl_unchanged_between_reference_and_adjusted_scenarios():
    table = pk_impact_table(0.6)
    ref_cl = float(table.iloc[0]["true_CL"])
    adj_cl = float(table.iloc[1]["true_CL"])
    assert ref_cl == adj_cl


def test_clf_increases_when_f_decreases():
    """CL/F must increase when F decreases under fixed dose and true CL."""
    table_high_f = pk_impact_table(0.95)
    table_low_f = pk_impact_table(0.05)
    clf_high = float(table_high_f.iloc[1]["CL/F"])
    clf_low = float(table_low_f.iloc[1]["CL/F"])
    assert clf_low > clf_high


def test_auc_ratio_equals_adjusted_divided_by_reference():
    table = pk_impact_table(0.7)
    ref_auc = float(table.iloc[0]["AUC"])
    adj_auc = float(table.iloc[1]["AUC"])
    stated_ratio = float(table.iloc[1]["AUC_ratio_vs_reference"])
    computed_ratio = adj_auc / ref_auc
    assert abs(stated_ratio - computed_ratio) < 1e-6


def test_report_includes_selected_molecule_prediction_and_scientific_limits():
    pk_table = pk_impact_table(0.7)
    report = build_downloadable_report(
        molecule_name="Caffeine",
        category="Natural products",
        smiles="Cn1cnc2c1c(=O)n(C)c(=O)n2C",
        canonical_smiles="Cn1cnc2c1c(=O)n(C)c(=O)n2C",
        descriptors={"molecular_weight": 194.19, "logp": -0.07, "tpsa": 58.4},
        prediction={"predicted_label": "high permeability class", "high_permeability_probability": 0.78,
                    "prediction_source": "trained Caco-2 classifier"},
        confidence={"confidence_category": "Medium confidence", "confidence_score": 0.56, "prediction_entropy": 0.65},
        applicability={"applicability_category": "In domain", "nearest_neighbor_similarity": 0.6, "applicability_warning": ""},
        pk_table=pk_table,
    )
    assert "Caffeine" in report
    assert "AUC ratio" in report
    assert "CL/F" in report
    assert "Scientific Limitations" in report


def test_report_does_not_claim_permeability_changes_true_cl():
    pk_table = pk_impact_table(0.5)
    report = build_downloadable_report(
        molecule_name="Metformin",
        category="PK teaching examples",
        smiles="CN(C)C(=N)NC(=N)N",
        canonical_smiles="CN(C)C(=N)NC(=N)N",
        descriptors={"molecular_weight": 129.16, "logp": -1.43, "tpsa": 88.9},
        prediction={"predicted_label": "low permeability class", "high_permeability_probability": 0.2,
                    "prediction_source": "trained Caco-2 classifier"},
        confidence={"confidence_category": "High confidence", "confidence_score": 0.8, "prediction_entropy": 0.35},
        applicability={"applicability_category": "In domain", "nearest_neighbor_similarity": 0.55, "applicability_warning": ""},
        pk_table=pk_table,
    )
    lower = report.lower()
    assert "permeability changes true cl" not in lower
    assert "permeability changes true systemic clearance" not in lower


def test_report_does_not_claim_validated_human_pk_prediction():
    pk_table = pk_impact_table(0.5)
    report = build_downloadable_report(
        molecule_name="Ibuprofen",
        category="Analgesics/NSAIDs",
        smiles="CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        canonical_smiles="CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        descriptors={"molecular_weight": 206.28, "logp": 3.5, "tpsa": 37.3},
        prediction={"predicted_label": "high permeability class", "high_permeability_probability": 0.85,
                    "prediction_source": "trained Caco-2 classifier"},
        confidence={"confidence_category": "High confidence", "confidence_score": 0.85, "prediction_entropy": 0.3},
        applicability={"applicability_category": "In domain", "nearest_neighbor_similarity": 0.72, "applicability_warning": ""},
        pk_table=pk_table,
    )
    # The report must not claim validated human PK prediction capability
    assert "validated human PK prediction" not in report
    # Must contain a disclaimer instead
    assert "NOT" in report or "not" in report


def test_pk_impact_table_has_correct_structure():
    table = pk_impact_table(0.75)
    assert len(table) == 2
    required_cols = {"scenario", "F", "ka", "AUC", "Cmax", "Tmax", "true_CL", "CL/F",
                     "AUC_ratio_vs_reference", "Cmax_ratio_vs_reference",
                     "Tmax_shift_vs_reference", "CLF_ratio_vs_reference"}
    assert required_cols.issubset(set(table.columns))
    assert float(table.iloc[0]["AUC_ratio_vs_reference"]) == pytest.approx(1.0)


def test_scientific_boundaries_consistent_with_no_cl_claim():
    """App boundaries must not include 'true CL prediction from permeability' in supports."""
    supported = " ".join(SCIENTIFIC_BOUNDARIES["supports"]).lower()
    assert "true cl prediction" not in supported


def test_what_this_app_does_mentions_educational_and_not_clinical():
    lower = WHAT_THIS_APP_DOES.lower()
    assert "educational" in lower or "learning" in lower
    assert "clinical" in lower  # must mention the boundary explicitly


def test_permeability_assumptions_bounded_between_zero_and_one():
    for prob in [0.0, 0.25, 0.5, 0.75, 1.0]:
        a = permeability_to_pk_assumptions(prob)
        assert 0.0 < a["adjusted_f"] <= 1.0
        assert a["adjusted_ka"] > 0.0


def test_comparison_interpretations_empty_dataframe():
    result = comparison_interpretations(pd.DataFrame())
    assert result["beginner"] == ""
    assert result["phd"] == ""
