import pytest

from adme_predictor.features import (
    DESCRIPTOR_KEYS,
    LIPINSKI_FLAG_KEYS,
    build_feature_vector,
    calculate_descriptors,
    calculate_lipinski_flags,
    canonicalize_smiles,
    generate_morgan_fingerprint,
    mol_from_smiles,
    validate_smiles,
)


VALID_MOLECULES = {
    "aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "caffeine": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "ethanol": "CCO",
}


@pytest.mark.parametrize("smiles", VALID_MOLECULES.values())
def test_validate_smiles_accepts_valid_molecules(smiles):
    assert validate_smiles(smiles) is True


@pytest.mark.parametrize("smiles", VALID_MOLECULES.values())
def test_mol_from_smiles_returns_rdkit_molecule(smiles):
    assert mol_from_smiles(smiles).GetNumAtoms() > 0


@pytest.mark.parametrize("smiles", VALID_MOLECULES.values())
def test_canonical_smiles_is_non_empty(smiles):
    assert canonicalize_smiles(smiles)


@pytest.mark.parametrize("smiles", VALID_MOLECULES.values())
def test_descriptor_dictionary_has_expected_keys(smiles):
    descriptors = calculate_descriptors(smiles)

    assert set(DESCRIPTOR_KEYS).issubset(descriptors)
    assert all(isinstance(value, (float, int)) for value in descriptors.values())


@pytest.mark.parametrize("smiles", VALID_MOLECULES.values())
def test_morgan_fingerprint_length_is_2048(smiles):
    fingerprint = generate_morgan_fingerprint(smiles)

    assert len(fingerprint) == 2048
    assert set(fingerprint).issubset({0, 1})


@pytest.mark.parametrize("smiles", VALID_MOLECULES.values())
def test_lipinski_flags_return_expected_keys(smiles):
    descriptors = calculate_descriptors(smiles)
    flags = calculate_lipinski_flags(descriptors)

    assert set(LIPINSKI_FLAG_KEYS).issubset(flags)
    assert isinstance(flags["lipinski_violations"], int)


@pytest.mark.parametrize("smiles", VALID_MOLECULES.values())
def test_build_feature_vector_combines_descriptors_and_flags(smiles):
    feature_vector = build_feature_vector(smiles)

    assert set(DESCRIPTOR_KEYS).issubset(feature_vector)
    assert set(LIPINSKI_FLAG_KEYS).issubset(feature_vector)


@pytest.mark.parametrize("smiles", ["", "   ", None])
def test_empty_smiles_raise_value_error(smiles):
    with pytest.raises(ValueError):
        validate_smiles(smiles)


@pytest.mark.parametrize("smiles", ["not_a_smiles", "C1CC", "XYZ"])
def test_invalid_smiles_raise_value_error(smiles):
    with pytest.raises(ValueError):
        validate_smiles(smiles)
