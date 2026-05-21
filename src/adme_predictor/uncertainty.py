"""Prediction confidence and uncertainty utilities."""

from __future__ import annotations

import math

import numpy as np


def binary_entropy(probability: float) -> float:
    """Return normalized binary entropy for a class probability."""
    p = min(max(float(probability), 1e-12), 1.0 - 1e-12)
    entropy = -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))
    return float(entropy)


def confidence_from_probability(high_class_probability: float) -> dict[str, float | str]:
    """Convert a binary probability into confidence score, entropy, and category."""
    probability = float(high_class_probability)
    if not 0.0 <= probability <= 1.0:
        raise ValueError("Probability must be between 0 and 1.")

    confidence = max(probability, 1.0 - probability)
    entropy = binary_entropy(probability)

    if confidence >= 0.80:
        category = "High confidence"
    elif confidence >= 0.65:
        category = "Medium confidence"
    else:
        category = "Low confidence"

    return {
        "confidence_score": float(confidence),
        "prediction_entropy": float(entropy),
        "confidence_category": category,
    }


def ensemble_prediction_summary(probabilities: list[float] | np.ndarray) -> dict[str, float]:
    """Summarize variation across multiple probability estimates."""
    values = np.asarray(probabilities, dtype=float)
    if values.size == 0:
        raise ValueError("At least one probability is required.")
    if np.any((values < 0.0) | (values > 1.0)):
        raise ValueError("All probabilities must be between 0 and 1.")

    return {
        "mean_probability": float(values.mean()),
        "probability_std": float(values.std(ddof=0)),
        "min_probability": float(values.min()),
        "max_probability": float(values.max()),
    }
