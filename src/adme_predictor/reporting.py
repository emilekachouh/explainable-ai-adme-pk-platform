"""Professional reporting and molecule-rendering utilities."""

from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import RocCurveDisplay

from adme_predictor.config import REPORTS_DIR
from adme_predictor.data import load_caco2_wang_processed
from adme_predictor.features import calculate_descriptors, mol_from_smiles
from adme_predictor.uncertainty import confidence_from_probability


FIGURES_DIR = REPORTS_DIR / "figures"
MODEL_CARD_DOC_PATH = Path("docs") / "model_card.md"


def _load_rdmoldraw2d() -> object:
    """Load the rdMolDraw2D C++ extension via the most direct path available.

    Streamlit Cloud (Linux) ships RDKit from PyPI.  The extension lives at
    rdkit.Chem.Draw.rdMolDraw2D.  We import it via ``importlib.import_module``
    which resolves the submodule directly after the parent packages are loaded,
    avoiding any optional high-level Draw helpers (PIL, Cairo, Qt) that may be
    absent on the cloud runtime.
    """
    import importlib

    # Primary path: direct submodule import (works on all PyPI rdkit builds)
    try:
        return importlib.import_module("rdkit.Chem.Draw.rdMolDraw2D")
    except ImportError:
        pass

    # Fallback: some RDKit installs expose it at rdkit.Chem.rdMolDraw2D
    try:
        return importlib.import_module("rdkit.Chem.rdMolDraw2D")
    except ImportError:
        pass

    # Last resort: go through the Draw package public API
    from rdkit.Chem.Draw import rdMolDraw2D  # noqa: PLC0415
    return rdMolDraw2D


def render_molecule_svg(smiles: str, size: tuple[int, int] = (450, 300)) -> str:
    """Render a SMILES string as an SVG string using RDKit's pure vector drawer.

    The function never imports PIL, Cairo, or any GUI toolkit.  It uses
    ``MolDraw2DSVG`` which is a self-contained C++ SVG renderer and works on
    headless cloud environments (Streamlit Cloud, GitHub Actions, etc.).

    2D coordinates are generated explicitly via ``rdDepictor`` before the
    drawing step so that ``PrepareMolForDrawing`` failure on unusual molecules
    does not silently produce a blank image.
    """
    rdMolDraw2D = _load_rdmoldraw2d()

    mol = mol_from_smiles(smiles)

    # Ensure 2D coordinates exist — try the explicit depictor first
    try:
        from rdkit.Chem import rdDepictor  # noqa: PLC0415
        rdDepictor.Compute2DCoords(mol)
    except Exception:
        try:
            mol = rdMolDraw2D.PrepareMolForDrawing(mol)
        except Exception:
            pass  # draw without explicit 2D coords — RDKit will auto-assign

    width, height = size
    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()
    if not svg or "<svg" not in svg:
        raise RuntimeError(f"Empty SVG produced for SMILES: {smiles}")
    return str(svg)


def svg_to_html_page(svg: str, bg_color: str = "white") -> str:
    """Wrap a raw SVG string in a minimal HTML document for use in st.components.v1.html.

    Without this wrapper, some browser/iframe environments do not render raw SVG
    text correctly when it begins with an XML declaration.  Embedding it in a
    proper HTML page ensures consistent rendering on Streamlit Cloud and locally.
    """
    svg_clean = svg.replace("<?xml version='1.0' encoding='iso-8859-1'?>", "").strip()
    return (
        "<!DOCTYPE html>"
        "<html>"
        "<head>"
        "<style>"
        f"body{{margin:0;padding:0;background:{bg_color};overflow:hidden;}}"
        "svg{display:block;max-width:100%;height:auto;}"
        "</style>"
        "</head>"
        f"<body>{svg_clean}</body>"
        "</html>"
    )


