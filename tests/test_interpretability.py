import numpy as np
from pathlib import Path

from adme_predictor.interpretability import save_shap_bar_plot, save_local_explanation_plot


TEST_OUTPUT_DIR = Path("reports") / "figures" / "test_outputs"


def test_shap_bar_plot_generation():
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    values = np.array([[0.1, -0.2, 0.3], [0.2, -0.1, 0.4]])
    path = save_shap_bar_plot(
        values,
        ["mw", "tpsa", "logp"],
        TEST_OUTPUT_DIR / "bar.png",
        "Test SHAP Bar",
    )

    assert path.exists()
    assert path.stat().st_size > 0


def test_local_explanation_plot_generation():
    import pandas as pd

    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    values = np.array([0.1, -0.2, 0.3])
    features = pd.DataFrame([[180.0, 60.0, 1.2]], columns=["mw", "tpsa", "logp"])
    path = save_local_explanation_plot(
        values,
        features,
        TEST_OUTPUT_DIR / "local.png",
        "Local Explanation",
    )

    assert path.exists()
    assert path.stat().st_size > 0
