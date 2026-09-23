"""Period-search and observing-window diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from astropy.timeseries import LombScargle


@dataclass(frozen=True)
class PeriodogramResult:
    period: np.ndarray
    power: np.ndarray
    best_period: float
    best_power: float
    false_alarm_probability: float


def frequency_grid(time, *, min_period: float, max_period: float, samples_per_peak: float = 8.0):
    t = np.asarray(time, dtype=float)
    if t.ndim != 1 or len(t) < 3 or not np.isfinite(t).all():
        raise ValueError("time must contain at least three finite values")
    if not (0 < min_period < max_period):
        raise ValueError("require 0 < min_period < max_period")
    baseline = float(np.ptp(t))
    if baseline <= 0:
        raise ValueError("time baseline must be positive")
    fmin, fmax = 1.0 / max_period, 1.0 / min_period
    df = 1.0 / (samples_per_peak * baseline)
    n = max(32, int(np.ceil((fmax - fmin) / df)) + 1)
    return np.linspace(fmin, fmax, n)


def gls(time, values, errors, *, min_period: float, max_period: float, samples_per_peak: float = 8.0):
    t = np.asarray(time, dtype=float)
    y = np.asarray(values, dtype=float)
    e = np.asarray(errors, dtype=float)
    if not (t.shape == y.shape == e.shape and t.ndim == 1 and len(t) >= 3):
        raise ValueError("time, values and errors must be matching 1D arrays")
    if np.any(e <= 0) or not np.isfinite(np.r_[t, y, e]).all():
        raise ValueError("all inputs must be finite and errors > 0")
    freq = frequency_grid(
        t,
        min_period=min_period,
        max_period=max_period,
        samples_per_peak=samples_per_peak,
    )
    ls = LombScargle(t, y, e, fit_mean=True, center_data=True)
    power = ls.power(freq, normalization="standard")
    idx = int(np.nanargmax(power))
    fap = float(ls.false_alarm_probability(power[idx], method="baluev"))
    return PeriodogramResult(
        period=1.0 / freq,
        power=np.asarray(power),
        best_period=float(1.0 / freq[idx]),
        best_power=float(power[idx]),
        false_alarm_probability=fap,
    )


def spectral_window(time, frequency):
    """Return |sum exp(-2 pi i f t)|^2 / N^2 for cadence diagnostics."""
    t = np.asarray(time, dtype=float)
    f = np.asarray(frequency, dtype=float)
    if t.ndim != 1 or f.ndim != 1 or len(t) == 0:
        raise ValueError("time and frequency must be non-empty 1D arrays")
    phase = np.exp(-2j * np.pi * f[:, None] * (t[None, :] - np.mean(t)))
    return np.abs(np.mean(phase, axis=1)) ** 2
