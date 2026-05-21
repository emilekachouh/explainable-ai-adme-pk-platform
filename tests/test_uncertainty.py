import pytest

from adme_predictor.uncertainty import (
    binary_entropy,
    confidence_from_probability,
    ensemble_prediction_summary,
)


def test_confidence_score_validity_and_category():
    result = confidence_from_probability(0.9)

    assert result["confidence_score"] == pytest.approx(0.9)
    assert result["confidence_category"] == "High confidence"
    assert 0 <= result["prediction_entropy"] <= 1


def test_confidence_rejects_invalid_probability():
    with pytest.raises(ValueError):
        confidence_from_probability(1.2)


def test_binary_entropy_is_highest_near_half():
    assert binary_entropy(0.5) > binary_entropy(0.95)


def test_ensemble_prediction_summary():
    summary = ensemble_prediction_summary([0.2, 0.4, 0.6])

    assert summary["mean_probability"] == pytest.approx(0.4)
    assert summary["probability_std"] >= 0
