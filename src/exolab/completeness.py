"""Injection/recovery primitives for RV detection-completeness experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from .periodogram import generalized_lomb_scargle


@dataclass(frozen=True)
class InjectionRecovery:
    injected_period: float
    injected_k: float
    injected_phase: float
    detected_period: float
    detected_power: float
    fap: float
    recovered: bool
    recovery_mode: str


@dataclass(frozen=True)
class InjectionOutcome:
    """Release-0.2 compatibility record for grid-level recovery output."""

    injected_period: float
    injected_k: float
    phase: float
    recovered_period: float
    fap: float
    recovered: bool


def circular_rv_signal(
    time: Iterable[float],
    period: float,
    semi_amplitude: float,
    phase: float,
) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    return float(semi_amplitude) * np.sin(2.0 * np.pi * t / float(period) + float(phase))


def inject_circular(time, residual_rv, period: float, k: float, phase: float) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    residual = np.asarray(residual_rv, dtype=float)
    if t.ndim != 1 or t.shape != residual.shape:
        raise ValueError("time/residual_rv must be matching 1D arrays")
    return residual + circular_rv_signal(t, period, k, phase)


def classify_period_recovery(
    detected_period: float,
    injected_period: float,
    *,
    fractional_tolerance: float = 0.02,
    aliases: Sequence[float] = (0.5, 1.0, 2.0),
) -> tuple[bool, str]:
    if injected_period <= 0 or detected_period <= 0:
        return False, "invalid"
    for factor in aliases:
        reference = injected_period * factor
        if abs(detected_period - reference) / reference <= fractional_tolerance:
            if factor == 1.0:
                return True, "period"
            return True, f"harmonic:{factor:g}"
    return False, "miss"


def inject_and_recover(
    time: Iterable[float],
    baseline_rv: Iterable[float],
    error: Iterable[float],
    *,
    period: float,
    semi_amplitude: float,
    phase: float,
    min_period: float,
    max_period: float,
    fap_threshold: float = 0.01,
    fractional_tolerance: float = 0.02,
) -> InjectionRecovery:
    t = np.asarray(time, dtype=float)
    y = np.asarray(baseline_rv, dtype=float)
    e = np.asarray(error, dtype=float)
    injected = y + circular_rv_signal(t, period, semi_amplitude, phase)
    result = generalized_lomb_scargle(
        t,
        injected,
        e,
        min_period=min_period,
        max_period=max_period,
    )
    period_ok, mode = classify_period_recovery(
        result.best_period,
        period,
        fractional_tolerance=fractional_tolerance,
    )
    recovered = period_ok and (
        not np.isfinite(result.false_alarm_probability)
        or result.false_alarm_probability <= fap_threshold
    )
    return InjectionRecovery(
        injected_period=float(period),
        injected_k=float(semi_amplitude),
        injected_phase=float(phase),
        detected_period=result.best_period,
        detected_power=result.best_power,
        fap=result.false_alarm_probability,
        recovered=bool(recovered),
        recovery_mode=mode,
    )


def run_injection_grid(
    time: Iterable[float],
    baseline_rv: Iterable[float],
    error: Iterable[float],
    *,
    periods: Iterable[float],
    semi_amplitudes: Iterable[float],
    phases: Iterable[float],
    min_period: float,
    max_period: float,
    fap_threshold: float = 0.01,
) -> pd.DataFrame:
    rows: list[dict[str, float | bool | str]] = []
    for period in periods:
        for k in semi_amplitudes:
            attempts: list[InjectionRecovery] = []
            for phase in phases:
                attempts.append(
                    inject_and_recover(
                        time,
                        baseline_rv,
                        error,
                        period=float(period),
                        semi_amplitude=float(k),
                        phase=float(phase),
                        min_period=min_period,
                        max_period=max_period,
                        fap_threshold=fap_threshold,
                    )
                )
            rows.append(
                {
                    "period": float(period),
                    "semi_amplitude": float(k),
                    "n_injections": len(attempts),
                    "n_recovered": int(sum(x.recovered for x in attempts)),
                    "completeness": float(np.mean([x.recovered for x in attempts])),
                }
            )
    return pd.DataFrame(rows)


def injection_recovery(
    time,
    residual_rv,
    errors,
    *,
    periods,
    amplitudes,
    phases,
    min_search_period: float | None = None,
    max_search_period: float | None = None,
    fap_threshold: float = 0.01,
    period_tolerance: float = 0.05,
    allow_harmonics: bool = True,
) -> list[InjectionOutcome]:
    """Compatibility grid that retains the explicit per-injection outcomes."""
    t = np.asarray(time, dtype=float)
    base = np.asarray(residual_rv, dtype=float)
    err = np.asarray(errors, dtype=float)
    if not (t.shape == base.shape == err.shape and t.ndim == 1 and t.size >= 5):
        raise ValueError("time, residual_rv and errors must be matching 1D arrays")
    period_grid = np.asarray(periods, dtype=float)
    amplitude_grid = np.asarray(amplitudes, dtype=float)
    phase_grid = np.asarray(phases, dtype=float)
    if np.any(period_grid <= 0) or np.any(amplitude_grid < 0):
        raise ValueError("periods must be > 0 and amplitudes >= 0")
    lower = float(min_search_period or max(0.2, np.min(period_grid) * 0.5))
    upper = float(
        max_search_period
        or min(float(np.ptp(t)) * 1.5, float(np.max(period_grid)) * 2.0)
    )
    aliases = (0.5, 1.0, 2.0) if allow_harmonics else (1.0,)
    outcomes: list[InjectionOutcome] = []
    for period in period_grid:
        for amplitude in amplitude_grid:
            for phase in phase_grid:
                signal = inject_circular(t, base, period, amplitude, phase)
                result = generalized_lomb_scargle(
                    t,
                    signal,
                    err,
                    min_period=lower,
                    max_period=upper,
                )
                period_ok, _ = classify_period_recovery(
                    result.best_period,
                    float(period),
                    fractional_tolerance=period_tolerance,
                    aliases=aliases,
                )
                detected = period_ok and (
                    not np.isfinite(result.false_alarm_probability)
                    or result.false_alarm_probability <= fap_threshold
                )
                outcomes.append(
                    InjectionOutcome(
                        injected_period=float(period),
                        injected_k=float(amplitude),
                        phase=float(phase),
                        recovered_period=result.best_period,
                        fap=result.false_alarm_probability,
                        recovered=bool(detected),
                    )
                )
    return outcomes


def completeness_table(outcomes: Iterable[InjectionOutcome]) -> list[dict[str, float | int]]:
    buckets: dict[tuple[float, float], list[bool]] = {}
    for outcome in outcomes:
        buckets.setdefault(
            (outcome.injected_period, outcome.injected_k), []
        ).append(outcome.recovered)
    return [
        {
            "period": period,
            "k": amplitude,
            "n": len(values),
            "recovered": int(sum(values)),
            "completeness": float(np.mean(values)),
        }
        for (period, amplitude), values in sorted(buckets.items())
    ]
