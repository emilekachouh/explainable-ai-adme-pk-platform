"""Tests for the fold_change module — safe ratio calculations."""
from __future__ import annotations

import math

import pandas as pd
import pytest

from adme_predictor.fold_change import (
    compute_drug_ratios,
    interpret_ratio,
    multi_drug_interpretation,
    safe_diff,
    safe_ratio,
)


# ---------------------------------------------------------------------------
# safe_ratio
# ---------------------------------------------------------------------------


def test_safe_ratio_normal():
    assert safe_ratio(10.0, 5.0) == pytest.approx(2.0)


def test_safe_ratio_zero_denominator():
    result = safe_ratio(10.0, 0.0)
    assert math.isnan(result)


def test_safe_ratio_none_numerator():
    result = safe_ratio(None, 5.0)
    assert math.isnan(result)


def test_safe_ratio_none_denominator():
    result = safe_ratio(10.0, None)
    assert math.isnan(result)


def test_safe_ratio_nan_denominator():
    result = safe_ratio(10.0, float("nan"))
    assert math.isnan(result)


def test_safe_ratio_inf_numerator():
    result = safe_ratio(float("inf"), 5.0)
    assert math.isnan(result)


def test_safe_ratio_custom_fallback():
    result = safe_ratio(10.0, 0.0, fallback=-1.0)
    assert result == -1.0


def test_safe_ratio_identity():
    assert safe_ratio(7.5, 7.5) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# safe_diff
# ---------------------------------------------------------------------------


def test_safe_diff_normal():
    assert safe_diff(5.0, 3.0) == pytest.approx(2.0)


def test_safe_diff_none():
    assert math.isnan(safe_diff(None, 3.0))
    assert math.isnan(safe_diff(5.0, None))


def test_safe_diff_nan():
    assert math.isnan(safe_diff(float("nan"), 3.0))


def test_safe_diff_zero():
    assert safe_diff(5.0, 5.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# compute_drug_ratios
# ---------------------------------------------------------------------------


_METRICS = pd.DataFrame(
    [
        {"molecule": "RefDrug", "auc": 100.0, "cmax": 10.0, "tmax": 2.0, "clf": 5.0, "f": 0.8, "ka": 1.2},
        {"molecule": "DrugA", "auc": 200.0, "cmax": 20.0, "tmax": 1.5, "clf": 2.5, "f": 0.9, "ka": 1.5},
        {"molecule": "DrugB", "auc": 50.0, "cmax": 5.0, "tmax": 3.0, "clf": 10.0, "f": 0.4, "ka": 0.6},
    ]
)


def test_compute_drug_ratios_auc():
    result = compute_drug_ratios(_METRICS, "RefDrug")
    assert result.loc[result["molecule"] == "DrugA", "auc_ratio"].iloc[0] == pytest.approx(2.0)
    assert result.loc[result["molecule"] == "DrugB", "auc_ratio"].iloc[0] == pytest.approx(0.5)


def test_compute_drug_ratios_reference_is_one():
    result = compute_drug_ratios(_METRICS, "RefDrug")
    ref_row = result[result["molecule"] == "RefDrug"].iloc[0]
    assert ref_row["auc_ratio"] == pytest.approx(1.0)
    assert ref_row["cmax_ratio"] == pytest.approx(1.0)
    assert ref_row["clf_ratio"] == pytest.approx(1.0)
    assert ref_row["tmax_shift"] == pytest.approx(0.0)


def test_compute_drug_ratios_tmax_shift():
    result = compute_drug_ratios(_METRICS, "RefDrug")
    assert result.loc[result["molecule"] == "DrugA", "tmax_shift"].iloc[0] == pytest.approx(-0.5)
    assert result.loc[result["molecule"] == "DrugB", "tmax_shift"].iloc[0] == pytest.approx(1.0)


def test_compute_drug_ratios_f_ratio():
    result = compute_drug_ratios(_METRICS, "RefDrug")
    assert "f_ratio" in result.columns
    assert result.loc[result["molecule"] == "DrugA", "f_ratio"].iloc[0] == pytest.approx(0.9 / 0.8)


def test_compute_drug_ratios_missing_reference():
    result = compute_drug_ratios(_METRICS, "NonExistent")
    assert result["auc_ratio"].apply(math.isnan).all()


def test_compute_drug_ratios_clf_inverse_of_auc():
    """CL/F ratio should be inverse of AUC ratio when dose is fixed."""
    result = compute_drug_ratios(_METRICS, "RefDrug")
    row_a = result[result["molecule"] == "DrugA"].iloc[0]
    # CL/F = Dose/AUC, so CLF_ratio = AUC_ref / AUC_drug = 1 / AUC_ratio
    assert row_a["clf_ratio"] == pytest.approx(1.0 / row_a["auc_ratio"], rel=0.01)


# ---------------------------------------------------------------------------
# interpret_ratio
# ---------------------------------------------------------------------------


def test_interpret_ratio_auc_high():
    result = interpret_ratio("auc", 2.0, "DrugA", "RefDrug")
    assert "higher" in result["beginner"].lower()
    assert "DrugA" in result["beginner"]


def test_interpret_ratio_auc_low():
    result = interpret_ratio("auc", 0.5, "DrugB", "RefDrug")
    assert "lower" in result["beginner"].lower()


def test_interpret_ratio_nan():
    result = interpret_ratio("auc", float("nan"), "DrugA", "RefDrug")
    assert "could not" in result["beginner"].lower() or "undefined" in result["phd"].lower()


def test_interpret_ratio_clf():
    result = interpret_ratio("clf", 2.0, "DrugA", "RefDrug")
    assert "clearance" in result["beginner"].lower() or "clf" in result["phd"].lower()


# ---------------------------------------------------------------------------
# multi_drug_interpretation
# ---------------------------------------------------------------------------


def test_multi_drug_interpretation_returns_keys():
    df = compute_drug_ratios(_METRICS, "RefDrug")
    result = multi_drug_interpretation(df, "RefDrug")
    assert "beginner" in result
    assert "phd" in result
    assert len(result["beginner"]) > 20


def test_multi_drug_interpretation_mentions_reference():
    df = compute_drug_ratios(_METRICS, "RefDrug")
    result = multi_drug_interpretation(df, "RefDrug")
    assert "RefDrug" in result["beginner"] or "RefDrug" in result["phd"]


def test_multi_drug_interpretation_empty_df():
    result = multi_drug_interpretation(pd.DataFrame(), "anything")
    assert result["beginner"] == ""
    assert result["phd"] == ""
