"""Optical/near-infrared coherence diagnostics for RV time series."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .rv import fit_shared_sinusoid


def wrap_phase(delta: float) -> float:
    return float((delta + np.pi) % (2.0 * np.pi) - np.pi)


@dataclass(frozen=True)
class CoherenceResult:
    period: float
    k_a: float
    k_b: float
    amplitude_ratio: float
    phase_a: float
    phase_b: float
    phase_delta: float


def compare_bands(time_a, rv_a, err_a, time_b, rv_b, err_b, *, period: float) -> CoherenceResult:
    a = fit_shared_sinusoid(time_a, rv_a, err_a, period=period)
    b = fit_shared_sinusoid(time_b, rv_b, err_b, period=period)
    ratio = np.nan if a.semi_amplitude == 0 else b.semi_amplitude / a.semi_amplitude
    return CoherenceResult(
        period=float(period),
        k_a=a.semi_amplitude,
        k_b=b.semi_amplitude,
        amplitude_ratio=float(ratio),
        phase_a=a.phase,
        phase_b=b.phase,
        phase_delta=wrap_phase(b.phase - a.phase),
    )


def simultaneity_counts(time_a, time_b, windows_hours=(1.0, 6.0, 24.0, 72.0, 168.0)):
    """Count A epochs with at least one B epoch within each symmetric window.

    Times are expected in days in the same standard (e.g. BJD_TDB).
    """
    a = np.sort(np.asarray(time_a, dtype=float))
    b = np.sort(np.asarray(time_b, dtype=float))
    if a.ndim != 1 or b.ndim != 1 or not np.isfinite(np.r_[a, b]).all():
        raise ValueError("times must be finite 1D arrays")
    if len(a) == 0 or len(b) == 0:
        return {float(w): 0 for w in windows_hours}
    nearest = np.min(np.abs(a[:, None] - b[None, :]), axis=1)
    return {float(w): int(np.sum(nearest <= float(w) / 24.0)) for w in windows_hours}
