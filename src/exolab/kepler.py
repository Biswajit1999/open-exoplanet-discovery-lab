"""Keplerian radial-velocity equations with explicit numerical conventions."""

from __future__ import annotations

from typing import Iterable

import numpy as np


def solve_eccentric_anomaly(
    mean_anomaly: Iterable[float] | float,
    eccentricity: float,
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> np.ndarray:
    e = float(eccentricity)
    if not 0.0 <= e < 1.0:
        raise ValueError("eccentricity must satisfy 0 <= e < 1")
    m = np.asarray(mean_anomaly, dtype=float)
    wrapped = np.mod(m, 2.0 * np.pi)
    estimate = np.where(e < 0.8, wrapped, np.pi)
    for _ in range(int(max_iterations)):
        f = estimate - e * np.sin(estimate) - wrapped
        fp = 1.0 - e * np.cos(estimate)
        step = f / fp
        estimate = estimate - step
        if np.nanmax(np.abs(step)) < tolerance:
            return estimate
    raise RuntimeError("Kepler equation did not converge")


def true_anomaly(eccentric_anomaly: Iterable[float] | float, eccentricity: float) -> np.ndarray:
    e = float(eccentricity)
    E = np.asarray(eccentric_anomaly, dtype=float)
    numerator = np.sqrt(1.0 + e) * np.sin(E / 2.0)
    denominator = np.sqrt(1.0 - e) * np.cos(E / 2.0)
    return 2.0 * np.arctan2(numerator, denominator)


def keplerian_rv(
    time: Iterable[float],
    *,
    period: float,
    semi_amplitude: float,
    eccentricity: float = 0.0,
    omega_radians: float = 0.0,
    t_periastron: float = 0.0,
    systemic_velocity: float = 0.0,
) -> np.ndarray:
    """Evaluate the standard single-planet stellar reflex velocity.

    Positive velocity follows the conventional receding-positive RV sign.
    """
    if period <= 0 or semi_amplitude < 0:
        raise ValueError("period must be positive and semi_amplitude non-negative")
    t = np.asarray(time, dtype=float)
    mean_anomaly = 2.0 * np.pi * (t - float(t_periastron)) / float(period)
    E = solve_eccentric_anomaly(mean_anomaly, float(eccentricity))
    nu = true_anomaly(E, float(eccentricity))
    omega = float(omega_radians)
    return (
        float(systemic_velocity)
        + float(semi_amplitude)
        * (np.cos(nu + omega) + float(eccentricity) * np.cos(omega))
    )
