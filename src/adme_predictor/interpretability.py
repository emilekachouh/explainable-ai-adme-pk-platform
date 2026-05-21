"""SHAP and feature-importance reporting for ADME baseline models."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from xgboost import XGBClassifier, XGBRegressor

from adme_predictor.config import REPORTS_DIR
from adme_predictor.data import RANDOM_SEED, load_caco2_wang_processed
from adme_predictor.modeling import build_feature_matrix, make_single_feature_row, split_features


SHAP_DIR = REPORTS_DIR / "figures" / "shap"
SHAP_REPORT_PATH = REPORTS_DIR / "shap_interpretation.md"


def _fit_xgboost_models() -> tuple[XGBClassifier, XGBRegressor, pd.DataFrame, pd.Series, pd.Series, list[str]]:
    data = load_caco2_wang_processed()
    X, feature_columns = build_feature_matrix(data)
    y_class = data["permeability_class"].astype(int)
    y_regression = data["caco2_log_papp"].astype(float)
    X_train, X_test, y_class_train, _, y_reg_train, _ = split_features(X, y_class, y_regression)

    classifier = XGBClassifier(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=RANDOM_SEED,
        n_jobs=1,
    )
    regressor = XGBRegressor(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=RANDOM_SEED,
        n_jobs=1,
    )
    classifier.fit(X_train, y_class_train)
    regressor.fit(X_train, y_reg_train)
    return classifier, regressor, X_test, y_class, y_regression, feature_columns


def save_shap_bar_plot(
    values: np.ndarray,
    feature_names: list[str],
    output_path: Path,
    title: str,
    max_display: int = 20,
) -> Path:
    """Save a simple SHAP mean absolute importance bar plot."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    values = np.asarray(values)
    if values.ndim == 1:
        values = values.reshape(1, -1)
    importance = np.abs(values).mean(axis=0)
    order = np.argsort(importance)[-max_display:]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh([feature_names[i] for i in order], importance[order])
    ax.set_title(title)
    ax.set_xlabel("Mean absolute SHAP value")
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)
    return output_path


def save_local_explanation_plot(
    values: np.ndarray,
    feature_values: pd.DataFrame,
    output_path: Path,
    title: str,
    max_display: int = 12,
) -> Path:
    """Save a local top-contribution plot for one molecule."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    values = np.asarray(values).reshape(-1)
    order = np.argsort(np.abs(values))[-max_display:]
    labels = [
        f"{feature_values.columns[i]}={feature_values.iloc[0, i]:.3g}"
        for i in order
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#b91c1c" if values[i] > 0 else "#1d4ed8" for i in order]
    ax.barh(labels, values[order], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title(title)
    ax.set_xlabel("Local SHAP contribution")
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)
    return output_path


def generate_shap_outputs(max_samples: int = 150) -> list[Path]:
    """Train XGBoost reference models and save SHAP plots/report."""
    import shap

    SHAP_DIR.mkdir(parents=True, exist_ok=True)
    classifier, regressor, X_test, _, _, feature_columns = _fit_xgboost_models()
    sample = X_test.sample(n=min(max_samples, len(X_test)), random_state=RANDOM_SEED)
    output_paths: list[Path] = []

    for model, name in [(classifier, "classifier"), (regressor, "regressor")]:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(sample)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        plt.figure()
        shap.summary_plot(shap_values, sample, show=False, max_display=25)
        path = SHAP_DIR / f"{name}_summary.png"
        plt.tight_layout()
        plt.savefig(path, dpi=220, bbox_inches="tight")
        plt.close()
        output_paths.append(path)

        explanation = shap.Explanation(
            values=shap_values,
            data=sample.to_numpy(),
            feature_names=sample.columns.tolist(),
        )
        shap.plots.beeswarm(explanation, show=False, max_display=25)
        path = SHAP_DIR / f"{name}_beeswarm.png"
        plt.tight_layout()
        plt.savefig(path, dpi=220, bbox_inches="tight")
        plt.close()
        output_paths.append(path)

        output_paths.append(
            save_shap_bar_plot(
                shap_values,
                feature_columns,
                SHAP_DIR / f"{name}_bar_importance.png",
                f"{name.title()} SHAP Feature Importance",
            )
        )

    aspirin = "CC(=O)OC1=CC=CC=C1C(=O)O"
    caffeine = "Cn1cnc2c1c(=O)n(C)c(=O)n2C"
    classifier_explainer = shap.TreeExplainer(classifier)
    for label, smiles in [("aspirin", aspirin), ("caffeine", caffeine)]:
        row = make_single_feature_row(smiles, feature_columns)
        local_values = classifier_explainer.shap_values(row)
        if isinstance(local_values, list):
            local_values = local_values[1]
        output_paths.append(
            save_local_explanation_plot(
                local_values,
                row,
                SHAP_DIR / f"local_{label}_classifier.png",
                f"Local SHAP Explanation: {label.title()}",
            )
        )

    write_shap_interpretation_report()
    return output_paths


def write_shap_interpretation_report() -> Path:
    """Write a scientific SHAP interpretation report."""
    SHAP_REPORT_PATH.write_text(
        "\n".join(
            [
                "# SHAP Interpretation Report",
                "",
                "This report interprets XGBoost classifier and regressor behavior for the TDC Caco2_Wang Caco-2 permeability benchmark. The analysis supports explainable early ADME screening; it does not establish clinical PK or PBPK validity.",
                "",
                "## Scientific Interpretation",
                "",
                "- TPSA: Higher polar surface area commonly reduces passive membrane diffusion because polar surface must be desolvated before crossing lipid-rich barriers.",
                "- HBD/HBA: Hydrogen bond donors and acceptors can increase aqueous interaction and reduce passive permeability when excessive, consistent with Lipinski-style ADME heuristics.",
                "- Molecular weight: Larger molecules often show lower passive permeability because size increases desolvation and conformational costs.",
                "- logP: Moderate lipophilicity can support membrane partitioning, but very high logP may introduce solubility and assay-liability concerns.",
                "- Flexibility: Many rotatable bonds can reduce permeability by increasing entropic cost and conformational heterogeneity.",
                "- Fingerprint contributions: Morgan fingerprint bits capture scaffold-specific and substituent-specific motifs not represented by global descriptors.",
                "",
                "## Scaffold-Related Chemistry",
                "",
                "SHAP values on fingerprint bits should be interpreted as structural pattern signals, not direct mechanistic causal claims. Their importance indicates that local substructures and scaffolds contribute to model decisions.",
                "",
                "## Passive Permeability and Oral Absorption Context",
                "",
                "Caco-2 permeability is a useful in vitro proxy for intestinal epithelial transport, but oral absorption also depends on solubility, dissolution, metabolism, transporters, protein binding, dose, formulation, and physiology. These models should therefore support early prioritization rather than clinical prediction.",
            ]
        ),
        encoding="utf-8",
    )
    return SHAP_REPORT_PATH
