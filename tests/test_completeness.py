import numpy as np

from exolab.completeness import classify_period_recovery, inject_and_recover


def test_period_recovery_classification():
    assert classify_period_recovery(10.05, 10.0)[0]
    recovered, mode = classify_period_recovery(20.0, 10.0)
    assert recovered and mode == "harmonic:2"
    assert not classify_period_recovery(13.0, 10.0)[0]


def test_strong_injected_signal_is_recovered():
    rng = np.random.default_rng(42)
    t = np.sort(rng.uniform(0.0, 160.0, 180))
    baseline = np.zeros_like(t)
    error = np.full_like(t, 0.25)
    result = inject_and_recover(
        t,
        baseline,
        error,
        period=17.3,
        semi_amplitude=3.0,
        phase=0.7,
        min_period=2.0,
        max_period=60.0,
        fap_threshold=1e-4,
    )
    assert result.recovered
    assert abs(result.detected_period - 17.3) / 17.3 < 0.02
