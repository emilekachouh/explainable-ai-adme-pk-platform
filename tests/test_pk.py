import numpy as np
import pytest

from adme_predictor.pk import (
    make_time_grid,
    simulate_iv_bolus,
    simulate_iv_infusion,
    simulate_oral_first_order,
    simulate_pk_profile,
)


def test_iv_bolus_concentration_calculation():
    times = np.array([0.0, 1.0])
    profile = simulate_iv_bolus(dose=100.0, vd=10.0, kel=0.1, times=times)

    assert profile.loc[0, "concentration"] == pytest.approx(10.0)
    assert profile.loc[1, "concentration"] == pytest.approx(10.0 * np.exp(-0.1))


def test_oral_concentration_calculation():
    times = np.array([0.0, 1.0])
    profile, warnings = simulate_oral_first_order(
        dose=100.0,
        vd=10.0,
        kel=0.1,
        ka=1.0,
        bioavailability=0.8,
        times=times,
    )
    expected = (0.8 * 100.0 * 1.0 / (10.0 * (1.0 - 0.1))) * (
        np.exp(-0.1) - np.exp(-1.0)
    )

    assert profile.loc[0, "concentration"] == pytest.approx(0.0)
    assert profile.loc[1, "concentration"] == pytest.approx(expected)
    assert warnings == []


def test_oral_ka_equal_kel_uses_stable_limit_warning():
    times = np.array([0.0, 1.0])
    profile, warnings = simulate_oral_first_order(
        dose=100.0,
        vd=10.0,
        kel=0.5,
        ka=0.5,
        bioavailability=1.0,
        times=times,
    )

    assert profile.loc[1, "concentration"] == pytest.approx(5.0 * np.exp(-0.5))
    assert any("ka <=" in warning for warning in warnings)
    assert any("limiting approximation" in warning for warning in warnings)


def test_iv_infusion_calculation():
    times = np.array([0.0, 1.0, 2.0])
    profile = simulate_iv_infusion(
        dose=100.0,
        vd=10.0,
        kel=0.1,
        infusion_duration=1.0,
        times=times,
    )

    assert profile.loc[0, "concentration"] == pytest.approx(0.0)
    assert profile.loc[1, "concentration"] > 0
    assert profile.loc[2, "concentration"] < profile.loc[1, "concentration"]


def test_make_time_grid_and_route_dispatch():
    profile, warnings = simulate_pk_profile(
        route="IV bolus",
        dose=100.0,
        vd=10.0,
        kel=0.1,
        duration=2.0,
        interval=1.0,
    )

    assert len(profile) == 3
    assert warnings == []
    assert np.array_equal(make_time_grid(2.0, 1.0), np.array([0.0, 1.0, 2.0]))
