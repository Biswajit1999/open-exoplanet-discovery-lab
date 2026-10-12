"""Reproducibility statistics for repeated atmospheric measurements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.optimize import brentq, minimize_scalar


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


@dataclass(frozen=True)
class ThermalRetrieval:
    """One-temperature blackbody fit to an eclipse-depth spectrum."""

    temperature_k: float
    error_minus_k: float
    error_plus_k: float
    lower_status: str
    upper_status: str
    chi2: float
    dof: int
    bic: float
    n_bins: int


def blackbody_eclipse_depth_ppm(
    wavelength_micron: Iterable[float],
    planet_temperature_k: float,
    stellar_temperature_k: float,
    radius_ratio: float,
) -> np.ndarray:
    """Planet/star blackbody flux ratio for a secondary eclipse.

    The Planck prefactor cancels at a common wavelength. This deliberately
    simple forward model does not represent molecular opacity or a stellar
    atmosphere grid.
    """
    wavelength = np.asarray(wavelength_micron, dtype=float)
    if (
        np.any(~np.isfinite(wavelength))
        or np.any(wavelength <= 0)
        or planet_temperature_k <= 0
        or stellar_temperature_k <= 0
        or radius_ratio <= 0
    ):
        raise ValueError("wavelengths, temperatures, and radius ratio must be positive")
    second_radiation_constant_m_k = 1.438776877e-2
    wavelength_m = wavelength * 1e-6
    star_exponent = second_radiation_constant_m_k / (
        wavelength_m * float(stellar_temperature_k)
    )
    planet_exponent = second_radiation_constant_m_k / (
        wavelength_m * float(planet_temperature_k)
    )
    ratio = np.expm1(star_exponent) / np.expm1(planet_exponent)
    return 1e6 * float(radius_ratio) ** 2 * ratio


def fit_blackbody_temperature(
    wavelength_micron: Iterable[float],
    eclipse_depth_ppm: Iterable[float],
    error_ppm: Iterable[float],
    *,
    stellar_temperature_k: float,
    radius_ratio: float,
    temperature_bounds_k: tuple[float, float] = (300.0, 5000.0),
) -> ThermalRetrieval:
    """Profile-likelihood blackbody brightness-temperature retrieval.

    The one-sigma interval uses delta chi-square=1. A bound status is explicit
    when the interval is not bracketed by the stated temperature prior.
    """
    wavelength = np.asarray(wavelength_micron, dtype=float)
    depth = np.asarray(eclipse_depth_ppm, dtype=float)
    error = np.asarray(error_ppm, dtype=float)
    if not (wavelength.shape == depth.shape == error.shape):
        raise ValueError("wavelength, depth, and error must have matching shapes")
    valid = (
        np.isfinite(wavelength)
        & np.isfinite(depth)
        & np.isfinite(error)
        & (wavelength > 0)
        & (error > 0)
    )
    wavelength, depth, error = wavelength[valid], depth[valid], error[valid]
    if wavelength.size < 2:
        raise ValueError("at least two valid spectral points are required")
    lower, upper = map(float, temperature_bounds_k)
    if not 0 < lower < upper:
        raise ValueError("invalid temperature bounds")

    def chi2(temperature: float) -> float:
        model = blackbody_eclipse_depth_ppm(
            wavelength,
            temperature,
            stellar_temperature_k,
            radius_ratio,
        )
        return float(np.sum(np.square((depth - model) / error)))

    result = minimize_scalar(chi2, bounds=(lower, upper), method="bounded")
    best = float(result.x)
    best_chi2 = float(result.fun)
    target = best_chi2 + 1.0

    if chi2(lower) <= target:
        profile_lower = lower
        lower_status = "bounded_by_prior"
    else:
        profile_lower = float(brentq(lambda value: chi2(value) - target, lower, best))
        lower_status = "bracketed"
    if chi2(upper) <= target:
        profile_upper = upper
        upper_status = "bounded_by_prior"
    else:
        profile_upper = float(brentq(lambda value: chi2(value) - target, best, upper))
        upper_status = "bracketed"

    n_bins = int(wavelength.size)
    return ThermalRetrieval(
        temperature_k=best,
        error_minus_k=best - profile_lower,
        error_plus_k=profile_upper - best,
        lower_status=lower_status,
        upper_status=upper_status,
        chi2=best_chi2,
        dof=n_bins - 1,
        bic=best_chi2 + np.log(n_bins),
        n_bins=n_bins,
    )


def weighted_polynomial_fit_statistics(
    wavelength_micron: Iterable[float],
    eclipse_depth_ppm: Iterable[float],
    error_ppm: Iterable[float],
    *,
    degree: int,
) -> dict[str, object]:
    """Fit a constant or linear empirical spectrum and return BIC diagnostics."""
    if degree not in (0, 1):
        raise ValueError("only constant and linear empirical spectra are supported")
    wavelength = np.asarray(wavelength_micron, dtype=float)
    depth = np.asarray(eclipse_depth_ppm, dtype=float)
    error = np.asarray(error_ppm, dtype=float)
    valid = (
        np.isfinite(wavelength)
        & np.isfinite(depth)
        & np.isfinite(error)
        & (error > 0)
    )
    wavelength, depth, error = wavelength[valid], depth[valid], error[valid]
    if wavelength.size <= degree + 1:
        raise ValueError("insufficient valid points for polynomial fit")
    centered = wavelength - float(np.mean(wavelength))
    design = np.column_stack([np.ones_like(centered), centered])[:, : degree + 1]
    weighted_design = design / error[:, None]
    coefficients, *_ = np.linalg.lstsq(weighted_design, depth / error, rcond=None)
    model = design @ coefficients
    chi2 = float(np.sum(np.square((depth - model) / error)))
    n = int(wavelength.size)
    parameters = degree + 1
    return {
        "coefficients": coefficients,
        "chi2": chi2,
        "dof": n - parameters,
        "bic": chi2 + parameters * np.log(n),
        "n_bins": n,
        "pivot_micron": float(np.mean(wavelength)),
    }


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