def build_prediction_report(
    smiles: str,
    prediction: dict[str, object],
    confidence: dict[str, object],
    applicability: dict[str, object],
) -> str:
    """Create a downloadable markdown prediction report."""
    descriptors = calculate_descriptors(smiles)
    descriptor_lines = [f"- {key}: {value}" for key, value in descriptors.items()]
    return "\n".join(
        [
            "# AI-PBPK / ADME Predictor Report",
            "",
            "Scientific positioning: explainable AI-assisted ADME screening for early discovery and education. This is not a clinical, regulatory, or validated PBPK prediction report.",
            "",
            f"Input SMILES: `{smiles}`",
            "",
            "## Permeability Prediction",
            "",
            f"- Predicted class: {prediction.get('predicted_label', 'not available')}",
            f"- High-permeability probability: {prediction.get('high_permeability_probability', 'not available')}",
            "",
            "## Confidence",
            "",
            f"- Confidence score: {confidence.get('confidence_score', 'not available')}",
            f"- Confidence category: {confidence.get('confidence_category', 'not available')}",
            f"- Prediction entropy: {confidence.get('prediction_entropy', 'not available')}",
            "",
            "## Applicability Domain",
            "",
            f"- Category: {applicability.get('applicability_category', 'not available')}",
            f"- Nearest-neighbor similarity: {applicability.get('nearest_neighbor_similarity', 'not available')}",
            f"- Warning: {applicability.get('applicability_warning', '') or 'None'}",
            "",
            "## Molecular Descriptors",
            "",
            *descriptor_lines,
            "",
            "## Interpretation",
            "",
            "Descriptor and fingerprint models can highlight permeability-related structural patterns, but they cannot establish human clinical PK behavior. Scaffold split validation and applicability-domain checks should be reviewed before using the prediction for prioritization.",
        ]
    )


def write_model_card() -> Path:
    """Write the project model card used by docs and reviewers."""
    MODEL_CARD_DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_CARD_DOC_PATH.write_text(
        "\n".join(
            [
                "# Model Card: AI-PBPK / ADME Predictor",
                "",
                "## Intended Use",
                "",
                "Explainable AI-assisted early discovery screening for Caco-2 permeability-related risk from molecular structure. The platform is also suitable for educational translational modeling demonstrations.",
                "",
                "## Not Intended For",
                "",
                "- Clinical decision-making",
                "- Regulatory submission",
                "- Human PK or PBPK claims",
                "- Dose selection or therapeutic recommendations",
                "",
                "## Training Dataset",
                "",
                "TDC Caco2_Wang public benchmark with experimentally measured Caco-2 log(Papp). Processed sample size: 906 valid canonicalized molecules.",
                "",
                "## Evaluation Strategy",
                "",
                "The project reports both random train/test split validation and Bemis-Murcko scaffold split validation. Scaffold split is stricter because test molecules have chemically distinct core scaffolds from training molecules.",
                "",
                "## Explainability",
                "",
                "RDKit descriptors, Morgan fingerprints, feature importance, and SHAP analyses are used to interpret global and local model behavior. Interpretations emphasize TPSA, HBD/HBA, molecular weight, logP, flexibility, and fingerprint-defined chemical motifs.",
                "",
                "## Applicability Domain",
                "",
                "Predictions include nearest-neighbor Tanimoto similarity to training molecules. Chemically dissimilar inputs are flagged because reliability may be reduced outside the training chemistry.",
                "",
                "## Limitations",
                "",
                "- Caco-2 data are in vitro permeability measurements and do not validate clinical absorption.",
                "- Median-threshold classification is dataset-specific.",
                "- Experimental noise, assay protocol variation, and chemical domain shift can affect performance.",
                "- Scaffold validation is more credible than random splitting but still not prospective external validation.",
                "",
                "## Appropriate Use Cases",
                "",
                "- Early ADME triage",
                "- Molecule prioritization support",
                "- Computational pharmacology portfolio demonstration",
                "- Educational explanation of descriptors, permeability, and validation design",
            ]
        ),
        encoding="utf-8",
    )
    return MODEL_CARD_DOC_PATH


