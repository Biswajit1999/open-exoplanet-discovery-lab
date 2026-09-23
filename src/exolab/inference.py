"""Small model-comparison utilities used across work packages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.optimize import minimize_scalar


def gaussian_log_likelihood(
    residual: Iterable[float],
    error: Iterable[float],
    *,
    jitter: float = 0.0,
) -> float:
    r = np.asarray(residual, dtype=float)
    e = np.asarray(error, dtype=float)
    mask = np.isfinite(r) & np.isfinite(e) & (e > 0)
    r, e = r[mask], e[mask]
    if r.size == 0:
        raise ValueError("no valid residuals")
    if jitter < 0:
        raise ValueError("jitter must be non-negative")
    variance = np.square(e) + float(jitter) ** 2
    return float(-0.5 * np.sum(np.square(r) / variance + np.log(2.0 * np.pi * variance)))


@dataclass(frozen=True)
class JitterFit:
    jitter: float
    log_likelihood: float


def fit_white_jitter(
    residual: Iterable[float],
    error: Iterable[float],
    *,
    upper: float | None = None,
) -> JitterFit:
    r = np.asarray(residual, dtype=float)
    e = np.asarray(error, dtype=float)
    mask = np.isfinite(r) & np.isfinite(e) & (e > 0)
    r, e = r[mask], e[mask]
    if r.size < 2:
        raise ValueError("at least two residuals are required")
    if upper is None:
        upper = max(10.0 * float(np.std(r)), 10.0 * float(np.median(e)), 1.0)
    objective = lambda j: -gaussian_log_likelihood(r, e, jitter=float(j))
    fit = minimize_scalar(objective, bounds=(0.0, float(upper)), method="bounded")
    return JitterFit(jitter=float(fit.x), log_likelihood=float(-fit.fun))


def bic(log_likelihood: float, n_parameters: int, n_observations: int) -> float:
    if n_parameters < 0 or n_observations <= 0:
        raise ValueError("invalid model dimensions")
    return float(n_parameters * np.log(n_observations) - 2.0 * log_likelihood)


def aicc(log_likelihood: float, n_parameters: int, n_observations: int) -> float:
    k = int(n_parameters)
    n = int(n_observations)
    if k < 0 or n <= k + 1:
        raise ValueError("AICc requires n > k + 1")
    aic = 2.0 * k - 2.0 * float(log_likelihood)
    return float(aic + (2.0 * k * (k + 1)) / (n - k - 1))
