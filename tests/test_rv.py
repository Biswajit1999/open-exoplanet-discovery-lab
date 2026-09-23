import numpy as np

from exolab.rv import fit_instrument_offsets, fit_shared_sinusoid, weighted_mean


def test_weighted_mean():
    mean, err = weighted_mean([1.0, 3.0], [1.0, 1.0])
    assert mean == 2.0
    assert np.isclose(err, 1 / np.sqrt(2))


def test_shared_sinusoid_recovers_amplitude_with_offsets():
    rng = np.random.default_rng(3)
    t = np.linspace(0, 120, 160)
    period = 17.25
    k = 2.4
    inst = np.where(np.arange(len(t)) % 2 == 0, "A", "B")
    offsets = np.where(inst == "A", 4.0, -2.0)
    err = np.full_like(t, 0.15)
    y = k * np.sin(2 * np.pi * (t - np.median(t)) / period + 0.35) + offsets
    y += rng.normal(0, err)

    fit = fit_shared_sinusoid(t, y, err, period=period, instrument=inst)
    assert abs(fit.semi_amplitude - k) < 0.08
    assert fit.dof > 0
    assert np.std(fit.residuals) < 0.25


def test_instrument_offsets():
    t = np.arange(10.0)
    inst = np.array(["A"] * 5 + ["B"] * 5)
    rv = np.array([2.0] * 5 + [-3.0] * 5)
    err = np.ones(10)
    result = fit_instrument_offsets(t, rv, err, inst)
    assert np.isclose(result["offsets"]["A"], 2.0)
    assert np.isclose(result["offsets"]["B"], -3.0)
