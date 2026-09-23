"""Generate static validation figures from deterministic synthetic controls."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from exolab.atmosphere import estimate_extra_scatter
from exolab.completeness import run_injection_grid
from exolab.figures import (
    plot_chromatic_amplitudes,
    plot_completeness,
    plot_repeatability,
    plot_rv_timeseries,
)
from exolab.timeseries import fit_sinusoid


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/validation_figures")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(20260923)
    t = np.sort(rng.uniform(0.0, 150.0, 180))
    period = 21.4
    error = np.full(t.size, 0.35)
    groups = np.where(t < 75, "era0", "era1")
    offsets = np.where(groups == "era0", 0.0, 1.6)
    rv = offsets + 2.2 * np.sin(2.0 * np.pi * t / period + 0.3)
    fit = fit_sinusoid(t, rv, error, period, groups=groups)
    plot_rv_timeseries(t, rv, error, groups=groups, title="Synthetic instrument-era validation", path=output / "validation_rv.png")

    completeness = run_injection_grid(
        t,
        np.zeros_like(t),
        error,
        periods=[5.0, 10.0, 20.0, 40.0],
        semi_amplitudes=[0.3, 0.6, 1.2, 2.4],
        phases=np.linspace(0.0, 2.0 * np.pi, 8, endpoint=False),
        min_period=2.0,
        max_period=60.0,
        fap_threshold=0.01,
    )
    completeness.to_csv(output / "validation_completeness.csv", index=False)
    plot_completeness(completeness, path=output / "validation_completeness.png")

    plot_chromatic_amplitudes(
        ["control"],
        [3.0],
        [0.12],
        [2.1],
        [0.14],
        path=output / "validation_chromatic.png",
    )

    values = [95.0, 106.0, 91.0, 109.0]
    errors = [2.0, 2.0, 2.0, 2.0]
    repeat = estimate_extra_scatter(values, errors)
    plot_repeatability(
        ["visit 1", "visit 2", "visit 3", "visit 4"],
        values,
        errors,
        mean=repeat.mean,
        extra_scatter=repeat.extra_scatter,
        path=output / "validation_repeatability.png",
    )

    metrics = pd.DataFrame([{
        "injected_k": 2.2,
        "recovered_k": fit.semi_amplitude,
        "period": period,
        "extra_scatter": repeat.extra_scatter,
    }])
    metrics.to_csv(output / "validation_metrics.csv", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
