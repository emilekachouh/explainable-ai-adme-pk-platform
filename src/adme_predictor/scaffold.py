"""Bemis-Murcko scaffold utilities for stricter chemical validation splits."""

from __future__ import annotations

import random

import pandas as pd
from rdkit.Chem.Scaffolds import MurckoScaffold

from adme_predictor.features import mol_from_smiles


def get_bemis_murcko_scaffold(smiles: str) -> str:
    """Return the canonical Bemis-Murcko scaffold for a valid SMILES string."""
    mol = mol_from_smiles(smiles)
    scaffold = MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False)
    return str(scaffold)


def scaffold_split(
    df: pd.DataFrame,
    smiles_col: str,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a dataframe so each Bemis-Murcko scaffold appears in only one split."""
    if smiles_col not in df.columns:
        raise ValueError(f"Missing SMILES column: {smiles_col}")
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")

    working = df.copy()
    working["_bemis_murcko_scaffold"] = working[smiles_col].map(get_bemis_murcko_scaffold)

    scaffold_groups = [
        group.index.tolist()
        for _, group in working.groupby("_bemis_murcko_scaffold", sort=False)
    ]
    rng = random.Random(random_state)
    rng.shuffle(scaffold_groups)
    scaffold_groups.sort(key=len, reverse=True)

    target_test_count = max(1, round(len(working) * test_size))
    test_indices: list[int] = []
    train_indices: list[int] = []

    for group_indices in scaffold_groups:
        would_improve_test_size = abs(
            target_test_count - (len(test_indices) + len(group_indices))
        ) <= abs(target_test_count - len(test_indices))
        if len(test_indices) < target_test_count and would_improve_test_size:
            test_indices.extend(group_indices)
        else:
            train_indices.extend(group_indices)

    if not train_indices or not test_indices:
        raise ValueError("Scaffold split produced an empty train or test set.")

    train_df = working.loc[train_indices].drop(columns=["_bemis_murcko_scaffold"])
    test_df = working.loc[test_indices].drop(columns=["_bemis_murcko_scaffold"])
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)
