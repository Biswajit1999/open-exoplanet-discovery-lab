import numpy as np

from exolab.tess import quality_normalize, temporal_coherence, time_bin


def test_quality_normalize_preserves_explicit_indices():
    time = np.arange(40.0)
    flux = np.ones(40)
    error = np.full(40, 0.001)
    quality = np.zeros(40, dtype=int)
    quality[[3, 7]] = 1
    t, relative, relative_error, indices = quality_normalize(
        time, flux, error, quality
    )
    assert len(t) == 38
    assert 3 not in indices and 7 not in indices
    assert np.allclose(relative, 0)
    assert np.all(relative_error > 0)


def test_time_bin_and_temporal_coherence():
    period = 8.2
    t1 = np.linspace(0, 25, 500)
    t2 = np.linspace(100, 125, 500)
    e = np.full(500, 0.2)
    y1 = 3 * np.sin(2 * np.pi * t1 / period + 0.4)
    y2 = 2 * np.sin(2 * np.pi * t2 / period + 0.4)
    result = temporal_coherence(t1, y1, e, t2, y2, e, period_days=period)
    assert np.isclose(result.amplitude_ratio, 2 / 3, atol=1e-8)
    assert abs(result.phase_difference_radians) < 1e-8
    tb, yb, eb = time_bin(t1, y1, e, width_minutes=180)
    assert len(tb) < len(t1)
    assert tb.shape == yb.shape == eb.shape
