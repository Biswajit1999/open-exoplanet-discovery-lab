"""Generalized Lomb-Scargle and observing-window diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from astropy.timeseries import LombScargle


@dataclass(frozen=True)
class PeriodogramResult:
    period: np.ndarray
    power: np.ndarray
    best_period: float
    best_power: float
    false_alarm_probability: float


def generalized_lomb_scargle(
    time: Iterable[float],
    value: Iterable[float],
    error: Iterable[float],
    *,
    min_period: float,
    max_period: float,
    samples_per_peak: int = 12,
) -> PeriodogramResult:
    t = np.asarray(time, dtype=float)
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    mask = np.isfinite(t) & np.isfinite(y) & np.isfinite(e) & (e > 0)
    t, y, e = t[mask], y[mask], e[mask]
    if t.size < 5:
        raise ValueError("at least five valid measurements are required")
    if not (0 < min_period < max_period):
        raise ValueError("require 0 < min_period < max_period")

    ls = LombScargle(t, y, dy=e, fit_mean=True, center_data=True)
    frequency, power = ls.autopower(
        minimum_frequency=1.0 / max_period,
        maximum_frequency=1.0 / min_period,
        samples_per_peak=samples_per_peak,
    )
    index = int(np.nanargmax(power))
    best_power = float(power[index])
    try:
        fap = float(ls.false_alarm_probability(best_power))
    except Exception:
        fap = float("nan")
    return PeriodogramResult(
        period=1.0 / frequency,
        power=power,
        best_period=float(1.0 / frequency[index]),
        best_power=best_power,
        false_alarm_probability=fap,
    )


def spectral_window(
    time: Iterable[float],
    *,
    min_period: float,
    max_period: float,
    n_frequency: int = 5000,
) -> tuple[np.ndarray, np.ndarray]:
    """Return period and normalized spectral-window power."""
    t = np.asarray(time, dtype=float)
    t = t[np.isfinite(t)]
    if t.size < 2:
        raise ValueError("at least two finite times are required")
    if not (0 < min_period < max_period):
        raise ValueError("require 0 < min_period < max_period")
    frequency = np.linspace(1.0 / max_period, 1.0 / min_period, int(n_frequency))
    phase = -2j * np.pi * frequency[:, None] * (t[None, :] - np.min(t))
    power = np.abs(np.mean(np.exp(phase), axis=1)) ** 2
    return 1.0 / frequency, power
