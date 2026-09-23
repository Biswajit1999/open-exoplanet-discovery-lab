"""Reproducibility statistics for repeated atmospheric measurements."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize_scalar


@dataclass(frozen=True)
class RandomEffectsResult:
    mean: float
    mean_error: float
    extra_sigma: float
    reduced_chi2: float
    n: int


def _profile_nll(tau: float, y: np.ndarray, e: np.ndarray) -> float:
    var = e**2 + tau**2
    w = 1.0 / var
    mu = np.sum(w * y) / np.sum(w)
    return float(0.5 * np.sum(np.log(var) + (y - mu) ** 2 / var))


def random_effects_mean(values, errors, *, max_extra_sigma: float | None = None) -> RandomEffectsResult:
    """Estimate a common mean plus non-negative between-measurement scatter.

    The extra-scatter term is a profile-likelihood estimate. It is an empirical
    reproducibility scale, not automatically an astrophysical variability term.
    """
    y = np.asarray(values, dtype=float)
    e = np.asarray(errors, dtype=float)
    if y.ndim != 1 or y.shape != e.shape or len(y) < 2:
        raise ValueError("values/errors must be matching 1D arrays with n >= 2")
    if np.any(e <= 0) or not np.isfinite(np.r_[y, e]).all():
        raise ValueError("measurements must be finite and errors > 0")
    spread = max(float(np.ptp(y)), float(np.max(e)))
    upper = float(max_extra_sigma) if max_extra_sigma is not None else max(1e-12, 10.0 * spread)
    if upper <= 0:
        raise ValueError("max_extra_sigma must be positive")
    opt = minimize_scalar(
        lambda tau: _profile_nll(float(tau), y, e),
        bounds=(0.0, upper),
        method="bounded",
        options={"xatol": max(1e-12, upper * 1e-10)},
    )
    tau = max(0.0, float(opt.x))
    var = e**2 + tau**2
    w = 1.0 / var
    mu = float(np.sum(w * y) / np.sum(w))
    mu_err = float(np.sqrt(1.0 / np.sum(w)))
    dof = max(1, len(y) - 1)
    rchi2 = float(np.sum((y - mu) ** 2 / var) / dof)
    return RandomEffectsResult(mu, mu_err, tau, rchi2, len(y))
