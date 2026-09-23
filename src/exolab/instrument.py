"""Instrument-specific provenance and quality gates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Iterable

from astropy.time import Time
import numpy as np


NIRPS_BAD_START_UTC = datetime(2025, 4, 1, 12, 0, tzinfo=timezone.utc)
NIRPS_BAD_END_UTC = datetime(2025, 7, 24, 12, 0, tzinfo=timezone.utc)


def parse_version(value: str | None) -> tuple[int, ...] | None:
    if not value:
        return None
    numbers = re.findall(r"\d+", str(value))
    return tuple(int(x) for x in numbers) if numbers else None


def version_at_least(value: str | None, minimum: str) -> bool:
    current = parse_version(value)
    floor = parse_version(minimum)
    if current is None or floor is None:
        return False
    length = max(len(current), len(floor))
    current = current + (0,) * (length - len(current))
    floor = floor + (0,) * (length - len(floor))
    return current >= floor


@dataclass(frozen=True)
class NIRPSQuality:
    precision_rv_safe: bool
    reason: str


def nirps_precision_rv_quality(
    observation_time: str | datetime,
    procsoft: str | None,
) -> NIRPSQuality:
    if isinstance(observation_time, datetime):
        dt = observation_time
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone.utc)
    else:
        dt = Time(str(observation_time), scale="utc").to_datetime(timezone=timezone.utc)

    in_bad_interval = NIRPS_BAD_START_UTC <= dt <= NIRPS_BAD_END_UTC
    if in_bad_interval and not version_at_least(procsoft, "3.2.7"):
        return NIRPSQuality(
            False,
            "Affected 2025 interval without verified DRS >= 3.2.7 reprocessing",
        )
    if procsoft is None:
        return NIRPSQuality(False, "PROCSOFT pipeline version is missing")
    return NIRPSQuality(True, "Pipeline/date gate passed")


def label_eras(time: Iterable[float], boundaries: Iterable[float], prefix: str = "era") -> np.ndarray:
    t = np.asarray(time, dtype=float)
    cuts = np.sort(np.asarray(list(boundaries), dtype=float))
    index = np.searchsorted(cuts, t, side="right")
    return np.array([f"{prefix}{int(i)}" for i in index], dtype=object)
