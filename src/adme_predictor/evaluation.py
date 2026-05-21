"""Model evaluation helpers for baseline ADME prediction tasks."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_probability: np.ndarray | None = None,
) -> dict[str, float]:
    """Calculate classification metrics for permeability class prediction."""
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }

    if y_probability is not None and len(set(y_true)) == 2:
        metrics["auroc"] = float(roc_auc_score(y_true, y_probability))
    else:
        metrics["auroc"] = float("nan")

    return metrics


def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Calculate regression metrics for continuous log(Papp) prediction."""
    return {
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def confusion_matrix_dataframe(y_true: np.ndarray, y_pred: np.ndarray) -> pd.DataFrame:
    """Return a labeled 2x2 confusion matrix dataframe."""
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    return pd.DataFrame(
        matrix,
        index=["actual_low", "actual_high"],
        columns=["predicted_low", "predicted_high"],
    )
