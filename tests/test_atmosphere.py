import numpy as np
import pytest

from exolab.atmosphere import (
    blackbody_eclipse_depth_ppm,
    estimate_extra_scatter,
    fit_blackbody_temperature,
    standardized_pairwise_differences,
    weighted_band_mean,
    weighted_polynomial_fit_statistics,
)


def test_consistent_measurements_need_no_extra_scatter():
    result = estimate_extra_scatter([100.0, 100.2, 99.9, 100.1], [1.0, 1.0, 1.0, 1.0])
    assert result.extra_scatter == 0.0
    assert result.reduced_chi2 < 1.0


def test_inconsistent_measurements_infer_positive_extra_scatter():
    result = estimate_extra_scatter([90.0, 110.0, 95.0, 115.0], [1.0, 1.0, 1.0, 1.0])
    assert result.extra_scatter > 0
    assert np.isclose(result.reduced_chi2, 1.0, atol=1e-7)
    assert standardized_pairwise_differences([90.0, 110.0], [1.0, 1.0]).size == 1


def test_weighted_band_mean_uses_only_requested_bins():
    result = weighted_band_mean(
        [3.9, 4.1, 4.2, 5.0],
        [99.0, 10.0, 14.0, 99.0],
        [1.0, 2.0, 2.0, 1.0],
        4.0,
        4.9,
    )
    assert result.mean == 12.0
    assert result.n_bins == 2
    assert result.error == pytest.approx(2.0**0.5)


def test_blackbody_retrieval_recovers_synthetic_temperature():
    wavelength = np.linspace(2.1, 5.0, 40)
    model = blackbody_eclipse_depth_ppm(wavelength, 2400.0, 5200.0, 0.0182)
    result = fit_blackbody_temperature(
        wavelength,
        model,
        np.full_like(model, 8.0),
        stellar_temperature_k=5200.0,
        radius_ratio=0.0182,
    )
    assert result.temperature_k == pytest.approx(2400.0, abs=0.1)
    assert result.lower_status == "bracketed"
    assert result.upper_status == "bracketed"
    assert result.chi2 < 1e-8


def test_empirical_spectrum_bic_rewards_required_slope():
    wavelength = np.linspace(4.0, 5.0, 30)
    depth = 50.0 + 80.0 * (wavelength - wavelength.mean())
    error = np.full(30, 5.0)
    flat = weighted_polynomial_fit_statistics(wavelength, depth, error, degree=0)
    slope = weighted_polynomial_fit_statistics(wavelength, depth, error, degree=1)
    assert slope["bic"] < flat["bic"]
