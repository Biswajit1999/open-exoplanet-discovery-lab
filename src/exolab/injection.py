"""Transit injection and recovery experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .search import search_bls


@dataclass(frozen=True)
class RecoveryResult:
    period_days: float
    depth_fraction: float
    epoch_days: float
    recovered_period_days: float
    recovered_snr: float
    recovered: bool

    def as_dict(self) -> dict[str, float | bool]:
        return asdict(self)


def inject_box_transit(
    time: np.ndarray,
    flux: np.ndarray,
    period_days: float,
    epoch_days: float,
    duration_days: float,
    depth_fraction: float,
) -> np.ndarray:
    """Inject a transparent box model into a normalized light curve."""

    if period_days <= 0 or duration_days <= 0 or not 0 < depth_fraction < 1:
        raise ValueError("period, duration and depth must be physically positive")
    time = np.asarray(time, dtype=float)
    injected = np.asarray(flux, dtype=float).copy()
    phase = ((time - epoch_days + 0.5 * period_days) % period_days) - 0.5 * period_days
    injected[np.abs(phase) <= duration_days / 2.0] -= depth_fraction
    return injected


def period_matches(injected: float, recovered: float, relative_tolerance: float = 0.02) -> bool:
    """Accept the period or common factor-of-two aliases."""

    for ratio in (1.0, 0.5, 2.0):
        if abs(recovered - ratio * injected) / (ratio * injected) <= relative_tolerance:
            return True
    return False


def run_injection_recovery(
    time: np.ndarray,
    flux: np.ndarray,
    periods_days: list[float] | np.ndarray,
    depths_fraction: list[float] | np.ndarray,
    duration_hours: float = 2.0,
    flux_err: np.ndarray | None = None,
    snr_threshold: float = 7.0,
    seed: int = 42,
) -> list[RecoveryResult]:
    """Evaluate a period-depth grid with randomized transit epochs."""

    rng = np.random.default_rng(seed)
    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)
    output: list[RecoveryResult] = []
    for period in np.asarray(periods_days, dtype=float):
        for depth in np.asarray(depths_fraction, dtype=float):
            epoch = float(time.min() + rng.uniform(0, period))
            injected = inject_box_transit(
                time,
                flux,
                period_days=float(period),
                epoch_days=epoch,
                duration_days=duration_hours / 24.0,
                depth_fraction=float(depth),
            )
            signal, _ = search_bls(
                time,
                injected,
                flux_err=flux_err,
                minimum_period=max(0.3, min(periods_days) * 0.7),
                maximum_period=min(float(np.ptp(time) / 2), max(periods_days) * 1.4),
                durations_hours=(duration_hours,),
            )
            recovered = period_matches(float(period), signal.period_days) and signal.depth_snr >= snr_threshold
            output.append(
                RecoveryResult(
                    period_days=float(period),
                    depth_fraction=float(depth),
                    epoch_days=epoch,
                    recovered_period_days=signal.period_days,
                    recovered_snr=signal.depth_snr,
                    recovered=bool(recovered),
                )
            )
    return output
