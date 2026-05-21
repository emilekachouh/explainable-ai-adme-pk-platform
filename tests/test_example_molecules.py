from adme_predictor.example_molecules import EXAMPLE_CATEGORIES, EXAMPLE_MOLECULES
from adme_predictor.features import canonicalize_smiles


def test_example_library_has_more_than_100_valid_canonical_smiles():
    assert len(EXAMPLE_MOLECULES) > 100

    for entry in EXAMPLE_MOLECULES:
        assert entry["category"] in EXAMPLE_CATEGORIES
        assert entry["teaching_note"]
        assert entry["smiles"] == canonicalize_smiles(entry["smiles"])


def test_example_library_contains_required_demo_categories():
    assert "Highly polar/low permeability examples" in EXAMPLE_CATEGORIES
    assert "Lipophilic/high permeability examples" in EXAMPLE_CATEGORIES
