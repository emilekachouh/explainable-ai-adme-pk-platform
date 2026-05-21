import pandas as pd
import pytest

from adme_predictor.scaffold import get_bemis_murcko_scaffold, scaffold_split


VALID_MOLECULES = [
    "CC(=O)OC1=CC=CC=C1C(=O)O",
    "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "CCO",
]


@pytest.mark.parametrize("smiles", VALID_MOLECULES)
def test_scaffold_generation_works_for_valid_molecules(smiles):
    scaffold = get_bemis_murcko_scaffold(smiles)

    assert isinstance(scaffold, str)


def test_scaffold_generation_rejects_invalid_smiles():
    with pytest.raises(ValueError):
        get_bemis_murcko_scaffold("not_a_smiles")


def test_scaffold_split_returns_non_empty_sets_without_scaffold_overlap():
    df = pd.DataFrame(
        {
            "canonical_smiles": [
                "c1ccccc1",
                "Cc1ccccc1",
                "c1ccncc1",
                "Cc1ccncc1",
                "C1CCCCC1",
                "CC1CCCCC1",
                "CCO",
                "CCCO",
            ],
            "permeability_class": [0, 0, 1, 1, 0, 0, 1, 1],
            "caco2_log_papp": [-5.8, -5.7, -4.8, -4.7, -5.5, -5.4, -4.2, -4.1],
        }
    )

    train_df, test_df = scaffold_split(df, "canonical_smiles", test_size=0.3, random_state=42)
    train_scaffolds = set(train_df["canonical_smiles"].map(get_bemis_murcko_scaffold))
    test_scaffolds = set(test_df["canonical_smiles"].map(get_bemis_murcko_scaffold))

    assert len(train_df) > 0
    assert len(test_df) > 0
    assert train_scaffolds.isdisjoint(test_scaffolds)
