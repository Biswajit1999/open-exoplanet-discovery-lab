"""Synthetic end-to-end demonstration used by tests and the CLI."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .injection import inject_box_transit
from .report import write_candidate_report
from .search import search_bls
from .vetting import vet_signal


def synthetic_lightcurve(seed: int = 7) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    time = np.arange(0.0, 27.0, 10.0 / (24 * 60))
    error = np.full_like(time, 4e-4)
    variability = 7e-4 * np.sin(2 * np.pi * time / 5.3)
    flux = 1.0 + variability + rng.normal(0.0, error)
    flux = inject_box_transit(time, flux, 3.2, 1.1, 2.0 / 24.0, 0.004)
    return time, flux, error


def run_demo(output: str | Path) -> tuple[object, object, tuple[Path, Path]]:
    time, flux, error = synthetic_lightcurve()
    signal, _ = search_bls(
        time,
        flux,
        error,
        minimum_period=1.0,
        maximum_period=8.0,
        durations_hours=(1.5, 2.0, 2.5),
    )
    vetting = vet_signal(time, flux, signal, error)
    paths = write_candidate_report(output, "Synthetic training target", time, flux, signal, vetting)
    return signal, vetting, paths
