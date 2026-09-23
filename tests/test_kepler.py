import numpy as np

from exolab.kepler import keplerian_rv, solve_eccentric_anomaly


def test_kepler_equation_residual_is_small():
    m = np.linspace(0.0, 2.0 * np.pi, 100)
    e = 0.62
    E = solve_eccentric_anomaly(m, e)
    residual = E - e * np.sin(E) - np.mod(m, 2.0 * np.pi)
    assert np.max(np.abs(residual)) < 1e-10


def test_circular_keplerian_has_requested_peak_to_peak():
    t = np.linspace(0.0, 10.0, 10000)
    rv = keplerian_rv(t, period=10.0, semi_amplitude=3.0, eccentricity=0.0)
    assert np.isclose(np.ptp(rv), 6.0, atol=1e-5)
