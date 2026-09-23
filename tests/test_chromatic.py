import numpy as np

from exolab.chromatic import compare_fixed_period_signal, simultaneity_counts


def test_simultaneity_windows_are_monotonic():
    optical = np.array([1.0, 2.0, 3.0, 8.0])
    nir = np.array([1.02, 2.2, 4.0, 8.1])
    counts = simultaneity_counts(optical, nir)
    values = [counts["1h"], counts["6h"], counts["1d"], counts["3d"], counts["7d"]]
    assert values == sorted(values)


def test_chromatic_fixed_period_recovers_amplitude_ratio():
    period = 12.3
    phase = 0.31
    optical_t = np.linspace(0.0, 70.0, 120)
    nir_t = optical_t + 0.01
    optical = 10.0 + 4.0 * np.sin(2.0 * np.pi * optical_t / period + phase)
    nir = -3.0 + 2.8 * np.sin(2.0 * np.pi * nir_t / period + phase)
    error = np.full(optical_t.size, 0.3)

    result = compare_fixed_period_signal(
        optical_t, optical, error, nir_t, nir, error, period
    )

    assert np.isclose(result.amplitude_ratio_nir_to_optical, 0.7, atol=1e-8)
    assert abs(result.phase_difference_radians) < 1e-8
    assert result.simultaneity["1h"] == optical_t.size
