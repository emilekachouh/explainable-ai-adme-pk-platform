"""Tests for batch SMILES screening logic used by render_batch_screening."""
from __future__ import annotations

import io
import textwrap

import pandas as pd
import pytest

from adme_predictor.applicability import assess_applicability_domain
from adme_predictor.demo_model import predict_permeability_class_resilient, prediction_confidence
from adme_predictor.education import permeability_to_pk_assumptions
from adme_predictor.features import (
    calculate_descriptors,
    canonicalize_smiles,
)


def _prediction_with_confidence(smi: str) -> tuple[dict, dict]:
    pred = predict_permeability_class_resilient(smi)
    conf = prediction_confidence(pred)
    return pred, conf


# ---------------------------------------------------------------------------
# Core batch processing helpers (mirroring what the UI does)
# ---------------------------------------------------------------------------

_BATCH_SMILES = [
    ("Aspirin", "CC(=O)Oc1ccccc1C(=O)O", "NSAIDs"),
    ("Caffeine", "Cn1cnc2c1c(=O)n(C)c(=O)n2C", "Natural products"),
    ("Metformin", "CN(C)C(=N)N=C(N)N", "Antidiabetic"),
    ("Ibuprofen", "CC(C)Cc1ccc(C(C)C(=O)O)cc1", "NSAIDs"),
    ("Warfarin", "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O", "Anticoagulants"),
]

_INVALID_SMILES = [
    ("Bad1", "not_a_smiles", "Test"),
    ("Bad2", "X=Y=Z!!!!", "Test"),
    ("Empty", "", "Test"),
]


def _process_batch(rows: list[tuple[str, str, str]]) -> tuple[list[dict], list[dict]]:
    """Minimal batch processor matching app logic."""
    results, failures = [], []
    for name, smi, cat in rows:
        if not smi:
            failures.append({"name": name, "smiles": smi, "error": "Empty SMILES"})
            continue
        try:
            can = canonicalize_smiles(smi)
            desc = calculate_descriptors(smi)
            pred, conf = _prediction_with_confidence(smi)
            appl = assess_applicability_domain(smi)
            prob = float(pred["high_permeability_probability"])
            pk = permeability_to_pk_assumptions(prob)
            results.append({
                "name": name,
                "category": cat,
                "canonical_smiles": can,
                "MW": round(float(desc.get("molecular_weight", float("nan"))), 1),
                "logP": round(float(desc.get("logp", float("nan"))), 2),
                "TPSA": round(float(desc.get("tpsa", float("nan"))), 1),
                "HBD": int(desc.get("hbd", 0)),
                "HBA": int(desc.get("hba", 0)),
                "predicted_class": str(pred["predicted_label"]),
                "probability": round(prob, 3),
                "confidence_cat": str(conf["confidence_category"]),
                "domain_cat": str(appl["applicability_category"]),
                "domain_sim": round(float(appl["nearest_neighbor_similarity"]), 3),
                "scenario_f": round(float(pk["scenario_f"]), 3),
                "scenario_ka": round(float(pk["scenario_ka"]), 3),
            })
        except Exception as exc:
            failures.append({"name": name, "smiles": smi, "error": str(exc)})
    return results, failures


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------


def test_csv_parser_reads_name_smiles_category() -> None:
    csv_text = "name,smiles,category\nAspirin,CC(=O)Oc1ccccc1C(=O)O,NSAIDs\n"
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [c.strip().lower() for c in df.columns]
    assert "name" in df.columns
    assert "smiles" in df.columns
    assert "category" in df.columns
    assert df["smiles"].iloc[0] == "CC(=O)Oc1ccccc1C(=O)O"


def test_csv_parser_works_without_category() -> None:
    csv_text = "name,smiles\nCaffeine,Cn1cnc2c1c(=O)n(C)c(=O)n2C\n"
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [c.strip().lower() for c in df.columns]
    assert "smiles" in df.columns
    assert "category" not in df.columns


def test_paste_parser_two_column() -> None:
    pasted = "aspirin,CC(=O)Oc1ccccc1C(=O)O\ncaffeine,Cn1cnc2c1c(=O)n(C)c(=O)n2C"
    rows = []
    for idx, line in enumerate(pasted.strip().splitlines(), start=1):
        parts = [p.strip() for p in line.split(",", 1)]
        if len(parts) == 2:
            rows.append((parts[0], parts[1], "Pasted"))
        elif len(parts) == 1 and parts[0]:
            rows.append((f"Compound_{idx}", parts[0], "Pasted"))
    assert len(rows) == 2
    assert rows[0][0] == "aspirin"
    assert rows[1][1] == "Cn1cnc2c1c(=O)n(C)c(=O)n2C"


