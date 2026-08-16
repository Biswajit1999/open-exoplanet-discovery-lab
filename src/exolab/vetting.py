"""Fast diagnostic tests for transit-like signals."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .search import TransitSignal


@dataclass(frozen=True)
class VettingResult:
    odd_depth: float
    even_depth: float
    odd_even_sigma: float
    secondary_depth: float
    secondary_snr: float
    in_transit_points: int
    n_transits: int
    flags: tuple[str, ...]

    def as_dict(self) -> dict[str, float | int | tuple[str, ...]]:
        return asdict(self)


def _weighted_depth(values: np.ndarray, errors: np.ndarray | None) -> tuple[float, float]:
    if not len(values):
        return float("nan"), float("nan")
    depth = 1.0 - float(np.nanmean(values))
    if errors is not None and np.all(np.isfinite(errors)) and np.all(errors > 0):
        weights = 1.0 / np.square(errors)
        mean = float(np.sum(weights * values) / np.sum(weights))
        return 1.0 - mean, float(np.sqrt(1.0 / np.sum(weights)))
    scatter = float(np.nanstd(values, ddof=1)) if len(values) > 1 else float("nan")
    return depth, scatter / np.sqrt(len(values))


def vet_signal(
    time: np.ndarray,
    flux: np.ndarray,
    signal: TransitSignal,
    flux_err: np.ndarray | None = None,
) -> VettingResult:
    """Measure odd/even and phase-0.5 depths; return explicit warning flags."""

    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)
    errors = None if flux_err is None else np.asarray(flux_err, dtype=float)
    phase_cycles = (time - signal.epoch_days) / signal.period_days
    event_number = np.floor(phase_cycles + 0.5).astype(int)
    centered_phase = phase_cycles - np.round(phase_cycles)
    half_width = 0.5 * signal.duration_days / signal.period_days
    in_transit = np.abs(centered_phase) <= half_width
    odd = in_transit & (np.abs(event_number) % 2 == 1)
    even = in_transit & (np.abs(event_number) % 2 == 0)

    odd_depth, odd_error = _weighted_depth(flux[odd], None if errors is None else errors[odd])
    even_depth, even_error = _weighted_depth(flux[even], None if errors is None else errors[even])
    denominator = np.hypot(odd_error, even_error)
    odd_even_sigma = abs(odd_depth - even_depth) / denominator if denominator > 0 else float("nan")

    secondary_phase = ((phase_cycles - 0.5 + 0.5) % 1.0) - 0.5
    secondary_mask = np.abs(secondary_phase) <= half_width
    secondary_depth, secondary_error = _weighted_depth(
        flux[secondary_mask], None if errors is None else errors[secondary_mask]
    )
    secondary_snr = secondary_depth / secondary_error if secondary_error > 0 else float("nan")

    flags: list[str] = []
    if signal.n_transits < 3:
        flags.append("fewer-than-three-transits")
    if np.isfinite(odd_even_sigma) and odd_even_sigma >= 3:
        flags.append("odd-even-depth-mismatch")
    if np.isfinite(secondary_snr) and secondary_snr >= 5:
        flags.append("significant-secondary-eclipse")
    if signal.depth_fraction <= 0:
        flags.append("non-positive-depth")
    if signal.depth_fraction >= 0.05:
        flags.append("very-deep-event")

    return VettingResult(
        odd_depth=odd_depth,
        even_depth=even_depth,
        odd_even_sigma=float(odd_even_sigma),
        secondary_depth=secondary_depth,
        secondary_snr=float(secondary_snr),
        in_transit_points=int(np.sum(in_transit)),
        n_transits=signal.n_transits,
        flags=tuple(flags),
    )
