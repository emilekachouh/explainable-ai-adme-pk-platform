from adme_predictor.demo_model import (
    descriptor_fallback_prediction,
    predict_permeability_class_resilient,
)


def test_descriptor_fallback_prediction_returns_usable_output():
    prediction = descriptor_fallback_prediction("CC(=O)Oc1ccccc1C(=O)O")

    assert prediction["predicted_label"] in {
        "high permeability class",
        "low permeability class",
    }
    assert 0.0 <= prediction["high_permeability_probability"] <= 1.0
    assert prediction["prediction_source"] == "descriptor fallback"


def test_resilient_prediction_uses_fallback_when_training_unavailable(monkeypatch):
    monkeypatch.setattr("adme_predictor.demo_model.ensure_model_artifacts", lambda auto_train=True: "fallback")

    prediction = predict_permeability_class_resilient("CN(C)C(=N)N=C(N)N")

    assert prediction["prediction_source"] == "descriptor fallback"
