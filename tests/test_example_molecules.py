from adme_predictor.example_molecules import EXAMPLE_CATEGORIES, EXAMPLE_MOLECULES
from adme_predictor.features import canonicalize_smiles


def test_example_library_has_more_than_100_valid_canonical_smiles():
    assert len(EXAMPLE_MOLECULES) > 100

    for entry in EXAMPLE_MOLECULES:
        assert entry["category"] in EXAMPLE_CATEGORIES
        assert entry["teaching_note"]
        assert entry["smiles"] == canonicalize_smiles(entry["smiles"])


def test_example_library_has_at_least_200_molecules():
    assert len(EXAMPLE_MOLECULES) >= 200, (
        f"Expected at least 200 molecules, found {len(EXAMPLE_MOLECULES)}"
    )


def test_example_library_no_duplicate_canonical_smiles():
    from collections import Counter
    smiles_counts = Counter(entry["smiles"] for entry in EXAMPLE_MOLECULES)
    duplicates = {s: n for s, n in smiles_counts.items() if n > 1}
    assert not duplicates, (
        f"Duplicate canonical SMILES found (name check recommended):\n"
        + "\n".join(f"  {s}: {n} times" for s, n in list(duplicates.items())[:5])
    )


def test_example_library_all_teaching_notes_non_empty():
    for entry in EXAMPLE_MOLECULES:
        assert entry["teaching_note"].strip(), (
            f"Empty teaching note for {entry['name']}"
        )


def test_example_library_new_categories_present():
    assert "Antihistamines" in EXAMPLE_CATEGORIES
    assert "Diabetes/metabolic drugs" in EXAMPLE_CATEGORIES
    assert "Antiepileptics" in EXAMPLE_CATEGORIES
    assert "Respiratory drugs" in EXAMPLE_CATEGORIES
    assert "Transporter-relevant examples" in EXAMPLE_CATEGORIES


def test_example_library_contains_required_demo_categories():
    assert "Highly polar/low permeability examples" in EXAMPLE_CATEGORIES
    assert "Lipophilic/high permeability examples" in EXAMPLE_CATEGORIES
