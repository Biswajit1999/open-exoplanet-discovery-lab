import numpy as np

from exolab.periodogram import gls, spectral_window


def test_gls_finds_injected_period():
    rng = np.random.default_rng(11)
    t = np.sort(rng.uniform(0, 150, 180))
    p = 12.4
    err = np.full_like(t, 0.2)
    y = 2.0 * np.sin(2 * np.pi * t / p + 0.2) + rng.normal(0, err)
    result = gls(t, y, err, min_period=2, max_period=50)
    assert abs(result.best_period / p - 1) < 0.02
    assert result.false_alarm_probability < 1e-6


def test_window_normalization_at_zero():
    t = np.arange(6.0)
    w = spectral_window(t, np.array([0.0, 0.1]))
    assert np.isclose(w[0], 1.0)
    assert np.all((w >= 0) & (w <= 1.0 + 1e-12))
