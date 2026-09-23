"""Signal-transfer diagnostics for nuisance preprocessing.

The main use is to quantify how sequentially removing per-era weighted means can
attenuate a coherent astrophysical sinusoid before a period search. This is not
the same operation as a joint likelihood fit with simultaneous signal and
offset parameters; the distinction is scientifically important.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


def weighted_group_demean(
    value: Iterable[float],
    error: Iterable[float],
    groups: Iterable[str],
) -> np.ndarray:
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    g = np.asarray(list(groups), dtype=object)
    if y.ndim != 1 or y.shape != e.shape or y.shape != g.shape:
        raise ValueError("value, error and groups must be matching 1D arrays")
    if np.any(~np.isfinite(e)) or np.any(e <= 0):
        raise ValueError("errors must be finite and positive")
    residual = y.copy()
    for label in sorted({str(item) for item in g}):
        mask = g.astype(str) == label
        weights = 1.0 / np.square(e[mask])
        mean = float(np.sum(weights * y[mask]) / np.sum(weights))
        residual[mask] -= mean
    return residual


def fixed_period_amplitude(
    time: Iterable[float],
    value: Iterable[float],
    error: Iterable[float],
    period: float,
) -> float:
    t = np.asarray(time, dtype=float)
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    if not (t.shape == y.shape == e.shape) or t.ndim != 1:
        raise ValueError("time, value and error must be matching 1D arrays")
    if period <= 0:
        raise ValueError("period must be positive")
    omega = 2.0 * np.pi / float(period)
    design = np.column_stack(
        [np.sin(omega * t), np.cos(omega * t), np.ones_like(t)]
    )
    weights = 1.0 / np.square(e)
    normal = design.T @ (weights[:, None] * design)
    beta = np.linalg.pinv(normal) @ (design.T @ (weights * y))
    return float(np.hypot(beta[0], beta[1]))


@dataclass(frozen=True)
class AttenuationSummary:
    period_days: float
    phase_ratios: np.ndarray

    @property
    def median_ratio(self) -> float:
        return float(np.median(self.phase_ratios))

    @property
    def worst_phase_ratio(self) -> float:
        return float(np.min(self.phase_ratios))

    @property
    def best_phase_ratio(self) -> float:
        return float(np.max(self.phase_ratios))


def group_demean_sinusoid_transfer(
    time: Iterable[float],
    error: Iterable[float],
    groups: Iterable[str],
    period: float,
    *,
    phases: Iterable[float] | None = None,
) -> AttenuationSummary:
    """Measure recovered K/K_in after sequential group de-meaning.

    A unit-amplitude sinusoid is sampled at the real observation times. For each
    phase, its weighted mean is removed independently within each group, then a
    fixed-period sinusoid is fitted to the preprocessed signal.
    """
    t = np.asarray(time, dtype=float)
    e = np.asarray(error, dtype=float)
    g = np.asarray(list(groups), dtype=object)
    if phases is None:
        phi = np.linspace(0.0, 2.0 * np.pi, 16, endpoint=False)
    else:
        phi = np.asarray(list(phases), dtype=float)
    ratios: list[float] = []
    for phase in phi:
        injected = np.sin(2.0 * np.pi * t / float(period) + float(phase))
        projected = weighted_group_demean(injected, e, g)
        ratios.append(fixed_period_amplitude(t, projected, e, float(period)))
    return AttenuationSummary(float(period), np.asarray(ratios, dtype=float))