# ---------------------------------------------------------------------------
# Processing correctness
# ---------------------------------------------------------------------------


def test_batch_valid_smiles_returns_results() -> None:
    results, failures = _process_batch(_BATCH_SMILES)
    assert len(results) == 5
    assert len(failures) == 0


def test_batch_invalid_smiles_handled_gracefully() -> None:
    results, failures = _process_batch(_INVALID_SMILES)
    assert len(results) == 0
    assert len(failures) == 3


def test_batch_mixed_input_separates_results_and_failures() -> None:
    mixed = _BATCH_SMILES[:2] + _INVALID_SMILES[:1]
    results, failures = _process_batch(mixed)
    assert len(results) == 2
    assert len(failures) == 1


def test_batch_output_has_required_columns() -> None:
    results, _ = _process_batch(_BATCH_SMILES[:3])
    required = {
        "name", "category", "canonical_smiles", "MW", "logP", "TPSA",
        "HBD", "HBA", "predicted_class", "probability", "confidence_cat",
        "domain_cat", "domain_sim", "scenario_f", "scenario_ka",
    }
    for row in results:
        assert required.issubset(set(row.keys())), f"Missing columns in row for {row['name']}"


def test_batch_probability_in_valid_range() -> None:
    results, _ = _process_batch(_BATCH_SMILES)
    for row in results:
        assert 0.0 <= row["probability"] <= 1.0, f"Probability out of range for {row['name']}"


def test_batch_scenario_f_in_valid_range() -> None:
    results, _ = _process_batch(_BATCH_SMILES)
    for row in results:
        assert 0.0 < row["scenario_f"] <= 1.0, f"scenario_f out of range for {row['name']}"


def test_batch_scenario_ka_positive() -> None:
    results, _ = _process_batch(_BATCH_SMILES)
    for row in results:
        assert row["scenario_ka"] > 0.0, f"scenario_ka not positive for {row['name']}"


def test_batch_canonical_smiles_is_non_empty_string() -> None:
    results, _ = _process_batch(_BATCH_SMILES)
    for row in results:
        assert isinstance(row["canonical_smiles"], str)
        assert len(row["canonical_smiles"]) > 0


# ---------------------------------------------------------------------------
# Download CSV generation
# ---------------------------------------------------------------------------


def test_batch_results_csv_downloadable() -> None:
    results, _ = _process_batch(_BATCH_SMILES)
    df = pd.DataFrame(results)
    csv_text = df.to_csv(index=False)
    assert "name" in csv_text
    assert "predicted_class" in csv_text
    assert "scenario_f" in csv_text
    assert len(csv_text.strip().splitlines()) == 6  # header + 5 rows


def test_batch_failures_csv_downloadable() -> None:
    _, failures = _process_batch(_INVALID_SMILES)
    df = pd.DataFrame(failures)
    csv_text = df.to_csv(index=False)
    assert "name" in csv_text
    assert "error" in csv_text


def test_batch_50_compound_does_not_crash() -> None:
    """50-compound batch must complete without raising."""
    smiles_50 = (
        [("Aspirin", "CC(=O)Oc1ccccc1C(=O)O", "Test")] * 10
        + [("Caffeine", "Cn1cnc2c1c(=O)n(C)c(=O)n2C", "Test")] * 10
        + [("Ibuprofen", "CC(C)Cc1ccc(C(C)C(=O)O)cc1", "Test")] * 10
        + [("Metformin", "CN(C)C(=N)N=C(N)N", "Test")] * 10
        + [("Warfarin", "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O", "Test")] * 10
    )
    results, failures = _process_batch(smiles_50)
    assert len(results) + len(failures) == 50


# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------


def test_batch_summary_high_low_counts_sum_to_valid() -> None:
    results, _ = _process_batch(_BATCH_SMILES)
    df = pd.DataFrame(results)
    high = int((df["predicted_class"].str.contains("high", case=False)).sum())
    low = int((df["predicted_class"].str.contains("low", case=False)).sum())
    assert high + low == len(results)


def test_batch_top_ranked_most_favorable_has_highest_probability() -> None:
    results, _ = _process_batch(_BATCH_SMILES)
    df = pd.DataFrame(results)
    top = df.nlargest(1, "probability")
    all_probs = df["probability"].tolist()
    assert top["probability"].iloc[0] == max(all_probs)
