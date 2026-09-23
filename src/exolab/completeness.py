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


def circular_rv_signal(
    time: Iterable[float],
    period: float,
    semi_amplitude: float,
    phase: float,
) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    return float(semi_amplitude) * np.sin(2.0 * np.pi * t / float(period) + float(phase))


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
