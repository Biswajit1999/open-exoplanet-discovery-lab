"""Reproducibility statistics for repeated atmospheric measurements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.optimize import brentq


@dataclass(frozen=True)
class RandomEffectsEstimate:
    mean: float
    mean_error: float
    extra_scatter: float
    chi2: float
    dof: int
    reduced_chi2: float


@dataclass(frozen=True)
class RandomEffectsResult:
    """Backward-compatible name and field layout for release 0.2 clients."""

    mean: float
    mean_error: float
    extra_sigma: float
    reduced_chi2: float
    n: int


@dataclass(frozen=True)
class BandMean:
    """Inverse-variance mean for a stated wavelength interval."""

    mean: float
    error: float
    n_bins: int
    wavelength_min: float
    wavelength_max: float


def weighted_band_mean(
    wavelength: Iterable[float],
    value: Iterable[float],
    error: Iterable[float],
    wavelength_min: float,
    wavelength_max: float,
) -> BandMean:
    """Summarise independent spectral bins inside an explicit common band.

    This descriptive calculation cannot correct for unpublished spectral
    covariance. Callers must retain that limitation in result metadata.
    """
    x = np.asarray(wavelength, dtype=float)
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    if not (x.shape == y.shape == e.shape):
        raise ValueError("wavelength, value, and error must have matching shapes")
    mask = (
        np.isfinite(x)
        & np.isfinite(y)
        & np.isfinite(e)
        & (e > 0)
        & (x >= wavelength_min)
        & (x <= wavelength_max)
    )
    if not np.any(mask):
        raise ValueError("no valid bins fall inside the requested wavelength interval")
    weight = 1.0 / np.square(e[mask])
    return BandMean(
        mean=float(np.sum(weight * y[mask]) / np.sum(weight)),
        error=float(np.sqrt(1.0 / np.sum(weight))),
        n_bins=int(mask.sum()),
        wavelength_min=float(wavelength_min),
        wavelength_max=float(wavelength_max),
    )


def _weighted_location(y: np.ndarray, sigma: np.ndarray, tau: float) -> tuple[float, float]:
    variance = np.square(sigma) + tau**2
    w = 1.0 / variance
    mean = float(np.sum(w * y) / np.sum(w))
    mean_error = float(np.sqrt(1.0 / np.sum(w)))
    return mean, mean_error


def estimate_extra_scatter(
    value: Iterable[float],
    error: Iterable[float],
) -> RandomEffectsEstimate:
    """Estimate an additional independent scatter term.

    tau is the non-negative value that brings chi2/dof to unity when possible.
    This is a transparent reproducibility diagnostic, not a substitute for a
    full covariance model.
    """
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    mask = np.isfinite(y) & np.isfinite(e) & (e > 0)
    y, e = y[mask], e[mask]
    if y.size < 2:
        raise ValueError("at least two independent measurements are required")
    dof = int(y.size - 1)

    def objective(tau: float) -> float:
        mean, _ = _weighted_location(y, e, tau)
        chi2 = float(np.sum(np.square(y - mean) / (np.square(e) + tau**2)))
        return chi2 / dof - 1.0

    if objective(0.0) <= 0:
        tau = 0.0
    else:
        upper = max(float(np.std(y, ddof=1)), float(np.max(e)), 1e-12)
        while objective(upper) > 0 and upper < 1e12:
            upper *= 2.0
        tau = float(brentq(objective, 0.0, upper))

    mean, mean_error = _weighted_location(y, e, tau)
    chi2 = float(np.sum(np.square(y - mean) / (np.square(e) + tau**2)))
    return RandomEffectsEstimate(
        mean=mean,
        mean_error=mean_error,
        extra_scatter=tau,
        chi2=chi2,
        dof=dof,
        reduced_chi2=chi2 / dof,
    )


def standardized_pairwise_differences(
    value: Iterable[float],
    error: Iterable[float],
) -> np.ndarray:
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    mask = np.isfinite(y) & np.isfinite(e) & (e > 0)
    y, e = y[mask], e[mask]
    values: list[float] = []
    for i in range(y.size):
        for j in range(i + 1, y.size):
            values.append(float((y[i] - y[j]) / np.hypot(e[i], e[j])))
    return np.asarray(values, dtype=float)


def random_effects_mean(
    values: Iterable[float],
    errors: Iterable[float],
    *,
    max_extra_sigma: float | None = None,
) -> RandomEffectsResult:
    """Compatibility wrapper around :func:`estimate_extra_scatter`.

    ``max_extra_sigma`` is retained for API compatibility. The transparent
    chi-square estimator does not need an optimisation bound; a fitted value
    above the caller's bound is clipped only when the bound is supplied.
    """
    y = np.asarray(values, dtype=float)
    estimate = estimate_extra_scatter(y, errors)
    tau = estimate.extra_scatter
    if max_extra_sigma is not None:
        if max_extra_sigma <= 0:
            raise ValueError("max_extra_sigma must be positive")
        tau = min(tau, float(max_extra_sigma))
    return RandomEffectsResult(
        mean=estimate.mean,
        mean_error=estimate.mean_error,
        extra_sigma=tau,
        reduced_chi2=estimate.reduced_chi2,
        n=int(np.isfinite(y).sum()),
    )
