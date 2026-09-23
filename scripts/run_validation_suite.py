"""Generate deterministic validation results for the science primitives."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from exolab.activity import weighted_activity_regression
from exolab.atmosphere import estimate_extra_scatter
from exolab.chromatic import compare_fixed_period_signal
from exolab.completeness import inject_and_recover
from exolab.timeseries import fit_sinusoid, wrapped_phase_difference


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/validation")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(20260923)
    t = np.sort(rng.uniform(0.0, 180.0, 240))
    period = 23.7
    k = 2.4
    phase = 0.52
    groups = np.where(t < 90.0, "era0", "era1")
    offset = np.where(groups == "era0", 4.0, 5.7)
    error = np.full(t.size, 0.35)
    y = offset + k * np.sin(2.0 * np.pi * t / period + phase)
    fit = fit_sinusoid(t, y, error, period, groups=groups)

    indicator = np.linspace(-1.0, 1.0, t.size)
    activity_rv = 1.2 * indicator + 0.15 * np.sin(np.arange(t.size))
    activity = weighted_activity_regression(activity_rv, error, indicator)

    nir_t = t + 0.005
    optical_rv = 2.0 + 3.0 * np.sin(2.0 * np.pi * t / period + phase)
    nir_rv = -1.0 + 2.1 * np.sin(2.0 * np.pi * nir_t / period + phase)
    chromatic = compare_fixed_period_signal(
        t, optical_rv, error, nir_t, nir_rv, error, period
    )

    repeatability = estimate_extra_scatter(
        [95.0, 106.0, 91.0, 109.0],
        [2.0, 2.0, 2.0, 2.0],
    )

    recovery = inject_and_recover(
        t,
        np.zeros_like(t),
        error,
        period=period,
        semi_amplitude=3.5,
        phase=phase,
        min_period=2.0,
        max_period=80.0,
        fap_threshold=1e-4,
    )

    checks = {
        "grouped_signal_amplitude": abs(fit.semi_amplitude - k) < 1e-8,
        "grouped_signal_phase": abs(wrapped_phase_difference(fit.phase_radians, phase)) < 1e-8,
        "activity_regression_improves_wrms": activity.corrected_wrms < activity.raw_wrms,
        "chromatic_ratio": abs(chromatic.amplitude_ratio_nir_to_optical - 0.7) < 1e-8,
        "repeatability_detects_extra_scatter": repeatability.extra_scatter > 0,
        "injected_signal_recovered": recovery.recovered,
    }
    payload = {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "metrics": {
            "recovered_k_mps": fit.semi_amplitude,
            "injected_k_mps": k,
            "phase_error_rad": wrapped_phase_difference(fit.phase_radians, phase),
            "activity_raw_wrms": activity.raw_wrms,
            "activity_corrected_wrms": activity.corrected_wrms,
            "nir_to_optical_k_ratio": chromatic.amplitude_ratio_nir_to_optical,
            "extra_scatter": repeatability.extra_scatter,
            "injection_detected_period_days": recovery.detected_period,
            "injection_period_days": period,
            "injection_fap": recovery.fap,
        },
    }
    path = output / "validation_summary.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path.read_text(encoding="utf-8"))
    if payload["status"] != "pass":
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
