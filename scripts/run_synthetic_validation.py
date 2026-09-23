"""Run deterministic end-to-end validations of the core science primitives."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from exolab.atmosphere import random_effects_mean
from exolab.chromatic import compare_bands
from exolab.periodogram import gls
from exolab.rv import fit_shared_sinusoid


def main() -> int:
    out = Path("outputs/validation")
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260923)

    t = np.sort(rng.uniform(0, 220, 240))
    p, k, phase = 23.7, 1.65, 0.42
    err = np.full_like(t, 0.25)
    rv = k * np.sin(2 * np.pi * (t - np.median(t)) / p + phase) + rng.normal(0, err)
    periodogram = gls(t, rv, err, min_period=2, max_period=100)
    fit = fit_shared_sinusoid(t, rv, err, period=p)

    t2 = np.sort(rng.uniform(0, 220, 180))
    err2 = np.full_like(t2, 0.3)
    rv2 = k * np.sin(2 * np.pi * (t2 - np.median(t2)) / p + phase) + rng.normal(0, err2)
    chromatic = compare_bands(t, rv, err, t2, rv2, err2, period=p)

    repeated = random_effects_mean([96.0, 101.0, 92.0, 106.0], [2.0, 2.0, 2.0, 2.0])

    result = {
        "seed": 20260923,
        "rv_injection": {
            "period_days": p,
            "k": k,
            "gls_best_period_days": periodogram.best_period,
            "gls_fap": periodogram.false_alarm_probability,
            "fit_k": fit.semi_amplitude,
        },
        "achromatic_control": {
            "k_ratio": chromatic.amplitude_ratio,
            "phase_delta_rad": chromatic.phase_delta,
        },
        "repeated_measurement_control": {
            "extra_sigma": repeated.extra_sigma,
            "reduced_chi2": repeated.reduced_chi2,
        },
        "interpretation": "Synthetic validation only; these values are not astrophysical measurements.",
    }
    (out / "synthetic_validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    assert abs(periodogram.best_period / p - 1.0) < 0.03
    assert abs(fit.semi_amplitude - k) < 0.12
    assert abs(chromatic.amplitude_ratio - 1.0) < 0.2
    assert repeated.extra_sigma > 0
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
