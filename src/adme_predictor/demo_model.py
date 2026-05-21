"""Deployment-safe prediction helpers for the Streamlit demo."""

from __future__ import annotations

import math

from adme_predictor.features import calculate_descriptors
from adme_predictor import modeling
from adme_predictor.uncertainty import confidence_from_probability


def model_artifacts_available() -> bool:
    """Return True when the lightweight classifier artifacts are available."""
    return modeling.CLASSIFIER_PATH.exists() and modeling.FEATURE_COLUMNS_PATH.exists()


def ensure_model_artifacts(auto_train: bool = True) -> str:
    """Ensure classifier artifacts exist, optionally training them on first run."""
    if model_artifacts_available():
        return "loaded"

    if not auto_train:
        return "missing"

    try:
        modeling.train_baseline_pipeline(force_data_refresh=False)
    except Exception:
        return "fallback"

    return "loaded" if model_artifacts_available() else "fallback"


def descriptor_fallback_prediction(smiles: str) -> dict[str, float | int | str]:
    """Return an educational descriptor-based fallback when model loading fails."""
    descriptors = calculate_descriptors(smiles)
    mw = float(descriptors["molecular_weight"])
    logp = float(descriptors["logp"])
    tpsa = float(descriptors["tpsa"])
    hbd = float(descriptors["hbd"])
    hba = float(descriptors["hba"])
    rotatable = float(descriptors["rotatable_bonds"])

    score = (
        0.55
        + 0.12 * (logp - 2.0)
        - 0.006 * max(tpsa - 60.0, 0.0)
        - 0.08 * max(hbd - 1.0, 0.0)
        - 0.025 * max(hba - 4.0, 0.0)
        - 0.002 * max(mw - 450.0, 0.0)
        - 0.025 * max(rotatable - 8.0, 0.0)
    )
    probability = 1.0 / (1.0 + math.exp(-4.0 * (score - 0.5)))
    probability = min(max(probability, 0.03), 0.97)
    predicted_class = int(probability >= 0.5)
    label = "high permeability class" if predicted_class == 1 else "low permeability class"

    return {
        "predicted_class": predicted_class,
        "predicted_label": label,
        "high_permeability_probability": float(probability),
        "prediction_source": "descriptor fallback",
        "prediction_note": (
            "Model artifacts could not be loaded, so this is a transparent descriptor-based "
            "teaching estimate rather than the trained Caco-2 classifier."
        ),
    }


def predict_permeability_class_resilient(
    smiles: str,
    auto_train: bool = True,
) -> dict[str, float | int | str]:
    """Predict permeability using saved/trained artifacts with a graceful fallback."""
    status = ensure_model_artifacts(auto_train=auto_train)
    if status == "loaded":
        try:
            prediction = modeling.predict_permeability_class(smiles)
            prediction["prediction_source"] = "trained Caco-2 classifier"
            prediction["prediction_note"] = "Prediction uses the saved baseline classifier artifacts."
            return prediction
        except Exception:
            pass

    return descriptor_fallback_prediction(smiles)


def prediction_confidence(prediction: dict[str, object]) -> dict[str, float | str]:
    """Calculate confidence metadata for a prediction dictionary."""
    probability = float(prediction["high_permeability_probability"])
    confidence = confidence_from_probability(probability)
    confidence["prediction_source"] = str(prediction.get("prediction_source", "unknown"))
    return confidence
