import numpy as np

from exolab.atmosphere import estimate_extra_scatter, standardized_pairwise_differences


def test_consistent_measurements_need_no_extra_scatter():
    result = estimate_extra_scatter([100.0, 100.2, 99.9, 100.1], [1.0, 1.0, 1.0, 1.0])
    assert result.extra_scatter == 0.0
    assert result.reduced_chi2 < 1.0


def test_inconsistent_measurements_infer_positive_extra_scatter():
    result = estimate_extra_scatter([90.0, 110.0, 95.0, 115.0], [1.0, 1.0, 1.0, 1.0])
    assert result.extra_scatter > 0
    assert np.isclose(result.reduced_chi2, 1.0, atol=1e-7)
    assert standardized_pairwise_differences([90.0, 110.0], [1.0, 1.0]).size == 1
