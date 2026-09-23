import numpy as np

from exolab.atmosphere import random_effects_mean


def test_consistent_measurements_need_little_extra_scatter():
    values = np.array([100.0, 100.05, 99.95, 100.02])
    errors = np.ones(4)
    result = random_effects_mean(values, errors)
    assert result.extra_sigma < 0.1
    assert abs(result.mean - 100.0) < 0.1


def test_inconsistent_measurements_infer_extra_scatter():
    values = np.array([90.0, 110.0, 92.0, 108.0])
    errors = np.ones(4)
    result = random_effects_mean(values, errors)
    assert result.extra_sigma > 5.0
    assert result.n == 4
