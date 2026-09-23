"""Transparent stellar-activity nuisance diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .timeseries import weighted_rms


@dataclass(frozen=True)
class ActivityRegression:
    intercept: float
    slope: float
    slope_error: float
    raw_wrms: float
    corrected_wrms: float
    residuals: np.ndarray


def weighted_activity_regression(
    rv: Iterable[float],
    rv_error: Iterable[float],
    indicator: Iterable[float],
) -> ActivityRegression:
    y = np.asarray(rv, dtype=float)
    e = np.asarray(rv_error, dtype=float)
    x = np.asarray(indicator, dtype=float)
    if not (y.shape == e.shape == x.shape) or y.ndim != 1:
        raise ValueError("rv, rv_error and indicator must have matching one-dimensional shapes")
    mask = np.isfinite(y) & np.isfinite(e) & np.isfinite(x) & (e > 0)
    y, e, x = y[mask], e[mask], x[mask]
    if y.size < 4 or np.ptp(x) == 0:
        raise ValueError("insufficient variation for activity regression")
    x0 = x - np.average(x, weights=1.0 / np.square(e))
    X = np.column_stack([np.ones_like(x0), x0])
    w = 1.0 / np.square(e)
    normal = X.T @ (w[:, None] * X)
    covariance = np.linalg.pinv(normal)
    beta = covariance @ (X.T @ (w * y))
    model = X @ beta
    residuals = y - model
    return ActivityRegression(
        intercept=float(beta[0]),
        slope=float(beta[1]),
        slope_error=float(np.sqrt(max(0.0, covariance[1, 1]))),
        raw_wrms=weighted_rms(y, e),
        corrected_wrms=weighted_rms(residuals, e),
        residuals=residuals,
    )
