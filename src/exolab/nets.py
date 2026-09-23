"""NETS III nuisance-model and completeness primitives.

These functions keep the circular benchmark deliberately transparent. They
quantify pipeline sensitivity; they do not turn a recovered period into a
planet interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from .completeness import circular_rv_signal, classify_period_recovery
from .inference import fit_white_jitter
from .periodogram import generalized_lomb_scargle
from .timeseries import fit_sinusoid


@dataclass(frozen=True)
class NuisanceProjection:
    model: np.ndarray
    residuals: np.ndarray
    coefficients: np.ndarray
    terms: tuple[str, ...]


def project_nuisance(
    values: Iterable[float],
    errors: Iterable[float],
    *,
    groups: Iterable[str] | None = None,
    activity: Iterable[float] | None = None,
) -> NuisanceProjection:
    """Weighted projection onto an intercept/group-offset/activity model."""
    y = np.asarray(values, dtype=float)
    e = np.asarray(errors, dtype=float)
    if y.ndim != 1 or y.shape != e.shape or y.size < 4:
        raise ValueError("values/errors must be matching 1D arrays with n >= 4")
    if not np.isfinite(np.r_[y, e]).all() or np.any(e <= 0):
        raise ValueError("values/errors must be finite and errors > 0")

    columns: list[np.ndarray] = []
    terms: list[str] = []
    if groups is None:
        columns.append(np.ones_like(y))
        terms.append("offset")
    else:
        labels = np.asarray(list(groups), dtype=str)
        if labels.shape != y.shape:
            raise ValueError("groups must match values")
        for label in sorted(set(labels.tolist())):
            columns.append((labels == label).astype(float))
            terms.append(f"offset:{label}")

    if activity is not None:
        indicator = np.asarray(activity, dtype=float)
        if indicator.shape != y.shape or not np.isfinite(indicator).all():
            raise ValueError("activity must be a finite array matching values")
        weights = 1.0 / np.square(e)
        centred = indicator - np.average(indicator, weights=weights)
        scale = float(np.std(centred))
        if scale > 0:
            columns.append(centred / scale)
            terms.append("activity:standardized")

    design = np.column_stack(columns)
    weighted_design = design / e[:, None]
    beta, _, rank, _ = np.linalg.lstsq(weighted_design, y / e, rcond=None)
    if rank < design.shape[1]:
        raise ValueError("nuisance design matrix is rank deficient")
    model = design @ beta
    return NuisanceProjection(
        model=model,
        residuals=y - model,
        coefficients=beta,
        terms=tuple(terms),
    )


def fit_group_jitters(
    residuals: Iterable[float],
    errors: Iterable[float],
    groups: Iterable[str],
) -> dict[str, float]:
    r = np.asarray(residuals, dtype=float)
    e = np.asarray(errors, dtype=float)
    g = np.asarray(list(groups), dtype=str)
    if not (r.shape == e.shape == g.shape):
        raise ValueError("residuals/errors/groups must match")
    result: dict[str, float] = {}
    for label in sorted(set(g.tolist())):
        mask = g == label
        result[label] = (
            fit_white_jitter(r[mask], e[mask]).jitter
            if np.count_nonzero(mask) >= 3
            else 0.0
        )
    return result


def effective_errors(
    errors: Iterable[float],
    groups: Iterable[str],
    jitters: Mapping[str, float],
) -> np.ndarray:
    e = np.asarray(errors, dtype=float)
    g = np.asarray(list(groups), dtype=str)
    return np.sqrt(
        np.square(e)
        + np.asarray([float(jitters.get(label, 0.0)) ** 2 for label in g])
    )


def calibrated_power_threshold(
    time: Iterable[float],
    residuals: Iterable[float],
    errors: Iterable[float],
    *,
    min_period: float,
    max_period: float,
    n_permutations: int,
    seed: int,
    false_alarm_probability: float = 0.01,
) -> float:
    """Empirical maximum-GLS threshold from deterministic residual shuffles."""
    if n_permutations < 20:
        raise ValueError("at least 20 permutations are required")
    t = np.asarray(time, dtype=float)
    r = np.asarray(residuals, dtype=float)
    e = np.asarray(errors, dtype=float)
    rng = np.random.default_rng(seed)
    maxima = np.empty(n_permutations, dtype=float)
    for index in range(n_permutations):
        permuted = rng.permutation(r)
        maxima[index] = generalized_lomb_scargle(
            t,
            permuted,
            e,
            min_period=min_period,
            max_period=max_period,
            samples_per_peak=8,
        ).best_power
    quantile = 1.0 - float(false_alarm_probability)
    return float(np.quantile(maxima, quantile, method="higher"))


def run_model_completeness(
    time: Iterable[float],
    base_residuals: Iterable[float],
    errors: Iterable[float],
    *,
    periods: Sequence[float],
    amplitudes: Sequence[float],
    phases: Sequence[float],
    min_period: float,
    max_period: float,
    power_threshold: float,
    groups: Iterable[str] | None = None,
    activity: Iterable[float] | None = None,
    fractional_tolerance: float = 0.05,
) -> pd.DataFrame:
    """Run one nuisance model over a frozen injection grid."""
    t = np.asarray(time, dtype=float)
    base = np.asarray(base_residuals, dtype=float)
    e = np.asarray(errors, dtype=float)
    rows: list[dict[str, float | int]] = []
    for period in periods:
        for amplitude in amplitudes:
            recovered = 0
            for phase in phases:
                injected = base + circular_rv_signal(t, period, amplitude, phase)
                projected = project_nuisance(
                    injected,
                    e,
                    groups=groups,
                    activity=activity,
                ).residuals
                search = generalized_lomb_scargle(
                    t,
                    projected,
                    e,
                    min_period=min_period,
                    max_period=max_period,
                    samples_per_peak=8,
                )
                period_ok, _ = classify_period_recovery(
                    search.best_period,
                    float(period),
                    fractional_tolerance=fractional_tolerance,
                )
                recovered += int(period_ok and search.best_power >= power_threshold)
            rows.append(
                {
                    "period": float(period),
                    "semi_amplitude": float(amplitude),
                    "n_injections": int(len(phases)),
                    "n_recovered": int(recovered),
                    "completeness": float(recovered / len(phases)),
                }
            )
    return pd.DataFrame(rows)


def completeness_contours(
    table: pd.DataFrame,
    levels: Sequence[float] = (0.5, 0.9),
) -> pd.DataFrame:
    """Interpolate K at requested recovery levels for each period."""
    rows: list[dict[str, float]] = []
    for period, group in table.groupby("period", sort=True):
        ordered = group.sort_values("semi_amplitude")
        amplitude = ordered["semi_amplitude"].to_numpy(float)
        completeness = np.maximum.accumulate(ordered["completeness"].to_numpy(float))
        row: dict[str, float] = {"period": float(period)}
        for level in levels:
            key = f"k{int(round(100 * level))}"
            if np.max(completeness) < level:
                row[key] = float("nan")
                continue
            index = int(np.flatnonzero(completeness >= level)[0])
            if index == 0:
                row[key] = float(amplitude[0])
            else:
                x0, x1 = completeness[index - 1], completeness[index]
                y0, y1 = amplitude[index - 1], amplitude[index]
                row[key] = float(y1 if x1 == x0 else y0 + (level - x0) * (y1 - y0) / (x1 - x0))
        rows.append(row)
    return pd.DataFrame(rows)


def projected_signal_transfer(
    time: Iterable[float],
    errors: Iterable[float],
    period: float,
    phases: Iterable[float],
    *,
    groups: Iterable[str] | None = None,
    activity: Iterable[float] | None = None,
) -> np.ndarray:
    """Known-period K recovery after nuisance projection for each phase."""
    t = np.asarray(time, dtype=float)
    e = np.asarray(errors, dtype=float)
    ratios = []
    for phase in phases:
        injected = circular_rv_signal(t, period, 1.0, phase)
        residual = project_nuisance(
            injected,
            e,
            groups=groups,
            activity=activity,
        ).residuals
        ratios.append(fit_sinusoid(t, residual, e, period).semi_amplitude)
    return np.asarray(ratios, dtype=float)
