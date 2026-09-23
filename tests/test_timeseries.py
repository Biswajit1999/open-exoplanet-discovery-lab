import numpy as np

from exolab.timeseries import fit_sinusoid, weighted_mean, weighted_rms, wrapped_phase_difference


def test_weighted_mean_and_rms():
    y = np.array([1.0, 2.0, 3.0])
    e = np.ones(3)
    assert weighted_mean(y, e) == 2.0
    assert np.isclose(weighted_rms(y, e), np.sqrt(2.0 / 3.0))


def test_grouped_sinusoid_recovers_signal_and_offsets():
    t = np.linspace(0.0, 80.0, 200)
    period = 19.7
    k = 3.2
    phase = 0.43
    groups = np.where(np.arange(t.size) < 100, "era0", "era1")
    offsets = np.where(groups == "era0", 5.0, 7.5)
    y = offsets + k * np.sin(2.0 * np.pi * t / period + phase)
    e = np.full(t.size, 0.4)

    fit = fit_sinusoid(t, y, e, period, groups=groups)

    assert np.isclose(fit.semi_amplitude, k, atol=1e-9)
    assert abs(wrapped_phase_difference(fit.phase_radians, phase)) < 1e-9
    assert np.isclose(fit.group_offsets["era0"], 5.0, atol=1e-9)
    assert np.isclose(fit.group_offsets["era1"], 7.5, atol=1e-9)
    assert np.max(np.abs(fit.residuals)) < 1e-9
