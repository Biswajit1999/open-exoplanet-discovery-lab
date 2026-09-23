"""Coordinate-level crossmatch helpers for multi-archive identity resolution."""

from __future__ import annotations

from typing import Iterable

import numpy as np


def angular_separation_arcsec(
    ra1_deg: Iterable[float] | float,
    dec1_deg: Iterable[float] | float,
    ra2_deg: Iterable[float] | float,
    dec2_deg: Iterable[float] | float,
) -> np.ndarray:
    ra1 = np.deg2rad(np.asarray(ra1_deg, dtype=float))
    dec1 = np.deg2rad(np.asarray(dec1_deg, dtype=float))
    ra2 = np.deg2rad(np.asarray(ra2_deg, dtype=float))
    dec2 = np.deg2rad(np.asarray(dec2_deg, dtype=float))
    dra = ra2 - ra1
    ddec = dec2 - dec1
    a = (
        np.sin(ddec / 2.0) ** 2
        + np.cos(dec1) * np.cos(dec2) * np.sin(dra / 2.0) ** 2
    )
    angle = 2.0 * np.arcsin(np.minimum(1.0, np.sqrt(a)))
    return np.rad2deg(angle) * 3600.0


def nearest_match(
    ra_deg: float,
    dec_deg: float,
    candidate_ra_deg: Iterable[float],
    candidate_dec_deg: Iterable[float],
    *,
    max_separation_arcsec: float,
) -> tuple[int, float] | None:
    separation = angular_separation_arcsec(
        ra_deg, dec_deg, candidate_ra_deg, candidate_dec_deg
    )
    if separation.size == 0 or not np.any(np.isfinite(separation)):
        return None
    index = int(np.nanargmin(separation))
    distance = float(separation[index])
    if distance > max_separation_arcsec:
        return None
    return index, distance
