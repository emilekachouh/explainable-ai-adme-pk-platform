"""Applicability-domain analysis based on nearest-neighbor chemistry."""

from __future__ import annotations

import numpy as np

from adme_predictor.data import load_caco2_wang_processed
from adme_predictor.features import generate_morgan_fingerprint


AD_WARNING = (
    "This molecule is chemically dissimilar to most training compounds. "
    "Prediction reliability may be reduced."
)


def tanimoto_similarity(fp_a: list[int], fp_b: list[int]) -> float:
    """Calculate Tanimoto similarity between two binary fingerprints."""
    a = np.asarray(fp_a, dtype=bool)
    b = np.asarray(fp_b, dtype=bool)
    if a.shape != b.shape:
        raise ValueError("Fingerprints must have the same length.")

    intersection = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    if union == 0:
        return 0.0
    return float(intersection / union)


def nearest_neighbor_similarity(
    smiles: str,
    training_smiles: list[str],
    radius: int = 2,
    n_bits: int = 2048,
) -> dict[str, float | str]:
    """Find the nearest training molecule by Morgan fingerprint Tanimoto similarity."""
    if not training_smiles:
        raise ValueError("training_smiles cannot be empty.")

    query_fp = generate_morgan_fingerprint(smiles, radius=radius, n_bits=n_bits)
    best_similarity = -1.0
    nearest_smiles = ""

    for candidate in training_smiles:
        candidate_fp = generate_morgan_fingerprint(candidate, radius=radius, n_bits=n_bits)
        similarity = tanimoto_similarity(query_fp, candidate_fp)
        if similarity > best_similarity:
            best_similarity = similarity
            nearest_smiles = candidate

    return {
        "nearest_neighbor_smiles": nearest_smiles,
        "nearest_neighbor_similarity": float(best_similarity),
    }


def assess_applicability_domain(
    smiles: str,
    training_smiles: list[str] | None = None,
    in_domain_threshold: float = 0.45,
    borderline_threshold: float = 0.30,
) -> dict[str, float | str | bool]:
    """Assess whether a molecule is close to the training chemistry."""
    if training_smiles is None:
        data = load_caco2_wang_processed()
        training_smiles = data["canonical_smiles"].tolist()

    neighbor = nearest_neighbor_similarity(smiles, training_smiles)
    similarity = float(neighbor["nearest_neighbor_similarity"])

    if similarity >= in_domain_threshold:
        category = "In domain"
        warning = ""
        is_outside = False
    elif similarity >= borderline_threshold:
        category = "Borderline domain"
        warning = "This molecule is moderately similar to training chemistry; interpret with caution."
        is_outside = False
    else:
        category = "Outside domain"
        warning = AD_WARNING
        is_outside = True

    return {
        **neighbor,
        "applicability_category": category,
        "outside_applicability_domain": is_outside,
        "applicability_warning": warning,
    }
