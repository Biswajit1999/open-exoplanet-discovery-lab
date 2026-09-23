"""Optical/near-infrared radial-velocity coherence diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np

from .timeseries import SinusoidFit, fit_sinusoid, wrapped_phase_difference


def matched_epoch_pairs(
    left_time: Iterable[float],
    right_time: Iterable[float],
    tolerance_days: float,
) -> list[tuple[int, int, float]]:
    """Greedy one-to-one nearest epoch matching.

    Returns (left_index, right_index, signed_delta_days). A right-hand epoch is
    never reused. The function is for simultaneity accounting, not interpolation.
    """
    if tolerance_days < 0:
        raise ValueError("tolerance_days must be non-negative")
    left = np.asarray(left_time, dtype=float)
    right = np.asarray(right_time, dtype=float)
    available = set(np.flatnonzero(np.isfinite(right)).tolist())
    pairs: list[tuple[int, int, float]] = []
    for i in np.flatnonzero(np.isfinite(left)):
        if not available:
            break
        candidates = np.array(sorted(available), dtype=int)
        delta = right[candidates] - left[i]
        j_local = int(np.argmin(np.abs(delta)))
        j = int(candidates[j_local])
        if abs(float(delta[j_local])) <= tolerance_days:
            pairs.append((int(i), j, float(delta[j_local])))
            available.remove(j)
    return pairs


def simultaneity_counts(
    optical_time: Iterable[float],
    nir_time: Iterable[float],
    windows_days: Iterable[float] = (1 / 24, 6 / 24, 1, 3, 7),
) -> dict[str, int]:
    result: dict[str, int] = {}
    for window in windows_days:
        hours = float(window) * 24.0
        if hours < 24:
            label = f"{hours:g}h"
        else:
            label = f"{float(window):g}d"
        result[label] = len(matched_epoch_pairs(optical_time, nir_time, float(window)))
    return result


@dataclass(frozen=True)
class ChromaticSignalComparison:
    period: float
    optical: SinusoidFit
    nir: SinusoidFit
    amplitude_ratio_nir_to_optical: float
    amplitude_ratio_error: float
    phase_difference_radians: float
    phase_difference_error_radians: float
    simultaneity: Mapping[str, int]


def compare_fixed_period_signal(
    optical_time: Iterable[float],
    optical_rv: Iterable[float],
    optical_error: Iterable[float],
    nir_time: Iterable[float],
    nir_rv: Iterable[float],
    nir_error: Iterable[float],
    period: float,
    *,
    optical_groups: Iterable[str] | None = None,
    nir_groups: Iterable[str] | None = None,
) -> ChromaticSignalComparison:
    optical = fit_sinusoid(
        optical_time, optical_rv, optical_error, period, groups=optical_groups
    )
    nir = fit_sinusoid(nir_time, nir_rv, nir_error, period, groups=nir_groups)
    if optical.semi_amplitude <= 0:
        ratio = float("nan")
        ratio_error = float("nan")
    else:
        ratio = nir.semi_amplitude / optical.semi_amplitude
        rel = 0.0
        if nir.semi_amplitude > 0:
            rel += (nir.semi_amplitude_error / nir.semi_amplitude) ** 2
        rel += (optical.semi_amplitude_error / optical.semi_amplitude) ** 2
        ratio_error = abs(ratio) * float(np.sqrt(rel))
    phase_delta = wrapped_phase_difference(nir.phase_radians, optical.phase_radians)
    phase_error = float(
        np.sqrt(nir.phase_error_radians**2 + optical.phase_error_radians**2)
    )
    return ChromaticSignalComparison(
        period=float(period),
        optical=optical,
        nir=nir,
        amplitude_ratio_nir_to_optical=float(ratio),
        amplitude_ratio_error=float(ratio_error),
        phase_difference_radians=phase_delta,
        phase_difference_error_radians=phase_error,
        simultaneity=simultaneity_counts(optical_time, nir_time),
    )
