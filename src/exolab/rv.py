"""Transparent radial-velocity fitting primitives.

These functions intentionally implement small, auditable weighted least-squares
models. They provide benchmark fits and validation layers; they do not replace
a full Keplerian inference package.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class SinusoidFit:
    period: float
    semi_amplitude: float
    phase: float
    coefficients: np.ndarray
    covariance: np.ndarray
    model: np.ndarray
    residuals: np.ndarray
    chi2: float
    dof: int


def _arrays(time, rv, err):
    t = np.asarray(time, dtype=float)
    y = np.asarray(rv, dtype=float)
    e = np.asarray(err, dtype=float)
    if not (t.ndim == y.ndim == e.ndim == 1 and len(t) == len(y) == len(e)):
        raise ValueError("time, rv and err must be equal-length 1D arrays")
    if len(t) < 3 or not (np.isfinite(t).all() and np.isfinite(y).all() and np.isfinite(e).all()):
        raise ValueError("inputs must contain at least three finite observations")
    if np.any(e <= 0):
        raise ValueError("all uncertainties must be > 0")
    return t, y, e


def weighted_mean(values, errors) -> tuple[float, float]:
    y = np.asarray(values, dtype=float)
    e = np.asarray(errors, dtype=float)
    if y.shape != e.shape or y.ndim != 1 or len(y) == 0 or np.any(e <= 0):
        raise ValueError("values/errors must be non-empty matching 1D arrays with errors > 0")
    w = 1.0 / e**2
    return float(np.sum(w * y) / np.sum(w)), float(np.sqrt(1.0 / np.sum(w)))


def _instrument_columns(instrument) -> tuple[np.ndarray, list[str]]:
    labels = np.asarray(instrument).astype(str)
    names = sorted(set(labels.tolist()))
    if not names:
        raise ValueError("instrument labels are required")
    design = np.column_stack([(labels == name).astype(float) for name in names])
    return design, names


def fit_shared_sinusoid(
    time,
    rv,
    err,
    *,
    period: float,
    instrument=None,
    include_trend: bool = False,
) -> SinusoidFit:
    """Fit a circular shared-period RV signal plus per-instrument zero points."""
    if period <= 0 or not np.isfinite(period):
        raise ValueError("period must be positive and finite")
    t, y, e = _arrays(time, rv, err)
    tref = float(np.median(t))
    omega = 2.0 * np.pi / float(period)
    columns = [np.sin(omega * (t - tref)), np.cos(omega * (t - tref))]

    if instrument is None:
        columns.append(np.ones_like(t))
    else:
        inst, _ = _instrument_columns(instrument)
        if len(inst) != len(t):
            raise ValueError("instrument must match time length")
        columns.extend(inst[:, i] for i in range(inst.shape[1]))

    if include_trend:
        columns.append(t - tref)

    X = np.column_stack(columns)
    sw = 1.0 / e
    Xw = X * sw[:, None]
    yw = y * sw
    coeff, _, rank, _ = np.linalg.lstsq(Xw, yw, rcond=None)
    if rank < X.shape[1]:
        raise ValueError("design matrix is rank deficient")
    normal = Xw.T @ Xw
    cov = np.linalg.inv(normal)
    model = X @ coeff
    resid = y - model
    chi2 = float(np.sum((resid / e) ** 2))
    a, b = coeff[:2]
    k = float(np.hypot(a, b))
    phase = float(np.arctan2(b, a))
    return SinusoidFit(
        period=float(period),
        semi_amplitude=k,
        phase=phase,
        coefficients=coeff,
        covariance=cov,
        model=model,
        residuals=resid,
        chi2=chi2,
        dof=int(len(y) - X.shape[1]),
    )


def fit_instrument_offsets(time, rv, err, instrument, *, include_trend: bool = False):
    """Fit only per-instrument offsets (and optionally a linear trend)."""
    t, y, e = _arrays(time, rv, err)
    inst, names = _instrument_columns(instrument)
    if len(inst) != len(t):
        raise ValueError("instrument must match time length")
    cols = [inst[:, i] for i in range(inst.shape[1])]
    tref = float(np.median(t))
    if include_trend:
        cols.append(t - tref)
    X = np.column_stack(cols)
    Xw = X / e[:, None]
    yw = y / e
    beta, _, rank, _ = np.linalg.lstsq(Xw, yw, rcond=None)
    if rank < X.shape[1]:
        raise ValueError("design matrix is rank deficient")
    model = X @ beta
    return {
        "instrument_names": names,
        "offsets": {name: float(beta[i]) for i, name in enumerate(names)},
        "trend": float(beta[-1]) if include_trend else None,
        "model": model,
        "residuals": y - model,
        "chi2": float(np.sum(((y - model) / e) ** 2)),
    }
