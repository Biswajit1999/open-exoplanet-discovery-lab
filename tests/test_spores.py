import numpy as np
import pandas as pd

from exolab.spores import (
    calibrated_group_power_threshold,
    clean_spores_rv,
    eccentric_rv_signal,
    interpolate_completeness_threshold,
    nightly_bin_spores_rv,
    orbital_draws,
    project_spores_nuisance,
)


def test_catalogue_cleaning_and_nightly_binning_are_explicit():
    frame = pd.DataFrame(
        {
            "HD": ["1", "1", "1", "1"],
            "BJD": [2450000.1, 2450000.2, 2450001.1, 2450002.0],
            "RVel": [1.0, 3.0, -1.0, 9.0],
            "e_RVel": [1.0, 1.0, 2.0, -1.0],
            "Inst": ["A", "A", "A", "A"],
            "BibCode": ["x", "x", "x", "x"],
        }
    )
    clean, diagnostics = clean_spores_rv(frame)
    assert len(clean) == 2
    assert diagnostics["sentinel_rows"] == 2
    binned = nightly_bin_spores_rv(frame)
    assert len(binned) == 1
    assert np.isclose(binned.iloc[0]["rv_mps"], 2.0)
    assert np.isclose(binned.iloc[0]["rv_error_mps"], np.sqrt(0.5))


def test_instrument_and_trend_projection_removes_declared_nuisance():
    time = np.linspace(0, 900, 120)
    instrument = np.where(np.arange(120) < 60, "A", "B")
    scaled = (time - np.median(time)) / 365.25
    values = np.where(instrument == "A", 7.0, -3.0) + 2.2 * scaled
    result = project_spores_nuisance(
        time,
        values,
        np.ones_like(time),
        instruments=instrument,
        trend_degree=1,
    )
    assert np.std(result.residuals) < 1e-10
    assert "trend:1" in result.terms


def test_orbital_draws_and_eccentric_signal_are_reproducible():
    first = orbital_draws(8, seed=42, eccentric=True)
    second = orbital_draws(8, seed=42, eccentric=True)
    pd.testing.assert_frame_equal(first, second)
    assert ((first["eccentricity"] >= 0) & (first["eccentricity"] < 1)).all()
    time = np.linspace(0, 50, 100)
    signal = eccentric_rv_signal(
        time,
        period=12.0,
        semi_amplitude=3.0,
        eccentricity=0.3,
        omega_radians=0.8,
        mean_anomaly_phase=1.2,
    )
    assert np.isfinite(signal).all()
    assert np.ptp(signal) > 5.0


def test_group_null_thresholds_are_finite_and_threshold_interpolates():
    rng = np.random.default_rng(7)
    time = np.sort(rng.uniform(0, 300, 80))
    group = np.where(np.arange(80) < 40, "A", "B")
    error = np.full(80, 0.8)
    residual = rng.normal(0, 0.8, 80)
    for null in ("white", "correlated"):
        threshold = calibrated_group_power_threshold(
            time,
            residual,
            error,
            group,
            min_period=2,
            max_period=100,
            n_permutations=20,
            seed=11,
            null=null,
        )
        assert 0 < threshold < 1
    assert np.isclose(
        interpolate_completeness_threshold([1, 2, 3], [0.1, 0.6, 1.0], 0.5),
        1.8,
    )
