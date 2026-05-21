"""RDKit-based molecular feature utilities for ADME/PBPK workflows."""

from __future__ import annotations

from typing import Any

from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdFingerprintGenerator, rdMolDescriptors


DESCRIPTOR_KEYS = (
    "molecular_weight",
    "logp",
    "tpsa",
    "hbd",
    "hba",
    "rotatable_bonds",
    "ring_count",
    "aromatic_ring_count",
    "formal_charge",
    "fraction_csp3",
    "heavy_atom_count",
    "heteroatom_count",
    "molar_refractivity",
)

LIPINSKI_FLAG_KEYS = (
    "lipinski_violations",
    "high_mw_flag",
    "high_tpsa_flag",
    "high_logp_flag",
    "high_hbd_flag",
    "high_hba_flag",
    "high_rotatable_bonds_flag",
)


def _clean_smiles(smiles: str) -> str:
    if smiles is None:
        raise ValueError("SMILES input cannot be None.")

    cleaned = smiles.strip()
    if not cleaned:
        raise ValueError("SMILES input cannot be empty.")

    return cleaned


def mol_from_smiles(smiles: str) -> Chem.Mol:
    """Convert a SMILES string to an RDKit molecule or raise ValueError."""
    cleaned = _clean_smiles(smiles)
    mol = Chem.MolFromSmiles(cleaned)

    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")

    return mol


def validate_smiles(smiles: str) -> bool:
    """Return True for valid SMILES and raise ValueError for invalid input."""
    mol_from_smiles(smiles)
    return True


def canonicalize_smiles(smiles: str) -> str:
    """Return the canonical RDKit SMILES representation."""
    mol = mol_from_smiles(smiles)
    canonical = Chem.MolToSmiles(mol, canonical=True)

    if not canonical:
        raise ValueError(f"Could not canonicalize SMILES string: {smiles}")

    return str(canonical)


def _heteroatom_count(mol: Chem.Mol) -> int:
    return int(sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() not in (1, 6)))


def calculate_descriptors(smiles: str) -> dict[str, float | int]:
    """Calculate a compact descriptor set for a valid molecule."""
    mol = mol_from_smiles(smiles)

    return {
        "molecular_weight": float(Descriptors.MolWt(mol)),
        "logp": float(Crippen.MolLogP(mol)),
        "tpsa": float(rdMolDescriptors.CalcTPSA(mol)),
        "hbd": int(Lipinski.NumHDonors(mol)),
        "hba": int(Lipinski.NumHAcceptors(mol)),
        "rotatable_bonds": int(Lipinski.NumRotatableBonds(mol)),
        "ring_count": int(rdMolDescriptors.CalcNumRings(mol)),
        "aromatic_ring_count": int(rdMolDescriptors.CalcNumAromaticRings(mol)),
        "formal_charge": int(Chem.GetFormalCharge(mol)),
        "fraction_csp3": float(rdMolDescriptors.CalcFractionCSP3(mol)),
        "heavy_atom_count": int(mol.GetNumHeavyAtoms()),
        "heteroatom_count": _heteroatom_count(mol),
        "molar_refractivity": float(Crippen.MolMR(mol)),
    }


def calculate_lipinski_flags(descriptors: dict[str, Any]) -> dict[str, bool | int]:
    """Calculate simple Lipinski and ADME-oriented screening flags."""
    required = set(DESCRIPTOR_KEYS)
    missing = sorted(required.difference(descriptors))
    if missing:
        raise ValueError(f"Descriptor dictionary is missing keys: {', '.join(missing)}")

    high_mw = float(descriptors["molecular_weight"]) > 500.0
    high_logp = float(descriptors["logp"]) > 5.0
    high_hbd = int(descriptors["hbd"]) > 5
    high_hba = int(descriptors["hba"]) > 10

    return {
        "lipinski_violations": int(sum((high_mw, high_logp, high_hbd, high_hba))),
        "high_mw_flag": bool(high_mw),
        "high_tpsa_flag": bool(float(descriptors["tpsa"]) > 140.0),
        "high_logp_flag": bool(high_logp),
        "high_hbd_flag": bool(high_hbd),
        "high_hba_flag": bool(high_hba),
        "high_rotatable_bonds_flag": bool(int(descriptors["rotatable_bonds"]) > 10),
    }


def generate_morgan_fingerprint(
    smiles: str,
    radius: int = 2,
    n_bits: int = 2048,
) -> list[int]:
    """Generate a binary Morgan fingerprint as a plain Python list."""
    if radius < 0:
        raise ValueError("Morgan fingerprint radius must be non-negative.")
    if n_bits <= 0:
        raise ValueError("Morgan fingerprint bit length must be positive.")

    mol = mol_from_smiles(smiles)
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    fingerprint = generator.GetFingerprint(mol)

    return [int(bit) for bit in fingerprint.ToBitString()]


def build_feature_vector(smiles: str) -> dict[str, float | int | bool]:
    """Combine molecular descriptors and rule flags for downstream use."""
    descriptors = calculate_descriptors(smiles)
    flags = calculate_lipinski_flags(descriptors)

    return {**descriptors, **flags}