def generate_publication_figures() -> list[Path]:
    """Generate lightweight publication-style summary figures from saved outputs."""
    from adme_predictor.modeling import (
        CLASSIFIER_PATH,
        FEATURE_COLUMNS_PATH,
        REGRESSOR_PATH,
        build_feature_matrix,
        split_features,
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    data = load_caco2_wang_processed()
    descriptors = pd.DataFrame([calculate_descriptors(s) for s in data["canonical_smiles"]])

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for ax, column in zip(axes.ravel(), ["molecular_weight", "logp", "tpsa", "rotatable_bonds"]):
        ax.hist(descriptors[column], bins=30, edgecolor="black")
        ax.set_title(column)
    fig.suptitle("Descriptor Distributions")
    fig.tight_layout()
    path = FIGURES_DIR / "publication_descriptor_distributions.png"
    fig.savefig(path, dpi=220)
    plt.close(fig)
    paths.append(path)

    comparison_path = REPORTS_DIR / "scaffold_vs_random_metric_comparison.csv"
    if comparison_path.exists():
        comparison = pd.read_csv(comparison_path)
        selected = comparison[
            (comparison["model"].isin(["xgboost", "xgboost_regressor"]))
            & (comparison["metric"].isin(["auroc", "f1", "r2", "mae"]))
        ]
        fig, ax = plt.subplots(figsize=(8, 5))
        labels = selected["model"] + ":" + selected["metric"]
        x = range(len(selected))
        ax.plot(x, selected["random_split"], marker="o", label="Random split")
        ax.plot(x, selected["scaffold_split"], marker="o", label="Scaffold split")
        ax.set_xticks(list(x), labels, rotation=45, ha="right")
        ax.set_title("Random vs Scaffold Split Metrics")
        ax.legend()
        fig.tight_layout()
        path = FIGURES_DIR / "publication_scaffold_split_comparison.png"
        fig.savefig(path, dpi=220)
        plt.close(fig)
        paths.append(path)

    metrics_path = REPORTS_DIR / "baseline_metrics.csv"
    if metrics_path.exists():
        metrics = pd.read_csv(metrics_path)
        class_metrics = metrics[metrics["task"] == "classification"].dropna(axis=1, how="all")
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(class_metrics["model"], class_metrics["auroc"])
        ax.set_ylim(0, 1)
        ax.set_ylabel("AUROC")
        ax.set_title("Baseline Classification AUROC")
        fig.tight_layout()
        path = FIGURES_DIR / "publication_roc_summary.png"
        fig.savefig(path, dpi=220)
        plt.close(fig)
        paths.append(path)

    if CLASSIFIER_PATH.exists() and REGRESSOR_PATH.exists() and FEATURE_COLUMNS_PATH.exists():
        classifier = joblib.load(CLASSIFIER_PATH)
        regressor = joblib.load(REGRESSOR_PATH)
        if hasattr(classifier, "n_jobs"):
            classifier.n_jobs = 1
        if hasattr(regressor, "n_jobs"):
            regressor.n_jobs = 1
        feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
        X, _ = build_feature_matrix(data)
        X = X.loc[:, feature_columns]
        y_class = data["permeability_class"].astype(int)
        y_regression = data["caco2_log_papp"].astype(float)
        _, X_test, _, y_class_test, _, y_reg_test = split_features(X, y_class, y_regression)

        probabilities = classifier.predict_proba(X_test)[:, 1]
        fig, ax = plt.subplots(figsize=(5, 5))
        RocCurveDisplay.from_predictions(y_class_test, probabilities, ax=ax)
        ax.set_title("Random Split ROC Curve")
        fig.tight_layout()
        path = FIGURES_DIR / "publication_roc_curve.png"
        fig.savefig(path, dpi=220)
        plt.close(fig)
        paths.append(path)

        reg_predictions = regressor.predict(X_test)
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.scatter(y_reg_test, reg_predictions, alpha=0.75)
        lower = min(y_reg_test.min(), reg_predictions.min())
        upper = max(y_reg_test.max(), reg_predictions.max())
        ax.plot([lower, upper], [lower, upper], color="black", linestyle="--")
        ax.set_xlabel("Observed log(Papp)")
        ax.set_ylabel("Predicted log(Papp)")
        ax.set_title("Regression Parity Plot")
        fig.tight_layout()
        path = FIGURES_DIR / "publication_parity_plot.png"
        fig.savefig(path, dpi=220)
        plt.close(fig)
        paths.append(path)

        confidence_scores = [
            confidence_from_probability(float(prob))["confidence_score"]
            for prob in probabilities
        ]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(confidence_scores, bins=20, edgecolor="black")
        ax.set_xlabel("Confidence score")
        ax.set_ylabel("Count")
        ax.set_title("Prediction Confidence Distribution")
        fig.tight_layout()
        path = FIGURES_DIR / "publication_confidence_distribution.png"
        fig.savefig(path, dpi=220)
        plt.close(fig)
        paths.append(path)

    return paths


def write_outlier_analysis() -> Path:
    """Write an outlier and reliability analysis report from the saved baseline models."""
    from adme_predictor.modeling import (
        CLASSIFIER_PATH,
        FEATURE_COLUMNS_PATH,
        REGRESSOR_PATH,
        build_feature_matrix,
        split_features,
    )

    output_path = REPORTS_DIR / "outlier_analysis.md"
    data = load_caco2_wang_processed()
    descriptors = pd.DataFrame([calculate_descriptors(s) for s in data["canonical_smiles"]])

    extreme_descriptor_rows = []
    for column in ["molecular_weight", "logp", "tpsa", "rotatable_bonds"]:
        low = descriptors[column].quantile(0.01)
        high = descriptors[column].quantile(0.99)
        count = int(((descriptors[column] <= low) | (descriptors[column] >= high)).sum())
        extreme_descriptor_rows.append(f"- {column}: {count} molecules outside 1st/99th percentile range")

    poorly_predicted = "Saved model artifacts were not available for residual analysis."
    if CLASSIFIER_PATH.exists() and REGRESSOR_PATH.exists() and FEATURE_COLUMNS_PATH.exists():
        regressor = joblib.load(REGRESSOR_PATH)
        if hasattr(regressor, "n_jobs"):
            regressor.n_jobs = 1
        feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
        X, _ = build_feature_matrix(data)
        X = X.loc[:, feature_columns]
        y_class = data["permeability_class"].astype(int)
        y_regression = data["caco2_log_papp"].astype(float)
        _, X_test, _, _, _, y_reg_test = split_features(X, y_class, y_regression)
        predictions = regressor.predict(X_test)
        residuals = (y_reg_test.to_numpy() - predictions)
        worst = pd.DataFrame(
            {
                "canonical_smiles": data.iloc[X_test.index]["canonical_smiles"].to_numpy(),
                "observed_log_papp": y_reg_test.to_numpy(),
                "predicted_log_papp": predictions,
                "absolute_error": abs(residuals),
            }
        ).sort_values("absolute_error", ascending=False).head(10)
        poorly_predicted = worst.to_markdown(index=False) if _has_tabulate() else worst.to_string(index=False)

    output_path.write_text(
        "\n".join(
            [
                "# Outlier and Reliability Analysis",
                "",
                "This analysis reviews molecules and descriptor regions where baseline predictions may be less reliable. It supports early discovery screening only and does not imply clinical validity.",
                "",
                "## Extreme Descriptor Values",
                "",
                *extreme_descriptor_rows,
                "",
                "Extreme molecular weight, TPSA, logP, or flexibility can indicate chemistry that is less represented in the training distribution. Predictions for such molecules should be reviewed with applicability-domain output.",
                "",
                "## Poorly Predicted Molecules",
                "",
                poorly_predicted,
                "",
                "## Possible Reasons for Prediction Failure",
                "",
                "- Chemical diversity limitations: a public benchmark may not cover all scaffolds or chemotypes.",
                "- Dataset limitations: Caco-2 measurements vary with assay protocol, pH, transporter expression, and lab conditions.",
                "- Experimental noise: permeability endpoints can contain measurement variability.",
                "- Domain shift: new molecules may differ from the training chemistry even when descriptors look plausible.",
                "- Descriptor limits: global descriptors and fingerprints may miss ionization, conformation, transporter effects, and formulation-relevant properties.",
            ]
        ),
        encoding="utf-8",
    )
    return output_path


def _has_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401

        return True
    except ImportError:
        return False
