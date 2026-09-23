import numpy as np

from exolab.activity import weighted_activity_regression


def test_activity_regression_recovers_linear_nuisance():
    indicator = np.linspace(-2.0, 2.0, 60)
    rv = 4.0 + 0.75 * indicator + 0.1 * np.sin(np.arange(indicator.size))
    error = np.full(indicator.size, 0.3)
    result = weighted_activity_regression(rv, error, indicator)

    assert np.isclose(result.slope, 0.75, atol=0.02)
    assert result.corrected_wrms < result.raw_wrms
    assert result.slope_error > 0
