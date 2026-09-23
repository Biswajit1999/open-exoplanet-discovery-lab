"""Numerical primitives for heterogeneous astronomical time series."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np


def _vectors(
    time: Iterable[float],
    value: Iterable[float],
    error: Iterable[float] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = np.asarray(time, dtype=float)
    y = np.asarray(value, dtype=float)
    if t.ndim != 1 or y.ndim != 1 or t.size != y.size:
        raise ValueError("time and value must be equal-length one-dimensional arrays")
    if error is None:
        e = np.ones_like(y)
    else:
        e = np.asarray(error, dtype=float)
        if e.shape != y.shape:
            raise ValueError("error must match value")
    mask = np.isfinite(t) & np.isfinite(y) & np.isfinite(e) & (e > 0)
    if np.count_nonzero(mask) < 3:
        raise ValueError("at least three finite measurements with positive errors are required")
    return t[mask], y[mask], e[mask]


def weighted_mean(value: Iterable[float], error: Iterable[float]) -> float:
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    if y.shape != e.shape or y.ndim != 1:
        raise ValueError("value and error must be equal-length one-dimensional arrays")
    mask = np.isfinite(y) & np.isfinite(e) & (e > 0)
    if not np.any(mask):
        raise ValueError("no finite values with positive errors")
    w = 1.0 / np.square(e[mask])
    return float(np.sum(w * y[mask]) / np.sum(w))


def weighted_rms(value: Iterable[float], error: Iterable[float]) -> float:
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    mu = weighted_mean(y, e)
    mask = np.isfinite(y) & np.isfinite(e) & (e > 0)
    w = 1.0 / np.square(e[mask])
    return float(np.sqrt(np.sum(w * np.square(y[mask] - mu)) / np.sum(w)))


@dataclass(frozen=True)
class SinusoidFit:
    period: float
    semi_amplitude: float
    semi_amplitude_error: float
    phase_radians: float
    phase_error_radians: float
    chi2: float
    dof: int
    offset: float
    trend_per_day: float
    group_offsets: dict[str, float]
    model: np.ndarray
    residuals: np.ndarray


def fit_sinusoid(
    time: Iterable[float],
    value: Iterable[float],
    error: Iterable[float],
    period: float,
    *,
    groups: Iterable[str] | None = None,
    include_trend: bool = False,
) -> SinusoidFit:
    """Weighted least-squares circular signal with optional group offsets.

    The model is K*sin(2*pi*t/P + phi), plus an intercept, optional linear
    trend, and optional offsets relative to the first sorted group.
    """
    if not np.isfinite(period) or period <= 0:
        raise ValueError("period must be positive and finite")
    t0, y0, e0 = _vectors(time, value, error)

    if groups is None:
        g = np.array(["all"] * t0.size, dtype=object)
    else:
        raw_t = np.asarray(time, dtype=float)
        raw_y = np.asarray(value, dtype=float)
        raw_e = np.asarray(error, dtype=float)
        raw_g = np.asarray(list(groups), dtype=object)
        if raw_g.shape != raw_t.shape:
            raise ValueError("groups must match time")
        mask = np.isfinite(raw_t) & np.isfinite(raw_y) & np.isfinite(raw_e) & (raw_e > 0)
        g = raw_g[mask]

    omega = 2.0 * np.pi / period
    tref = float(np.average(t0, weights=1.0 / np.square(e0)))
    columns = [
        np.sin(omega * t0),
        np.cos(omega * t0),
        np.ones_like(t0),
    ]
    names = ["sin", "cos", "offset"]
    if include_trend:
        columns.append(t0 - tref)
        names.append("trend")

    levels = sorted({str(x) for x in g})
    reference = levels[0]
    for level in levels[1:]:
        columns.append((g.astype(str) == level).astype(float))
        names.append(f"group:{level}")

    X = np.column_stack(columns)
    w = 1.0 / np.square(e0)
    xtwx = X.T @ (w[:, None] * X)
    xtwy = X.T @ (w * y0)
    try:
        covariance = np.linalg.inv(xtwx)
    except np.linalg.LinAlgError:
        covariance = np.linalg.pinv(xtwx)
    beta = covariance @ xtwy
    model = X @ beta
    residuals = y0 - model
    chi2 = float(np.sum(np.square(residuals / e0)))
    dof = int(max(0, t0.size - X.shape[1]))

    a = float(beta[0])
    b = float(beta[1])
    amplitude = float(math.hypot(a, b))
    phase = float(math.atan2(b, a))
    cov_ab = covariance[:2, :2]
    if amplitude > 0:
        grad_k = np.array([a / amplitude, b / amplitude])
        grad_phi = np.array([-b / amplitude**2, a / amplitude**2])
        k_var = float(grad_k @ cov_ab @ grad_k)
        phi_var = float(grad_phi @ cov_ab @ grad_phi)
    else:
        k_var = float(cov_ab[0, 0] + cov_ab[1, 1])
        phi_var = float("inf")

    offset = float(beta[names.index("offset")])
    group_offsets = {reference: offset}
    for level in levels[1:]:
        group_offsets[level] = offset + float(beta[names.index(f"group:{level}")])

    trend = float(beta[names.index("trend")]) if include_trend else 0.0
    return SinusoidFit(
        period=float(period),
        semi_amplitude=amplitude,
        semi_amplitude_error=float(np.sqrt(max(0.0, k_var))),
        phase_radians=phase,
        phase_error_radians=float(np.sqrt(max(0.0, phi_var))),
        chi2=chi2,
        dof=dof,
        offset=offset,
        trend_per_day=trend,
        group_offsets=group_offsets,
        model=model,
        residuals=residuals,
    )


def wrapped_phase_difference(a: float, b: float) -> float:
    """Return a-b wrapped to [-pi, pi)."""
    return float((a - b + np.pi) % (2.0 * np.pi) - np.pi)
