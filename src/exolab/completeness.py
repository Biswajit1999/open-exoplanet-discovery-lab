"""Deterministic RV injection/recovery utilities."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .periodogram import gls


@dataclass(frozen=True)
class InjectionOutcome:
    injected_period: float
    injected_k: float
    phase: float
    recovered_period: float
    fap: float
    recovered: bool


def _period_match(recovered: float, injected: float, *, tolerance: float, allow_harmonics: bool) -> bool:
    ratios = [1.0]
    if allow_harmonics:
        ratios += [0.5, 2.0]
    return any(abs(recovered / (injected * r) - 1.0) <= tolerance for r in ratios)


def inject_circular(time, residual_rv, period: float, k: float, phase: float):
    t = np.asarray(time, dtype=float)
    y = np.asarray(residual_rv, dtype=float)
    if t.shape != y.shape or t.ndim != 1:
        raise ValueError("time/residual_rv must be matching 1D arrays")
    return y + float(k) * np.sin(2.0 * np.pi * t / float(period) + float(phase))


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
):
    """Run a transparent circular-signal injection/recovery grid."""
    t = np.asarray(time, dtype=float)
    base = np.asarray(residual_rv, dtype=float)
    err = np.asarray(errors, dtype=float)
    if not (t.shape == base.shape == err.shape and t.ndim == 1 and len(t) >= 5):
        raise ValueError("time, residual_rv and errors must be matching 1D arrays")
    pgrid = np.asarray(periods, dtype=float)
    kgrid = np.asarray(amplitudes, dtype=float)
    phgrid = np.asarray(phases, dtype=float)
    if np.any(pgrid <= 0) or np.any(kgrid < 0):
        raise ValueError("periods must be > 0 and amplitudes >= 0")
    lo = float(min_search_period or max(0.2, np.min(pgrid) * 0.5))
    hi = float(max_search_period or min(np.ptp(t) * 1.5, np.max(pgrid) * 2.0))
    if hi <= lo:
        raise ValueError("invalid search bounds")

    outcomes: list[InjectionOutcome] = []
    for p in pgrid:
        for k in kgrid:
            for phase in phgrid:
                injected = inject_circular(t, base, p, k, phase)
                pg = gls(t, injected, err, min_period=lo, max_period=hi)
                ok = (
                    pg.false_alarm_probability <= fap_threshold
                    and _period_match(pg.best_period, p, tolerance=period_tolerance, allow_harmonics=allow_harmonics)
                )
                outcomes.append(
                    InjectionOutcome(float(p), float(k), float(phase), pg.best_period, pg.false_alarm_probability, bool(ok))
                )
    return outcomes


def completeness_table(outcomes):
    """Aggregate outcomes by injected period/amplitude."""
    buckets: dict[tuple[float, float], list[bool]] = {}
    for row in outcomes:
        buckets.setdefault((row.injected_period, row.injected_k), []).append(row.recovered)
    return [
        {
            "period": p,
            "k": k,
            "n": len(values),
            "recovered": int(sum(values)),
            "completeness": float(np.mean(values)),
        }
        for (p, k), values in sorted(buckets.items())
    ]
