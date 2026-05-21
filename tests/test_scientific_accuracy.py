"""Tests verifying scientifically correct language and F/ka framing throughout the codebase."""
from __future__ import annotations

import ast
import math
from pathlib import Path

import pytest

from adme_predictor.drug_pk_profiles import DRUG_PK_PROFILES
from adme_predictor.education import (
    F_MISMATCH_THRESHOLD,
    F_SCENARIO_DISCLAIMER,
    permeability_to_pk_assumptions,
)
from adme_predictor.reporting import svg_to_html_page, render_molecule_svg


# ---------------------------------------------------------------------------
# Language safety checks on source files
# ---------------------------------------------------------------------------

_APP_SOURCE = Path("app/streamlit_app.py").read_text(encoding="utf-8")
_EDUCATION_SOURCE = Path("src/adme_predictor/education.py").read_text(encoding="utf-8")
_PROFILE_SOURCE = Path("src/adme_predictor/drug_pk_profiles.py").read_text(encoding="utf-8")


def _app_user_text_lines() -> list[str]:
    """Extract user-facing string literals from the app source."""
    lines = []
    for line in _APP_SOURCE.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        lines.append(stripped.lower())
    return lines


def test_no_predicted_f_language_in_user_facing_strings() -> None:
    """App must not tell users the ML model predicts F.

    This test scans only string literals (not Python identifiers or variable
    names) to avoid false positives from code like ``if prediction is None``.
    """
    tree = ast.parse(_APP_SOURCE)
    bad_phrases = [
        "model predicts f", "predicted bioavailability", "predicts bioavailability",
        "f prediction", "f predicted",
    ]
    negation_words = ["does not", "not predict", "not model-predicted", "not a prediction",
                      "illustrative", "not measured", "NOT model-predicted"]
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lower = node.value.lower()
            if any(phrase in lower for phrase in bad_phrases):
                if not any(neg in node.value for neg in negation_words) and \
                   not any(neg in lower for neg in ["does not", "not predict", "not a prediction"]):
                    violations.append(node.value[:120])
    assert not violations, (
        "String literal implies ML model predicts F:\n" + "\n".join(violations[:3])
    )


def test_no_permeability_predicts_cl_in_user_facing_strings() -> None:
    """App must not claim permeability changes true systemic clearance."""
    tree = ast.parse(_APP_SOURCE)
    bad = ["permeability changes clearance", "permeability predicts clearance",
           "caco-2 predicts cl", "permeability determines cl"]
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lower = node.value.lower()
            if any(p in lower for p in bad):
                violations.append(node.value[:100])
    assert not violations, "String literal claims permeability changes CL:\n" + "\n".join(violations[:3])


def test_no_validated_human_pk_claim_in_user_facing_strings() -> None:
    """App must not claim to predict validated human PK.

    Disclaimers that mention what would be REQUIRED for validated PK are allowed.
    Only positive assertions are flagged.
    """
    tree = ast.parse(_APP_SOURCE)
    bad = ["predicts validated human pk", "provides validated human pk",
           "validated human pk is available"]
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lower = node.value.lower()
            if any(p in lower for p in bad):
                violations.append(node.value[:100])
    assert not violations, "String literal claims validated human PK:\n" + "\n".join(violations[:3])


def test_f_scenario_disclaimer_present_in_education() -> None:
    """education.py must contain the F scenario disclaimer constant."""
    assert "F_SCENARIO_DISCLAIMER" in _EDUCATION_SOURCE
    assert "does NOT predict human bioavailability" in F_SCENARIO_DISCLAIMER or \
           "does not predict" in F_SCENARIO_DISCLAIMER.lower()


def test_absorption_sensitivity_language_in_app() -> None:
    """App must use 'scenario' or 'assumption' language for F/ka values."""
    good_patterns = ["scenario f", "educational f assumption", "scenario assumption",
                     "sensitivity", "user-editable"]
    found = any(p in _APP_SOURCE.lower() for p in good_patterns)
    assert found, "App does not use scenario/assumption language for F/ka"


# ---------------------------------------------------------------------------
# Drug profile literature F validation
# ---------------------------------------------------------------------------

def test_aspirin_profile_has_hydrolysis_warning() -> None:
    """Aspirin profile must mention hydrolysis or presystemic loss."""
    profile = DRUG_PK_PROFILES.get("aspirin", {})
    all_text = " ".join(str(v) for v in profile.values() if isinstance(v, str)).lower()
    warnings_text = " ".join(str(w) for w in profile.get("warning_notes", [])).lower()
    assert "hydroly" in all_text or "presystemic" in all_text or "hydroly" in warnings_text, (
        "Aspirin profile does not mention hydrolysis or presystemic loss"
    )


