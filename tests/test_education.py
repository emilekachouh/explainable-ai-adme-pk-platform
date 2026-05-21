import pandas as pd

from adme_predictor.education import (
    PK_EQUATIONS_TEXT,
    build_downloadable_report,
    comparison_interpretations,
    pk_impact_table,
)


def test_downloadable_report_includes_prediction_auc_ratio_and_clf_explanation():
    pk_table = pk_impact_table(0.8)
    report = build_downloadable_report(
        molecule_name="Aspirin",
        category="Analgesics/NSAIDs",
        smiles="CC(=O)Oc1ccccc1C(=O)O",
        canonical_smiles="CC(=O)Oc1ccccc1C(=O)O",
        descriptors={"molecular_weight": 180.16, "logp": 1.2, "tpsa": 63.6},
        prediction={"predicted_label": "high permeability class", "high_permeability_probability": 0.9},
        confidence={"confidence_category": "High confidence", "prediction_entropy": 0.4},
        applicability={"applicability_category": "In domain", "nearest_neighbor_similarity": 0.7},
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
