import pytest

from adme_predictor.applicability import (
    AD_WARNING,
    assess_applicability_domain,
    nearest_neighbor_similarity,
    tanimoto_similarity,
)


def test_tanimoto_similarity_bounds():
    similarity = tanimoto_similarity([1, 0, 1], [1, 1, 0])

    assert 0 <= similarity <= 1


def test_nearest_neighbor_similarity_identifies_identical_molecule():
    result = nearest_neighbor_similarity("CCO", ["CCO", "c1ccccc1"], n_bits=128)

    assert result["nearest_neighbor_smiles"] == "CCO"
    assert result["nearest_neighbor_similarity"] == pytest.approx(1.0)


def test_applicability_domain_flags_dissimilar_query():
    result = assess_applicability_domain(
        "CCCCCCCCCCCCCCCC",
        training_smiles=["c1ccccc1", "c1ccncc1"],
        in_domain_threshold=0.8,
        borderline_threshold=0.6,
    )

    assert result["outside_applicability_domain"] is True
    assert result["applicability_warning"] == AD_WARNING
