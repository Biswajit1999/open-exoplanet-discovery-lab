"""SPORES-HWO long-baseline radial-velocity robustness utilities.

The functions in this module operate on the public VizieR tables from
J/AJ/170/343.  They measure sensitivity changes under declared nuisance and
orbital assumptions; they do not classify new signals.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Sequence

import numpy as np
import pandas as pd

from .completeness import classify_period_recovery
from .inference import fit_white_jitter
from .kepler import solve_eccentric_anomaly, true_anomaly
from .periodogram import generalized_lomb_scargle


@dataclass(frozen=True)
class RVProjection:
    model: np.ndarray
    residuals: np.ndarray
    coefficients: np.ndarray
    terms: tuple[str, ...]


def clean_spores_rv(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Apply the catalogue's explicit missing-value and uncertainty rules."""
    required = {"HD", "BJD", "RVel", "e_RVel", "Inst", "BibCode"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing SPORES-HWO columns: {sorted(missing)}")
    result = frame.copy()
    for column in ("BJD", "RVel", "e_RVel"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
    result["HD"] = result["HD"].astype(str).str.strip()
    result["Inst"] = result["Inst"].astype(str).str.strip()
    finite = np.isfinite(result[["BJD", "RVel", "e_RVel"]]).all(axis=1)
    sentinel = (result["RVel"] == -1.0) | (result["e_RVel"] == -1.0)
    positive_error = result["e_RVel"] > 0.0
    identity = (result["HD"] != "") & (result["Inst"] != "")
    keep = finite & ~sentinel & positive_error & identity
    diagnostics = {
        "input_rows": int(len(result)),
        "non_finite_rows": int((~finite).sum()),
        "sentinel_rows": int(sentinel.sum()),
        "non_positive_error_rows": int((finite & ~sentinel & ~positive_error).sum()),
        "missing_identity_rows": int((~identity).sum()),
        "accepted_rows": int(keep.sum()),
    }
    return result.loc[keep].reset_index(drop=True), diagnostics


def nightly_bin_spores_rv(frame: pd.DataFrame) -> pd.DataFrame:
    """Inverse-variance-bin RVs by target, instrument, and UTC-like BJD day."""
    clean, _ = clean_spores_rv(frame)
    clean = clean.copy()
    clean["night"] = np.floor(clean["BJD"]).astype(int)
    rows: list[dict[str, object]] = []
    for (target, instrument, night), group in clean.groupby(
        ["HD", "Inst", "night"], sort=True
    ):
        error = group["e_RVel"].to_numpy(float)
        weights = 1.0 / np.square(error)
        rows.append(
            {
                "target": str(target),
                "instrument": str(instrument),
                "night": int(night),
                "bjd": float(np.average(group["BJD"], weights=weights)),
                "rv_mps": float(np.average(group["RVel"], weights=weights)),
                "rv_error_mps": float(np.sqrt(1.0 / np.sum(weights))),
                "n_raw": int(len(group)),
                "source_bibcodes": ";".join(
                    sorted(set(group["BibCode"].dropna().astype(str)))
                ),
            }
        )
    return pd.DataFrame(rows)


def project_spores_nuisance(
    time: Iterable[float],
    values: Iterable[float],
    errors: Iterable[float],
    *,
    instruments: Iterable[str] | None,
    trend_degree: int = 0,
) -> RVProjection:
    """Fit global/per-instrument offsets and optional linear/quadratic trend."""
    t = np.asarray(time, dtype=float)
    y = np.asarray(values, dtype=float)
    e = np.asarray(errors, dtype=float)
    if not (t.shape == y.shape == e.shape and t.ndim == 1 and t.size >= 5):
        raise ValueError("time, values and errors must be matching 1D arrays with n >= 5")
    if not np.isfinite(np.r_[t, y, e]).all() or np.any(e <= 0):
        raise ValueError("time, values and errors must be finite and errors > 0")
    if trend_degree not in (0, 1, 2):
        raise ValueError("trend_degree must be 0, 1 or 2")

    columns: list[np.ndarray] = []
    terms: list[str] = []
    if instruments is None:
        columns.append(np.ones_like(t))
        terms.append("offset")
    else:
        labels = np.asarray(list(instruments), dtype=str)
        if labels.shape != t.shape:
            raise ValueError("instruments must match time")
        for label in sorted(set(labels.tolist())):
            columns.append((labels == label).astype(float))
            terms.append(f"offset:{label}")

    scaled_time = (t - float(np.median(t))) / 365.25
    for degree in range(1, trend_degree + 1):
        columns.append(np.power(scaled_time, degree))
        terms.append(f"trend:{degree}")
    design = np.column_stack(columns)
    weighted = design / e[:, None]
    beta, _, rank, _ = np.linalg.lstsq(weighted, y / e, rcond=None)
    if rank < design.shape[1]:
        raise ValueError("nuisance design matrix is rank deficient")
    model = design @ beta
    return RVProjection(model, y - model, beta, tuple(terms))


def effective_group_errors(
    residuals: Iterable[float],
    formal_errors: Iterable[float],
    groups: Iterable[str],
) -> tuple[np.ndarray, dict[str, float]]:
    """Estimate one white-jitter term per declared group."""
    residual = np.asarray(residuals, dtype=float)
    error = np.asarray(formal_errors, dtype=float)
    labels = np.asarray(list(groups), dtype=str)
    if not (residual.shape == error.shape == labels.shape):
        raise ValueError("residuals, errors and groups must match")
    jitters: dict[str, float] = {}
    for label in sorted(set(labels.tolist())):
        mask = labels == label
        jitters[label] = (
            fit_white_jitter(residual[mask], error[mask]).jitter
            if np.count_nonzero(mask) >= 3
            else 0.0
        )
    effective = np.sqrt(
        np.square(error)
        + np.asarray([jitters[label] ** 2 for label in labels], dtype=float)
    )
    return effective, jitters


def calibrated_group_power_threshold(
    time: Iterable[float],
    residuals: Iterable[float],
    errors: Iterable[float],
    groups: Iterable[str],
    *,
    min_period: float,
    max_period: float,
    n_permutations: int,
    seed: int,
    null: Literal["white", "correlated"] = "white",
    false_alarm_probability: float = 0.01,
) -> float:
    """Calibrate max-GLS power within instruments.

    ``white`` independently permutes standardized residuals. ``correlated``
    circularly shifts the time-ordered standardized residual sequence inside
    each instrument, preserving short-range ordering without choosing a GP
    kernel.
    """
    if n_permutations < 20:
        raise ValueError("at least 20 permutations are required")
    if null not in ("white", "correlated"):
        raise ValueError("null must be 'white' or 'correlated'")
    t = np.asarray(time, dtype=float)
    r = np.asarray(residuals, dtype=float)
    e = np.asarray(errors, dtype=float)
    labels = np.asarray(list(groups), dtype=str)
    if not (t.shape == r.shape == e.shape == labels.shape):
        raise ValueError("time, residuals, errors and groups must match")
    standardized = r / e
    rng = np.random.default_rng(seed)
    maxima = np.empty(int(n_permutations), dtype=float)
    unique = sorted(set(labels.tolist()))
    for permutation in range(int(n_permutations)):
        draw = np.empty_like(standardized)
        for label in unique:
            indices = np.flatnonzero(labels == label)
            ordered = indices[np.argsort(t[indices])]
            if null == "white":
                draw[ordered] = rng.permutation(standardized[ordered])
            elif len(ordered) > 1:
                shift = int(rng.integers(1, len(ordered)))
                draw[ordered] = np.roll(standardized[ordered], shift)
            else:
                draw[ordered] = standardized[ordered]
        search = generalized_lomb_scargle(
            t,
            draw * e,
            e,
            min_period=min_period,
            max_period=max_period,
            samples_per_peak=6,
        )
        maxima[permutation] = search.best_power
    return float(
        np.quantile(
            maxima,
            1.0 - float(false_alarm_probability),
            method="higher",
        )
    )


def eccentric_rv_signal(
    time: Iterable[float],
    *,
    period: float,
    semi_amplitude: float,
    eccentricity: float,
    omega_radians: float,
    mean_anomaly_phase: float,
) -> np.ndarray:
    """Evaluate a zero-systemic-velocity Keplerian from a mean-anomaly phase."""
    if period <= 0 or semi_amplitude < 0 or not 0 <= eccentricity < 1:
        raise ValueError("invalid Keplerian parameters")
    t = np.asarray(time, dtype=float)
    mean_anomaly = 2.0 * np.pi * t / float(period) + float(mean_anomaly_phase)
    anomaly = solve_eccentric_anomaly(mean_anomaly, float(eccentricity))
    nu = true_anomaly(anomaly, float(eccentricity))
    omega = float(omega_radians)
    return float(semi_amplitude) * (
        np.cos(nu + omega) + float(eccentricity) * np.cos(omega)
    )


def orbital_draws(
    n_draws: int,
    *,
    seed: int,
    eccentric: bool,
    beta_a: float = 0.867,
    beta_b: float = 3.03,
) -> pd.DataFrame:
    """Return a frozen set of circular or Kipping-beta orbital geometries."""
    if n_draws < 2:
        raise ValueError("at least two orbital draws are required")
    rng = np.random.default_rng(seed)
    phase = np.linspace(0.0, 2.0 * np.pi, int(n_draws), endpoint=False)
    if eccentric:
        eccentricity = rng.beta(float(beta_a), float(beta_b), int(n_draws))
        omega = rng.uniform(0.0, 2.0 * np.pi, int(n_draws))
    else:
        eccentricity = np.zeros(int(n_draws), dtype=float)
        omega = np.zeros(int(n_draws), dtype=float)
    return pd.DataFrame(
        {
            "draw": np.arange(int(n_draws)),
            "mean_anomaly_phase": phase,
            "eccentricity": eccentricity,
            "omega_radians": omega,
        }
    )


def run_hz_injection_grid(
    time: Iterable[float],
    base_residuals: Iterable[float],
    errors: Iterable[float],
    instruments: Iterable[str] | None,
    *,
    period: float,
    amplitudes: Sequence[float],
    draws: pd.DataFrame,
    trend_degree: int,
    power_threshold: float,
    min_period: float,
    max_period: float,
    fractional_tolerance: float = 0.05,
) -> pd.DataFrame:
    """Measure harmonic-aware completeness at one habitable-zone period."""
    t = np.asarray(time, dtype=float)
    base = np.asarray(base_residuals, dtype=float)
    e = np.asarray(errors, dtype=float)
    labels = None if instruments is None else np.asarray(list(instruments), dtype=str)
    rows: list[dict[str, float | int]] = []
    for amplitude in amplitudes:
        recovered = 0
        period_recoveries = 0
        harmonic_recoveries = 0
        for draw in draws.itertuples(index=False):
            signal = eccentric_rv_signal(
                t,
                period=float(period),
                semi_amplitude=float(amplitude),
                eccentricity=float(draw.eccentricity),
                omega_radians=float(draw.omega_radians),
                mean_anomaly_phase=float(draw.mean_anomaly_phase),
            )
            projected = project_spores_nuisance(
                t,
                base + signal,
                e,
                instruments=labels,
                trend_degree=int(trend_degree),
            ).residuals
            search = generalized_lomb_scargle(
                t,
                projected,
                e,
                min_period=float(min_period),
                max_period=float(max_period),
                samples_per_peak=6,
            )
            period_ok, mode = classify_period_recovery(
                search.best_period,
                float(period),
                fractional_tolerance=float(fractional_tolerance),
            )
            accepted = bool(period_ok and search.best_power >= power_threshold)
            recovered += int(accepted)
            period_recoveries += int(accepted and mode == "period")
            harmonic_recoveries += int(accepted and mode != "period")
        rows.append(
            {
                "period_days": float(period),
                "semi_amplitude_mps": float(amplitude),
                "n_injections": int(len(draws)),
                "n_recovered": int(recovered),
                "n_period_recovered": int(period_recoveries),
                "n_harmonic_recovered": int(harmonic_recoveries),
                "completeness": float(recovered / len(draws)),
            }
        )
    return pd.DataFrame(rows)


def interpolate_completeness_threshold(
    amplitudes: Iterable[float],
    completeness: Iterable[float],
    level: float,
) -> float:
    """Interpolate a monotonic K-level threshold, returning NaN if unbracketed."""
    x = np.asarray(amplitudes, dtype=float)
    y = np.maximum.accumulate(np.asarray(completeness, dtype=float))
    order = np.argsort(x)
    x, y = x[order], y[order]
    if not 0 < level < 1 or x.size == 0 or np.nanmax(y) < level:
        return float("nan")
    index = int(np.flatnonzero(y >= level)[0])
    if index == 0:
        return float(x[0])
    y0, y1 = y[index - 1], y[index]
    x0, x1 = x[index - 1], x[index]
    return float(x1 if y1 == y0 else x0 + (level - y0) * (x1 - x0) / (y1 - y0))
