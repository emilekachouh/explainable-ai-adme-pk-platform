import numpy as np
import pandas as pd
import pytest

from adme_predictor.nca import (
    calculate_nca,
    estimate_lambda_z,
    linear_trapezoidal_auc,
    linear_trapezoidal_aumc,
)


def test_auc_calculation():
    time = np.array([0.0, 1.0, 2.0])
    concentration = np.array([10.0, 5.0, 0.0])

    assert linear_trapezoidal_auc(time, concentration) == pytest.approx(10.0)


def test_aumc_calculation():
    time = np.array([0.0, 1.0, 2.0])
    concentration = np.array([10.0, 5.0, 0.0])

    assert linear_trapezoidal_aumc(time, concentration) == pytest.approx(5.0)


def test_mrt_and_iv_clearance_calculation():
    time = np.arange(0.0, 25.0, 1.0)
    concentration = 10.0 * np.exp(-0.2 * time)
    profile = pd.DataFrame({"time": time, "concentration": concentration})

    summary, warnings = calculate_nca(profile, dose=100.0, route="IV bolus")

    assert summary["mrt"] > 0
    assert summary["clearance_label"] == "CL"
    assert summary["clearance"] == pytest.approx(2.0, rel=0.15)
    assert summary["vss"] > 0
    assert not any("fewer than 3" in warning for warning in warnings)


def test_oral_clearance_labeling_logic():
    time = np.arange(0.0, 25.0, 1.0)
    concentration = 5.0 * np.exp(-0.2 * time)
    profile = pd.DataFrame({"time": time, "concentration": concentration})

    summary, warnings = calculate_nca(profile, dose=100.0, route="oral")

    assert summary["clearance_label"] == "CL/F"
    assert np.isnan(summary["vss"])
    assert any("CL/F" in warning for warning in warnings)


def test_high_percent_extrapolated_warning():
    profile = pd.DataFrame(
        {
            "time": np.array([0.0, 1.0, 2.0]),
            "concentration": np.array([10.0, 9.0, 8.1]),
        }
    )

    summary, warnings = calculate_nca(profile, dose=100.0, route="IV bolus")

    assert summary["percent_auc_extrapolated"] > 20
    assert any("Percent extrapolated AUC is high" in warning for warning in warnings)


def test_terminal_phase_warning_with_too_few_points():
    time = np.array([0.0, 1.0, 2.0])
    concentration = np.array([0.0, 10.0, 5.0])

    lambda_z, _, warnings = estimate_lambda_z(time, concentration)

    assert np.isnan(lambda_z)
    assert any("fewer than 3" in warning for warning in warnings)
