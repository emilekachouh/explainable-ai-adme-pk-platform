from adme_predictor.reporting import build_prediction_report, render_molecule_png


def test_molecule_rendering_returns_png_bytes():
    image = render_molecule_png("CCO")

    assert image.startswith(b"\x89PNG")
    assert len(image) > 100


def test_downloadable_report_generation_contains_scientific_sections():
    report = build_prediction_report(
        "CCO",
        {"predicted_label": "high permeability class", "high_permeability_probability": 0.8},
        {"confidence_score": 0.8, "confidence_category": "High confidence", "prediction_entropy": 0.72},
        {
            "applicability_category": "In domain",
            "nearest_neighbor_similarity": 1.0,
            "applicability_warning": "",
        },
    )

    assert "Permeability Prediction" in report
    assert "Applicability Domain" in report
    assert "not a clinical" in report
