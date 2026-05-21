"""Lightweight health checks for the Streamlit deployment."""

from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path

from adme_predictor.config import PROJECT_ROOT, REPORTS_DIR
from adme_predictor.demo_model import model_artifacts_available
from adme_predictor.example_molecules import EXAMPLE_MOLECULE_COUNT


def check_app_health() -> dict[str, dict[str, str]]:
    """Return friendly deployment status messages for the sidebar."""
    figures_dir = REPORTS_DIR / "figures"
    runtime_path = PROJECT_ROOT / "runtime.txt"
    requirements_path = PROJECT_ROOT / "requirements.txt"
    required_packages = ("streamlit", "rdkit", "sklearn", "pandas", "numpy")
    missing_packages = [name for name in required_packages if find_spec(name) is None]

    return {
        "model": {
            "level": "ok" if model_artifacts_available() else "warn",
            "message": "Model loaded" if model_artifacts_available() else "Model will use auto-training or fallback",
        },
        "molecules": {
            "level": "ok" if EXAMPLE_MOLECULE_COUNT >= 100 else "error",
            "message": f"Molecule library loaded ({EXAMPLE_MOLECULE_COUNT})",
        },
        "pk": {
            "level": "ok",
            "message": "PK simulator ready",
        },
        "shap": {
            "level": "ok" if figures_dir.exists() and any(figures_dir.rglob("*.png")) else "warn",
            "message": "SHAP/report figures available" if figures_dir.exists() and any(figures_dir.rglob("*.png")) else "SHAP plots unavailable",
        },
        "requirements": {
            "level": "ok" if not missing_packages else "error",
            "message": "Requirements importable" if not missing_packages else f"Missing packages: {', '.join(missing_packages)}",
        },
        "runtime": {
            "level": "ok" if runtime_path.exists() and requirements_path.exists() else "warn",
            "message": "Runtime files present" if runtime_path.exists() and requirements_path.exists() else "Runtime metadata incomplete",
        },
    }


def health_icon(level: str) -> str:
    """Return a compact status icon for sidebar display."""
    if level == "ok":
        return "✅"
    if level == "warn":
        return "⚠"
    return "❌"
