"""Baseline machine-learning pipeline for Caco-2 permeability prediction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier, XGBRegressor

from adme_predictor.config import MODELS_DIR, REPORTS_DIR
from adme_predictor.data import RANDOM_SEED, load_caco2_wang_processed
from adme_predictor.evaluation import (
    confusion_matrix_dataframe,
    evaluate_classification,
    evaluate_regression,
)
from adme_predictor.features import (
    DESCRIPTOR_KEYS,
    LIPINSKI_FLAG_KEYS,
    build_feature_vector,
    generate_morgan_fingerprint,
)
from adme_predictor.scaffold import get_bemis_murcko_scaffold, scaffold_split


FIGURES_DIR = REPORTS_DIR / "figures"
CLASSIFIER_PATH = MODELS_DIR / "baseline_permeability_classifier.joblib"
REGRESSOR_PATH = MODELS_DIR / "baseline_permeability_regressor.joblib"
FEATURE_COLUMNS_PATH = MODELS_DIR / "baseline_feature_columns.joblib"
METRICS_PATH = REPORTS_DIR / "baseline_metrics.csv"
CONFUSION_MATRIX_PATH = REPORTS_DIR / "confusion_matrix.csv"
FEATURE_IMPORTANCE_PATH = REPORTS_DIR / "feature_importance.csv"
MODEL_CARD_PATH = REPORTS_DIR / "baseline_model_card.md"
SCAFFOLD_METRICS_PATH = REPORTS_DIR / "scaffold_split_metrics.csv"
SCAFFOLD_COMPARISON_PATH = REPORTS_DIR / "scaffold_split_comparison.md"
SCAFFOLD_CONFUSION_MATRIX_PATH = REPORTS_DIR / "scaffold_confusion_matrix.csv"


@dataclass(frozen=True)
class TrainingResult:
    """Paths and key results from a baseline training run."""

    best_classifier_name: str
    best_classifier_f1: float
    best_classifier_auroc: float
    best_regressor_name: str
    best_regressor_mae: float
    metrics_path: Path
    classifier_path: Path
    regressor_path: Path


def featurize_smiles(smiles: str, include_fingerprint: bool = True) -> dict[str, float | int | bool]:
    """Generate descriptor, flag, and optional Morgan fingerprint features."""
    features = build_feature_vector(smiles)

    if include_fingerprint:
        fingerprint = generate_morgan_fingerprint(smiles)
        features.update({f"morgan_{index}": bit for index, bit in enumerate(fingerprint)})

    return features


def build_feature_matrix(
    df: pd.DataFrame,
    smiles_column: str = "canonical_smiles",
    include_fingerprint: bool = True,
) -> tuple[pd.DataFrame, list[str]]:
    """Convert validated molecules into a numeric modeling matrix."""
    if smiles_column not in df.columns:
        raise ValueError(f"Missing SMILES column: {smiles_column}")

    rows = [featurize_smiles(smiles, include_fingerprint) for smiles in df[smiles_column]]
    matrix = pd.DataFrame(rows)
    matrix = matrix.apply(pd.to_numeric, errors="raise")
    return matrix, matrix.columns.tolist()


def make_single_feature_row(smiles: str, feature_columns: list[str]) -> pd.DataFrame:
    """Create one feature row aligned to saved training columns."""
    row = pd.DataFrame([featurize_smiles(smiles)])
    for column in feature_columns:
        if column not in row.columns:
            row[column] = 0
    return row.loc[:, feature_columns].apply(pd.to_numeric, errors="raise")


def split_features(
    X: pd.DataFrame,
    y_class: pd.Series,
    y_regression: pd.Series,
    test_size: float = 0.2,
    random_state: int = RANDOM_SEED,
):
    """Create one leakage-safe split reused by classification and regression."""
    indices = np.arange(len(X))
    train_idx, test_idx = train_test_split(
        indices,
        test_size=test_size,
        random_state=random_state,
        stratify=y_class,
    )
    return (
        X.iloc[train_idx],
        X.iloc[test_idx],
        y_class.iloc[train_idx],
        y_class.iloc[test_idx],
        y_regression.iloc[train_idx],
        y_regression.iloc[test_idx],
    )


def _classification_models(scale_pos_weight: float) -> dict[str, object]:
    return {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=RANDOM_SEED,
                    ),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_SEED,
            n_jobs=1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=250,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=RANDOM_SEED,
            n_jobs=1,
            scale_pos_weight=scale_pos_weight,
        ),
    }


def _regression_models() -> dict[str, object]:
    return {
        "linear_regression": Pipeline(
            [("scaler", StandardScaler()), ("model", LinearRegression())]
        ),
        "random_forest_regressor": RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=RANDOM_SEED,
            n_jobs=1,
        ),
        "xgboost_regressor": XGBRegressor(
            n_estimators=250,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=RANDOM_SEED,
            n_jobs=1,
        ),
    }


def _predict_probability(model: object, X: pd.DataFrame) -> np.ndarray | None:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    return None


def _plot_confusion_matrix(confusion_df: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(4.5, 4))
    image = ax.imshow(confusion_df.values, cmap="Blues")
    ax.set_xticks(range(2), confusion_df.columns, rotation=25, ha="right")
    ax.set_yticks(range(2), confusion_df.index)
    ax.set_title("Permeability Class Confusion Matrix")
    for row in range(2):
        for col in range(2):
            ax.text(col, row, int(confusion_df.iloc[row, col]), ha="center", va="center")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "confusion_matrix.png", dpi=200)
    plt.close(fig)


def _save_feature_importance(model: object, feature_columns: list[str]) -> pd.DataFrame:
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif isinstance(model, Pipeline) and hasattr(model[-1], "coef_"):
        importances = np.abs(model[-1].coef_[0])
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        importances = np.zeros(len(feature_columns))

    importance_df = pd.DataFrame(
        {"feature": feature_columns, "importance": np.asarray(importances, dtype=float)}
    ).sort_values("importance", ascending=False)
    importance_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False)

    top = importance_df.head(25).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.barh(top["feature"], top["importance"])
    ax.set_title("Top Baseline Feature Importances")
    ax.set_xlabel("Relative importance")
    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / "feature_importance.png", dpi=200)
    plt.close(fig)
    return importance_df


def _try_save_shap_summary(model: object, X_test: pd.DataFrame) -> str:
    try:
        import shap

        if isinstance(model, Pipeline):
            return "SHAP skipped for pipeline model; feature importance saved instead."

        sample = X_test.sample(n=min(100, len(X_test)), random_state=RANDOM_SEED)
        explainer = shap.TreeExplainer(model)
        values = explainer.shap_values(sample)
        if isinstance(values, list):
            values = values[1]
        shap.summary_plot(values, sample, show=False, max_display=20)
        plt.tight_layout()
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        plt.savefig(FIGURES_DIR / "shap_summary.png", dpi=200, bbox_inches="tight")
        plt.close()
        return "SHAP summary saved for the best tree-based classifier."
    except Exception as exc:
        return f"SHAP skipped: {exc}"


def _write_model_card(result_notes: str, best_classifier_name: str) -> None:
    MODEL_CARD_PATH.write_text(
        "\n".join(
            [
                "# Baseline Caco-2 Permeability Model",
                "",
                "This is an early discovery ADME screening prototype, not a clinical prediction tool.",
                "",
                "Dataset: TDC Caco2_Wang public benchmark.",
                "Endpoint: experimental Caco-2 log(Papp).",
                "Classification target: high vs low permeability using the processed dataset median.",
                "Regression target: continuous log(Papp).",
                f"Selected classifier: {best_classifier_name}.",
                "",
                "Scientific caveats:",
                "- Caco-2 is an in vitro permeability proxy and does not prove human absorption.",
                "- The median class threshold is data-derived and should not be treated as a clinical cutoff.",
                "- Random train/test splitting can overestimate generalization to new chemical scaffolds.",
                "- Descriptor and fingerprint baselines are useful controls, not final validated models.",
                "",
                f"Interpretability note: {result_notes}",
            ]
        ),
        encoding="utf-8",
    )


def train_baseline_pipeline(force_data_refresh: bool = False) -> TrainingResult:
    """Train baseline classification and regression models on Caco2_Wang."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    data = load_caco2_wang_processed(force_download=force_data_refresh)
    X, feature_columns = build_feature_matrix(data)
    y_class = data["permeability_class"].astype(int)
    y_regression = data["caco2_log_papp"].astype(float)

    (
        X_train,
        X_test,
        y_class_train,
        y_class_test,
        y_reg_train,
        y_reg_test,
    ) = split_features(X, y_class, y_regression)

    positive = int(y_class_train.sum())
    negative = int(len(y_class_train) - positive)
    scale_pos_weight = float(negative / positive) if positive else 1.0

    metric_rows = []
    trained_classifiers = {}
    for name, model in _classification_models(scale_pos_weight).items():
        model.fit(X_train, y_class_train)
        y_pred = model.predict(X_test)
        y_prob = _predict_probability(model, X_test)
        metrics = evaluate_classification(y_class_test.to_numpy(), y_pred, y_prob)
        metric_rows.append({"task": "classification", "model": name, **metrics})
        trained_classifiers[name] = model

    trained_regressors = {}
    for name, model in _regression_models().items():
        model.fit(X_train, y_reg_train)
        y_pred = model.predict(X_test)
        metrics = evaluate_regression(y_reg_test.to_numpy(), y_pred)
        metric_rows.append({"task": "regression", "model": name, **metrics})
        trained_regressors[name] = model

    metrics_df = pd.DataFrame(metric_rows)
    metrics_df.to_csv(METRICS_PATH, index=False)

    class_metrics = metrics_df[metrics_df["task"] == "classification"].copy()
    class_metrics = class_metrics.sort_values(["f1", "balanced_accuracy", "auroc"], ascending=False)
    best_classifier_name = str(class_metrics.iloc[0]["model"])
    best_classifier = trained_classifiers[best_classifier_name]

    reg_metrics = metrics_df[metrics_df["task"] == "regression"].copy()
    reg_metrics = reg_metrics.sort_values("mae", ascending=True)
    best_regressor_name = str(reg_metrics.iloc[0]["model"])
    best_regressor = trained_regressors[best_regressor_name]

    y_best_pred = best_classifier.predict(X_test)
    confusion_df = confusion_matrix_dataframe(y_class_test.to_numpy(), y_best_pred)
    confusion_df.to_csv(CONFUSION_MATRIX_PATH)
    _plot_confusion_matrix(confusion_df)
    _save_feature_importance(best_classifier, feature_columns)
    shap_note = _try_save_shap_summary(best_classifier, X_test)

    joblib.dump(best_classifier, CLASSIFIER_PATH)
    joblib.dump(best_regressor, REGRESSOR_PATH)
    joblib.dump(feature_columns, FEATURE_COLUMNS_PATH)
    _write_model_card(shap_note, best_classifier_name)

    return TrainingResult(
        best_classifier_name=best_classifier_name,
        best_classifier_f1=float(class_metrics.iloc[0]["f1"]),
        best_classifier_auroc=float(class_metrics.iloc[0]["auroc"]),
        best_regressor_name=best_regressor_name,
        best_regressor_mae=float(reg_metrics.iloc[0]["mae"]),
        metrics_path=METRICS_PATH,
        classifier_path=CLASSIFIER_PATH,
        regressor_path=REGRESSOR_PATH,
    )