def test_caffeine_profile_has_complete_absorption_note() -> None:
    """Caffeine profile must indicate near-complete oral bioavailability."""
    profile = DRUG_PK_PROFILES.get("caffeine", {})
    all_text = " ".join(str(v) for v in profile.values() if isinstance(v, str)).lower()
    assert "complete" in all_text or "f_literature" in all_text or "1.0" in all_text, (
        "Caffeine profile does not mention near-complete oral bioavailability"
    )


def test_caffeine_f_literature_is_near_one() -> None:
    """Caffeine literature F should be very high (≥ 0.95)."""
    profile = DRUG_PK_PROFILES.get("caffeine", {})
    f_lit = profile.get("f_literature")
    if f_lit is not None:
        assert float(f_lit) >= 0.95, f"Caffeine literature F should be near 1.0, got {f_lit}"


def test_aspirin_f_literature_is_below_0_8() -> None:
    """Aspirin literature F should reflect its formulation-dependent/hydrolysis-affected value."""
    profile = DRUG_PK_PROFILES.get("aspirin", {})
    f_lit = profile.get("f_literature")
    if f_lit is not None:
        assert float(f_lit) <= 0.75, f"Aspirin literature F should be < 0.75 (formulation/hydrolysis), got {f_lit}"


def test_all_profiles_have_profile_type() -> None:
    """All drug profiles must have profile_type = 'literature teaching preset'."""
    for key, profile in DRUG_PK_PROFILES.items():
        assert profile.get("profile_type") == "literature teaching preset", (
            f"Profile {key} missing profile_type='literature teaching preset'"
        )


def test_f_mismatch_threshold_is_defined() -> None:
    assert isinstance(F_MISMATCH_THRESHOLD, float)
    assert 0 < F_MISMATCH_THRESHOLD < 1


# ---------------------------------------------------------------------------
# permeability_to_pk_assumptions uses scenario_f/ka keys
# ---------------------------------------------------------------------------

def test_scenario_f_key_present() -> None:
    result = permeability_to_pk_assumptions(0.7)
    assert "scenario_f" in result, "permeability_to_pk_assumptions must return scenario_f key"
    assert "scenario_ka" in result


def test_scenario_f_within_valid_range() -> None:
    for prob in [0.0, 0.25, 0.5, 0.75, 1.0]:
        result = permeability_to_pk_assumptions(prob)
        assert 0 < result["scenario_f"] <= 1.0
        assert result["scenario_ka"] > 0


def test_higher_probability_gives_higher_scenario_f() -> None:
    low = permeability_to_pk_assumptions(0.1)
    high = permeability_to_pk_assumptions(0.9)
    assert high["scenario_f"] > low["scenario_f"]
    assert high["scenario_ka"] > low["scenario_ka"]


def test_legacy_adjusted_f_alias_still_works() -> None:
    """adjusted_f legacy alias must still be present for backward compatibility."""
    result = permeability_to_pk_assumptions(0.5)
    assert "adjusted_f" in result
    assert result["adjusted_f"] == result["scenario_f"]


# ---------------------------------------------------------------------------
# SVG rendering and HTML wrapper
# ---------------------------------------------------------------------------

def test_svg_to_html_page_contains_svg() -> None:
    svg = render_molecule_svg("CC(=O)Oc1ccccc1C(=O)O")
    html = svg_to_html_page(svg)
    assert "<!DOCTYPE html>" in html
    assert "<svg" in html
    assert "<body>" in html
    assert "<?xml" not in html  # XML declaration should be stripped


def test_svg_to_html_page_has_white_background() -> None:
    svg = render_molecule_svg("Cn1cnc2c1c(=O)n(C)c(=O)n2C")
    html = svg_to_html_page(svg)
    assert "background" in html.lower()


def test_svg_rendering_all_core_drugs() -> None:
    """All 10 core drugs must render non-empty SVGs."""
    core_drugs = {
        "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
        "caffeine": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
        "ibuprofen": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        "metformin": "CN(C)C(=N)N=C(N)N",
        "propranolol": "CC(C)NCC(O)COc1cccc2ccccc12",
        "atenolol": "CC(C)NCC(O)COc1ccc(CC(N)=O)cc1",
        "warfarin": "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
        "diazepam": "CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21",
        "midazolam": "Cc1ncc2n1-c1ccc(Cl)cc1C(=NC2)c1ccccc1F",
        "omeprazole": "COc1ccc2c(c1)[nH]c(CS(=O)c1ncccc1C)n2",
    }
    for name, smiles in core_drugs.items():
        svg = render_molecule_svg(smiles)
        assert "<svg" in svg and len(svg) > 200, f"SVG empty/invalid for {name}"
        html = svg_to_html_page(svg)
        assert "<!DOCTYPE html>" in html and "<svg" in html, f"HTML wrapper failed for {name}"
