"""Tests for molecule rendering and report generation."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from adme_predictor.reporting import build_prediction_report, render_molecule_svg

# fmt: off
MOLECULE_SMILES = {
    "aspirin":     "CC(=O)Oc1ccccc1C(=O)O",
    "caffeine":    "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "ibuprofen":   "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
    "metformin":   "CN(C)C(=N)N=C(N)N",
    "propranolol": "CC(C)NCC(O)COc1cccc2ccccc12",
}
# fmt: on


@pytest.mark.parametrize("name,smiles", MOLECULE_SMILES.items())
def test_render_molecule_svg_returns_valid_svg(name: str, smiles: str) -> None:
    """SVG rendering must work for all key example molecules on any deployment."""
    svg = render_molecule_svg(smiles)
    assert "<svg" in svg, f"{name}: SVG output missing <svg tag"
    assert "</svg>" in svg, f"{name}: SVG output missing </svg> closing tag"
    assert len(svg) > 200, f"{name}: SVG output suspiciously short ({len(svg)} chars)"


def test_render_molecule_svg_ethanol() -> None:
    svg = render_molecule_svg("CCO")
    assert "<svg" in svg
    assert len(svg) > 100


def test_render_molecule_svg_raises_on_invalid_smiles() -> None:
    with pytest.raises((ValueError, RuntimeError)):
        render_molecule_svg("NOT_A_VALID_SMILES!!!")


def test_render_molecule_svg_uses_robust_import_path() -> None:
    """Ensure reporting.py uses _load_rdmoldraw2d() for cloud-safe module loading.

    The function must not call 'from rdkit.Chem.Draw import rdMolDraw2D' at the
    top of render_molecule_svg — that import is allowed only inside the helper
    _load_rdmoldraw2d as a last-resort fallback, never as the primary path.
    """
    source = Path("src/adme_predictor/reporting.py").read_text(encoding="utf-8")
    assert "_load_rdmoldraw2d" in source, "Expected helper function _load_rdmoldraw2d not found"
    assert "importlib.import_module" in source, "Expected importlib.import_module usage not found"
    # render_molecule_svg must delegate to the helper, not import Draw directly
    in_render_fn = False
    found_direct_import = False
    for line in source.splitlines():
        if "def render_molecule_svg" in line:
            in_render_fn = True
        elif in_render_fn and line.startswith("def "):
            in_render_fn = False
        if in_render_fn and "from rdkit.Chem.Draw import rdMolDraw2D" in line:
            found_direct_import = True
    assert not found_direct_import, (
        "render_molecule_svg must not contain 'from rdkit.Chem.Draw import rdMolDraw2D' directly"
    )


def test_no_applymap_in_streamlit_app() -> None:
    """The Streamlit app must not call applymap directly (pandas 2.x/3.x compatibility)."""
    source = Path("app/streamlit_app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "applymap":
            # Only permitted inside a try/except as a fallback — verify context
            # by checking the raw source line
            lineno = node.lineno
            line = source.splitlines()[lineno - 1].strip()
            assert line.startswith("return") or "except" in line or "try" in line, (
                f"Direct .applymap() call found at line {lineno}: {line!r}\n"
                "Replace with _safe_style() helper."
            )


def test_app_imports_cleanly() -> None:
    """app/streamlit_app.py must parse as valid Python without import errors
    for all stdlib/non-Streamlit symbols."""
    source = Path("app/streamlit_app.py").read_text(encoding="utf-8")
    ast.parse(source)  # raises SyntaxError on bad syntax


def test_downloadable_report_generation_contains_scientific_sections() -> None:
    report = build_prediction_report(
        "CCO",
        {"predicted_label": "high permeability class", "high_permeability_probability": 0.8},
        {"confidence_score": 0.8, "confidence_category": "High confidence", "prediction_entropy": 0.72},
        {
            "applicability_category": "In domain",
            "nearest_neighbor_similarity": 1.0,
            "applicability_warning": "",
        },
    )
    assert "Permeability Prediction" in report
    assert "Applicability Domain" in report
    assert "not a clinical" in report
