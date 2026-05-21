"""Data loading and preprocessing utilities for public ADME datasets."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from adme_predictor.config import DATA_DIR, REPORTS_DIR
from adme_predictor.features import canonicalize_smiles


RANDOM_SEED = 42
CACO2_WANG_URL = (
    "https://huggingface.co/datasets/scikit-fingerprints/TDC_caco2_wang/"
    "resolve/main/tdc_caco2_wang.csv"
)
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACO2_RAW_PATH = RAW_DATA_DIR / "tdc_caco2_wang.csv"
CACO2_PROCESSED_PATH = PROCESSED_DATA_DIR / "tdc_caco2_wang_processed.csv"
DATASET_METADATA_PATH = REPORTS_DIR / "caco2_wang_dataset_metadata.csv"


@dataclass(frozen=True)
class DatasetMetadata:
    """Minimal scientific metadata required for dataset provenance."""

    name: str
    source: str
    endpoint: str
    units: str
    sample_size: int
    license_usage_note: str
    preprocessing_steps: str
    limitations: str


def get_caco2_wang_metadata(sample_size: int = 910) -> DatasetMetadata:
    """Return provenance details for the selected public Caco-2 dataset."""
    return DatasetMetadata(
        name="TDC Caco2_Wang",
        source=(
            "Therapeutics Data Commons Caco-2 Wang benchmark mirrored at "
            "Hugging Face scikit-fingerprints/TDC_caco2_wang"
        ),
        endpoint="Caco-2 cell effective permeability from Wang et al.",
        units="log10 apparent permeability, log(Papp)",
        sample_size=int(sample_size),
        license_usage_note=(
            "Hugging Face mirror lists license as unknown; use as a public benchmark "
            "with citation to TDC and Wang et al."
        ),
        preprocessing_steps=(
            "Load SMILES and Y endpoint; drop missing values; reject invalid SMILES; "
            "canonicalize with RDKit; remove duplicate canonical SMILES by averaging "
            "replicate endpoint values; add median-threshold permeability class."
        ),
        limitations=(
            "In vitro Caco-2 assay data do not directly establish human clinical "
            "permeability. Median-threshold classification is a modeling convenience, "
            "not a clinical or regulatory cutoff."
        ),
    )


def download_caco2_wang(force: bool = False) -> Path:
    """Download the public Caco2_Wang CSV if needed and return its local path."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if CACO2_RAW_PATH.exists() and not force:
        return CACO2_RAW_PATH

    df = pd.read_csv(CACO2_WANG_URL)
    df.to_csv(CACO2_RAW_PATH, index=False)
    return CACO2_RAW_PATH


def load_caco2_wang_raw(force_download: bool = False) -> pd.DataFrame:
    """Load the raw public Caco2_Wang dataset."""
    path = download_caco2_wang(force=force_download)
    raw = pd.read_csv(path)

    expected = {"SMILES", "Y"}
    missing = expected.difference(raw.columns)
    if missing:
        raise ValueError(f"Caco2_Wang dataset missing required columns: {sorted(missing)}")

    return raw.loc[:, ["SMILES", "Y"]].rename(
        columns={"SMILES": "smiles", "Y": "caco2_log_papp"}
    )


def preprocess_caco2_wang(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate, canonicalize, deduplicate, and label the Caco2_Wang dataset."""
    required = {"smiles", "caco2_log_papp"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"Raw dataframe missing required columns: {sorted(missing)}")

    df = raw.copy()
    df["smiles"] = df["smiles"].astype("string")
    df["caco2_log_papp"] = pd.to_numeric(df["caco2_log_papp"], errors="coerce")
    df = df.dropna(subset=["smiles", "caco2_log_papp"])

    valid_rows = []
    for row in df.itertuples(index=False):
        try:
            valid_rows.append(
                {
                    "smiles": str(row.smiles),
                    "canonical_smiles": canonicalize_smiles(str(row.smiles)),
                    "caco2_log_papp": float(row.caco2_log_papp),
                }
            )
        except ValueError:
            continue

    clean = pd.DataFrame(valid_rows)
    if clean.empty:
        raise ValueError("No valid molecules remained after SMILES validation.")

    clean = (
        clean.groupby("canonical_smiles", as_index=False)
        .agg(smiles=("smiles", "first"), caco2_log_papp=("caco2_log_papp", "mean"))
        .sort_values("canonical_smiles")
        .reset_index(drop=True)
    )
    threshold = float(clean["caco2_log_papp"].median())
    clean["permeability_class"] = (clean["caco2_log_papp"] >= threshold).astype(int)
    clean["class_threshold_log_papp"] = threshold

    return clean


def load_caco2_wang_processed(
    force_download: bool = False,
    force_preprocess: bool = False,
) -> pd.DataFrame:
    """Load or create the cleaned Caco2_Wang modeling table."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if CACO2_PROCESSED_PATH.exists() and not force_preprocess and not force_download:
        return pd.read_csv(CACO2_PROCESSED_PATH)

    raw = load_caco2_wang_raw(force_download=force_download)
    processed = preprocess_caco2_wang(raw)
    processed.to_csv(CACO2_PROCESSED_PATH, index=False)

    metadata = get_caco2_wang_metadata(sample_size=len(processed))
    pd.DataFrame([asdict(metadata)]).to_csv(DATASET_METADATA_PATH, index=False)
    return processed
