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


def frequency_grid(
    time: Iterable[float],
    *,
    min_period: float,
    max_period: float,
    samples_per_peak: float = 8.0,
) -> np.ndarray:
    """Return the deterministic frequency grid used by the legacy API."""
    t = np.asarray(time, dtype=float)
    if t.ndim != 1 or t.size < 3 or not np.isfinite(t).all():
        raise ValueError("time must contain at least three finite values")
    if not (0 < min_period < max_period):
        raise ValueError("require 0 < min_period < max_period")
    baseline = float(np.ptp(t))
    if baseline <= 0:
        raise ValueError("time baseline must be positive")
    fmin, fmax = 1.0 / max_period, 1.0 / min_period
    step = 1.0 / (float(samples_per_peak) * baseline)
    size = max(32, int(np.ceil((fmax - fmin) / step)) + 1)
    return np.linspace(fmin, fmax, size)


def gls(
    time: Iterable[float],
    values: Iterable[float],
    errors: Iterable[float],
    *,
    min_period: float,
    max_period: float,
    samples_per_peak: float = 8.0,
) -> PeriodogramResult:
    """Compatibility GLS entry point with an explicit reproducible grid."""
    t = np.asarray(time, dtype=float)
    y = np.asarray(values, dtype=float)
    e = np.asarray(errors, dtype=float)
    if not (t.shape == y.shape == e.shape and t.ndim == 1 and t.size >= 3):
        raise ValueError("time, values and errors must be matching 1D arrays")
    if np.any(e <= 0) or not np.isfinite(np.r_[t, y, e]).all():
        raise ValueError("all inputs must be finite and errors > 0")
    frequency = frequency_grid(
        t,
        min_period=min_period,
        max_period=max_period,
        samples_per_peak=samples_per_peak,
    )
    model = LombScargle(t, y, e, fit_mean=True, center_data=True)
    power = model.power(frequency, normalization="standard")
    index = int(np.nanargmax(power))
    best_power = float(power[index])
    return PeriodogramResult(
        period=1.0 / frequency,
        power=np.asarray(power),
        best_period=float(1.0 / frequency[index]),
        best_power=best_power,
        false_alarm_probability=float(
            model.false_alarm_probability(best_power, method="baluev")
        ),
    )


def spectral_window(
    time: Iterable[float],
    frequency: Iterable[float] | None = None,
    *,
    min_period: float | None = None,
    max_period: float | None = None,
    n_frequency: int = 5000,
) -> tuple[np.ndarray, np.ndarray] | np.ndarray:
    """Return spectral-window power, with both current and legacy signatures."""
    t = np.asarray(time, dtype=float)
    t = t[np.isfinite(t)]
    if t.size < 2:
        raise ValueError("at least two finite times are required")
    if frequency is not None:
        frequencies = np.asarray(frequency, dtype=float)
        if frequencies.ndim != 1 or frequencies.size == 0:
            raise ValueError("frequency must be a non-empty 1D array")
        phase = -2j * np.pi * frequencies[:, None] * (t[None, :] - np.mean(t))
        return np.abs(np.mean(np.exp(phase), axis=1)) ** 2
    if min_period is None or max_period is None or not (0 < min_period < max_period):
        raise ValueError("require 0 < min_period < max_period")
    frequencies = np.linspace(1.0 / max_period, 1.0 / min_period, int(n_frequency))
    phase = -2j * np.pi * frequencies[:, None] * (t[None, :] - np.min(t))
    power = np.abs(np.mean(np.exp(phase), axis=1)) ** 2
    return 1.0 / frequencies, power
