"""TESS temporal/activity context utilities.

The module reports photometric periodicity and cross-epoch coherence. It does
not classify a transit signal as a confirmed planet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .periodogram import PeriodogramResult, generalized_lomb_scargle
from .timeseries import SinusoidFit, fit_sinusoid, wrapped_phase_difference


@dataclass(frozen=True)
class TemporalCoherence:
    period_days: float
    control: SinusoidFit
    test: SinusoidFit
    amplitude_ratio: float
    phase_difference_radians: float


def quality_normalize(
    time: Iterable[float],
    flux: Iterable[float],
    flux_error: Iterable[float],
    quality: Iterable[int],
    *,
    accepted_quality: int = 0,
    sigma: float = 7.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Apply an explicit TESS quality rule and return relative flux in ppm."""
    t = np.asarray(time, dtype=float)
    f = np.asarray(flux, dtype=float)
    e = np.asarray(flux_error, dtype=float)
    q = np.asarray(quality, dtype=int)
    if not (t.shape == f.shape == e.shape == q.shape and t.ndim == 1):
        raise ValueError("time/flux/error/quality must be matching 1D arrays")
    mask = np.isfinite(t) & np.isfinite(f) & np.isfinite(e) & (e > 0) & (q == accepted_quality)
    if np.count_nonzero(mask) < 20:
        raise ValueError("fewer than 20 cadences pass the quality rule")
    t, f, e = t[mask], f[mask], e[mask]
    median = float(np.median(f))
    relative = (f / median - 1.0) * 1e6
    relative_error = e / abs(median) * 1e6
    centre = float(np.median(relative))
    mad = 1.4826 * float(np.median(np.abs(relative - centre)))
    keep = np.ones_like(relative, dtype=bool) if mad == 0 else np.abs(relative - centre) <= sigma * mad
    accepted_indices = np.flatnonzero(mask)[keep]
    return t[keep], relative[keep], relative_error[keep], accepted_indices


def time_bin(
    time: Iterable[float],
    value: Iterable[float],
    error: Iterable[float],
    *,
    width_minutes: float = 30.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = np.asarray(time, dtype=float)
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    if width_minutes <= 0 or not (t.shape == y.shape == e.shape):
        raise ValueError("invalid bin width or mismatched arrays")
    key = np.floor((t - np.min(t)) / (float(width_minutes) / 1440.0)).astype(int)
    rows = []
    for label in np.unique(key):
        mask = key == label
        weights = 1.0 / np.square(e[mask])
        rows.append(
            (
                float(np.average(t[mask], weights=weights)),
                float(np.average(y[mask], weights=weights)),
                float(np.sqrt(1.0 / np.sum(weights))),
            )
        )
    columns = np.asarray(rows, dtype=float)
    return columns[:, 0], columns[:, 1], columns[:, 2]


def activity_periodogram(
    time: Iterable[float],
    relative_flux_ppm: Iterable[float],
    error_ppm: Iterable[float],
    *,
    min_period_days: float = 2.0,
    max_period_days: float = 30.0,
) -> PeriodogramResult:
    t = np.asarray(time, dtype=float)
    upper = min(float(max_period_days), float(np.ptp(t)) * 0.8)
    return generalized_lomb_scargle(
        t,
        relative_flux_ppm,
        error_ppm,
        min_period=min_period_days,
        max_period=upper,
    )


def temporal_coherence(
    control_time,
    control_flux,
    control_error,
    test_time,
    test_flux,
    test_error,
    *,
    period_days: float,
) -> TemporalCoherence:
    control = fit_sinusoid(control_time, control_flux, control_error, period_days)
    test = fit_sinusoid(test_time, test_flux, test_error, period_days)
    ratio = np.nan if control.semi_amplitude == 0 else test.semi_amplitude / control.semi_amplitude
    return TemporalCoherence(
        period_days=float(period_days),
        control=control,
        test=test,
        amplitude_ratio=float(ratio),
        phase_difference_radians=wrapped_phase_difference(
            test.phase_radians, control.phase_radians
        ),
    )
