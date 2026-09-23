import numpy as np

from exolab.nuisance import group_demean_sinusoid_transfer, weighted_group_demean


def test_weighted_group_demean_removes_each_group_mean():
    y = np.array([1.0, 3.0, 10.0, 14.0])
    e = np.ones(4)
    g = np.array(["a", "a", "b", "b"])
    residual = weighted_group_demean(y, e, g)
    assert np.isclose(residual[:2].mean(), 0.0)
    assert np.isclose(residual[2:].mean(), 0.0)


def test_group_demean_preserves_short_period_better_than_long_period():
    t = np.concatenate([np.linspace(0, 20, 40), np.linspace(200, 220, 40)])
    e = np.full(t.size, 0.5)
    g = np.array(["run1"] * 40 + ["run2"] * 40)
    short = group_demean_sinusoid_transfer(t, e, g, 5.0)
    long = group_demean_sinusoid_transfer(t, e, g, 500.0)
    assert short.median_ratio > long.median_ratio
    assert 0.0 <= long.worst_phase_ratio <= long.best_phase_ratio