def _evaluate_models_on_split(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_class_train: pd.Series,
    y_class_test: pd.Series,
    y_reg_train: pd.Series,
    y_reg_test: pd.Series,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    positive = int(y_class_train.sum())
    negative = int(len(y_class_train) - positive)
    scale_pos_weight = float(negative / positive) if positive else 1.0

    metric_rows = []
    trained_classifiers = {}
    for name, model in _classification_models(scale_pos_weight).items():
        model.fit(X_train, y_class_train)
        y_pred = model.predict(X_test)
        y_prob = _predict_probability(model, X_test)
        metrics = evaluate_classification(y_class_test.to_numpy(), y_pred, y_prob)
        metric_rows.append({"task": "classification", "model": name, **metrics})
        trained_classifiers[name] = model

    trained_regressors = {}
    for name, model in _regression_models().items():
        model.fit(X_train, y_reg_train)
        y_pred = model.predict(X_test)
        metrics = evaluate_regression(y_reg_test.to_numpy(), y_pred)
        metric_rows.append({"task": "regression", "model": name, **metrics})
        trained_regressors[name] = model

    return pd.DataFrame(metric_rows), trained_classifiers, trained_regressors


def _split_summary(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict[str, int | str]:
    train_scaffolds = set(train_df["canonical_smiles"].map(get_bemis_murcko_scaffold))
    test_scaffolds = set(test_df["canonical_smiles"].map(get_bemis_murcko_scaffold))
    overlap = train_scaffolds.intersection(test_scaffolds)

    return {
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_unique_scaffolds": int(len(train_scaffolds)),
        "test_unique_scaffolds": int(len(test_scaffolds)),
        "total_unique_scaffolds": int(len(train_scaffolds.union(test_scaffolds))),
        "overlapping_scaffolds": int(len(overlap)),
        "train_class_counts": str(train_df["permeability_class"].value_counts().sort_index().to_dict()),
        "test_class_counts": str(test_df["permeability_class"].value_counts().sort_index().to_dict()),
    }


def _comparison_table(random_metrics: pd.DataFrame, scaffold_metrics: pd.DataFrame) -> pd.DataFrame:
    random_long = random_metrics.copy()
    random_long["validation"] = "random"
    scaffold_long = scaffold_metrics.copy()
    scaffold_long["validation"] = "scaffold"
    combined = pd.concat([random_long, scaffold_long], ignore_index=True)

    metric_columns = [
        "accuracy",
        "balanced_accuracy",
        "precision",
        "recall",
        "f1",
        "auroc",
        "rmse",
        "mae",
        "r2",
    ]
    rows = []
    for _, scaffold_row in scaffold_metrics.iterrows():
        match = random_metrics[
            (random_metrics["task"] == scaffold_row["task"])
            & (random_metrics["model"] == scaffold_row["model"])
        ]
        for metric in metric_columns:
            if metric not in scaffold_metrics.columns or pd.isna(scaffold_row.get(metric)):
                continue
            random_value = float(match.iloc[0][metric]) if not match.empty and not pd.isna(match.iloc[0].get(metric)) else float("nan")
            scaffold_value = float(scaffold_row[metric])
            rows.append(
                {
                    "task": scaffold_row["task"],
                    "model": scaffold_row["model"],
                    "metric": metric,
                    "random_split": random_value,
                    "scaffold_split": scaffold_value,
                    "performance_drop": random_value - scaffold_value,
                }
            )
    return pd.DataFrame(rows)


def _write_scaffold_comparison_report(
    comparison: pd.DataFrame,
    split_summary: dict[str, int | str],
    best_classifier: pd.Series,
    best_regressor: pd.Series,
) -> None:
    key_metrics = comparison[
        comparison["metric"].isin(["auroc", "f1", "balanced_accuracy", "mae", "r2"])
    ].copy()
    key_table = _dataframe_to_markdown(key_metrics)

    SCAFFOLD_COMPARISON_PATH.write_text(
        "\n".join(
            [
                "# Scaffold Split Validation Comparison",
                "",
                "This report compares the original random split baseline with a Bemis-Murcko scaffold split. Scaffold splitting is stricter because compounds sharing the same core scaffold are kept entirely in train or test, reducing the chance that the model benefits from close structural analogs across the split.",
                "",
                "## Split Summary",
                "",
                f"- Train rows: {split_summary['train_rows']}",
                f"- Test rows: {split_summary['test_rows']}",
                f"- Total unique scaffolds: {split_summary['total_unique_scaffolds']}",
                f"- Train unique scaffolds: {split_summary['train_unique_scaffolds']}",
                f"- Test unique scaffolds: {split_summary['test_unique_scaffolds']}",
                f"- Overlapping scaffolds: {split_summary['overlapping_scaffolds']}",
                f"- Train class counts: {split_summary['train_class_counts']}",
                f"- Test class counts: {split_summary['test_class_counts']}",
                "",
                "## Metric Comparison",
                "",
                key_table,
                "",
                "## Scientific Interpretation",
                "",
                "Scaffold split validation is harder than random splitting in drug-discovery ML because the test set is chemically less redundant with the training set. A model that performs well only on a random split may be learning scaffold similarity rather than portable ADME relationships.",
                "",
                f"The best scaffold-split classifier was `{best_classifier['model']}` with AUROC {best_classifier['auroc']:.3f}, balanced accuracy {best_classifier['balanced_accuracy']:.3f}, and F1 {best_classifier['f1']:.3f}. This should be interpreted as a stricter estimate of prospective screening behavior than the random split.",
                "",
                f"The best scaffold-split regressor was `{best_regressor['model']}` with MAE {best_regressor['mae']:.3f} and R2 {best_regressor['r2']:.3f}. Regression performance is especially sensitive to whether the test scaffolds occupy endpoint ranges represented in training.",
                "",
                "If scaffold performance drops relative to random split performance, that does not mean the model is useless. It means the original random split likely benefited from chemically similar analogs appearing in both train and test. The scaffold result is more credible for early discovery screening because it asks whether descriptors and fingerprints capture transferable permeability patterns.",
                "",
                "Important ADME interpretation remains qualitative: TPSA, HBD/HBA, logP, molecular weight, and flexibility are mechanistically relevant to permeability, but this model is not a clinical predictor. It is an explainable AI-assisted ADME screening prototype.",
                "",
                "For recruiter or interviewer credibility, showing both random and scaffold validation is valuable because it demonstrates awareness of chemical leakage, dataset bias, and the difference between conventional ML validation and drug-discovery validation.",
            ]
        ),
        encoding="utf-8",
    )


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a simple markdown table without optional pandas dependencies."""
    if df.empty:
        return "No comparison table available."

    columns = df.columns.tolist()
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in df.iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def train_scaffold_split_pipeline() -> pd.DataFrame:
    """Train baseline models using a Bemis-Murcko scaffold split."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    data = load_caco2_wang_processed()
    train_df, test_df = scaffold_split(
        data,
        smiles_col="canonical_smiles",
        test_size=0.2,
        random_state=RANDOM_SEED,
    )
    split_summary = _split_summary(train_df, test_df)
    if split_summary["overlapping_scaffolds"] != 0:
        raise ValueError("Scaffold leakage detected between train and test splits.")

    X_train, feature_columns = build_feature_matrix(train_df)
    X_test, _ = build_feature_matrix(test_df)
    X_test = X_test.loc[:, feature_columns]

    metrics_df, classifiers, _ = _evaluate_models_on_split(
        X_train,
        X_test,
        train_df["permeability_class"].astype(int),
        test_df["permeability_class"].astype(int),
        train_df["caco2_log_papp"].astype(float),
        test_df["caco2_log_papp"].astype(float),
    )

    for key, value in split_summary.items():
        metrics_df[key] = value
    metrics_df.to_csv(SCAFFOLD_METRICS_PATH, index=False)

    class_metrics = metrics_df[metrics_df["task"] == "classification"].copy()
    class_metrics = class_metrics.sort_values(["f1", "balanced_accuracy", "auroc"], ascending=False)
    best_classifier = class_metrics.iloc[0]
    y_pred = classifiers[str(best_classifier["model"])].predict(X_test)
    confusion_df = confusion_matrix_dataframe(test_df["permeability_class"].to_numpy(), y_pred)
    confusion_df.to_csv(SCAFFOLD_CONFUSION_MATRIX_PATH)

    random_metrics = pd.read_csv(METRICS_PATH) if METRICS_PATH.exists() else pd.DataFrame()
    if not random_metrics.empty:
        comparison = _comparison_table(random_metrics, metrics_df)
        comparison.to_csv(REPORTS_DIR / "scaffold_vs_random_metric_comparison.csv", index=False)
    else:
        comparison = pd.DataFrame()

    reg_metrics = metrics_df[metrics_df["task"] == "regression"].copy()
    reg_metrics = reg_metrics.sort_values("mae", ascending=True)
    _write_scaffold_comparison_report(
        comparison,
        split_summary,
        best_classifier,
        reg_metrics.iloc[0],
    )
    return metrics_df


def load_baseline_classifier() -> tuple[object, list[str]]:
    """Load the saved baseline classifier and feature columns."""
    if not CLASSIFIER_PATH.exists() or not FEATURE_COLUMNS_PATH.exists():
        raise FileNotFoundError("Baseline classifier has not been trained yet.")
    return joblib.load(CLASSIFIER_PATH), joblib.load(FEATURE_COLUMNS_PATH)


def predict_permeability_class(smiles: str) -> dict[str, float | int | str]:
    """Predict median-threshold Caco-2 permeability class for one molecule."""
    model, feature_columns = load_baseline_classifier()
    X = make_single_feature_row(smiles, feature_columns)
    predicted_class = int(model.predict(X)[0])
    probability = _predict_probability(model, X)
    high_probability = float(probability[0]) if probability is not None else float("nan")
    label = "high permeability class" if predicted_class == 1 else "low permeability class"
    return {
        "predicted_class": predicted_class,
        "predicted_label": label,
        "high_permeability_probability": high_probability,
    }
