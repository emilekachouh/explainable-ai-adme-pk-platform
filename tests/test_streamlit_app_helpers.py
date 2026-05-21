from app.streamlit_app import _comparison_rows


def test_comparison_rows_include_model_and_descriptor_columns():
    rows = _comparison_rows(
        [
            "Aspirin - Analgesics/NSAIDs",
            "Ibuprofen - Analgesics/NSAIDs",
        ]
    )

    assert len(rows) == 2
    assert {
        "molecular_weight",
        "logp",
        "tpsa",
        "predicted_permeability",
        "confidence",
        "applicability_similarity",
    }.issubset(rows.columns)
