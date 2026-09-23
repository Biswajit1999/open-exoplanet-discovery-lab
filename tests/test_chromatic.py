import numpy as np

from exolab.chromatic import compare_bands, simultaneity_counts


def test_achromatic_signal_has_unity_amplitude_ratio():
    t1 = np.linspace(0, 80, 100)
    t2 = np.linspace(0.3, 80.3, 95)
    p = 9.5
    k = 1.8
    e1 = np.full_like(t1, 0.1)
    e2 = np.full_like(t2, 0.1)
    y1 = k * np.sin(2 * np.pi * (t1 - np.median(t1)) / p + 0.4)
    y2 = k * np.sin(2 * np.pi * (t2 - np.median(t2)) / p + 0.4)
    result = compare_bands(t1, y1, e1, t2, y2, e2, period=p)
    assert abs(result.amplitude_ratio - 1.0) < 1e-6


def test_simultaneity_counts_are_monotonic():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([1.02, 2.2, 4.0])
    counts = simultaneity_counts(a, b, windows_hours=(1, 6, 24))
    assert counts[1.0] <= counts[6.0] <= counts[24.0]
