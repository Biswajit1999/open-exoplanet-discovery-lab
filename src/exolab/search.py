"""Transit-search primitives with explicit assumptions."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from astropy.timeseries import BoxLeastSquares
from scipy.ndimage import median_filter


@dataclass(frozen=True)
class TransitSignal:
    period_days: float
    epoch_days: float
    duration_days: float
    depth_fraction: float
    depth_error_fraction: float
    depth_snr: float
    power: float
    n_transits: int

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


def clean_lightcurve(
    time: np.ndarray,
    flux: np.ndarray,
    flux_err: np.ndarray | None = None,
    sigma: float = 7.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Remove non-finite rows, normalize, and symmetrically clip gross outliers."""

    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)
    if flux_err is None:
        flux_err = np.full_like(flux, np.nan)
    else:
        flux_err = np.asarray(flux_err, dtype=float)
    if not (time.shape == flux.shape == flux_err.shape):
        raise ValueError("time, flux and flux_err must have identical shapes")

    finite = np.isfinite(time) & np.isfinite(flux)
    if np.any(np.isfinite(flux_err)):
        finite &= np.isfinite(flux_err) & (flux_err > 0)
    time, flux, flux_err = time[finite], flux[finite], flux_err[finite]
    if len(time) < 20:
        raise ValueError("at least 20 finite cadences are required")

    order = np.argsort(time)
    time, flux, flux_err = time[order], flux[order], flux_err[order]
    median = np.nanmedian(flux)
    if not np.isfinite(median) or median == 0:
        raise ValueError("flux median must be finite and non-zero")
    flux = flux / median
    flux_err = flux_err / abs(median)

    center = np.nanmedian(flux)
    mad = 1.4826 * np.nanmedian(np.abs(flux - center))
    keep = np.ones_like(flux, dtype=bool) if mad == 0 else np.abs(flux - center) <= sigma * mad
    return time[keep], flux[keep], flux_err[keep]


def detrend_lightcurve(
    time: np.ndarray,
    flux: np.ndarray,
    window_days: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Divide by a running median whose width is expressed in days."""

    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)
    if len(time) != len(flux) or len(time) < 20:
        raise ValueError("time and flux need at least 20 matching samples")
    cadence = np.nanmedian(np.diff(np.sort(time)))
    if not np.isfinite(cadence) or cadence <= 0:
        raise ValueError("time must contain increasing, distinct cadences")
    width = max(5, int(round(window_days / cadence)))
    if width % 2 == 0:
        width += 1
    width = min(width, len(flux) - (1 - len(flux) % 2))
    trend = median_filter(flux, size=width, mode="nearest")
    good = np.isfinite(trend) & (trend > 0)
    flattened = np.full_like(flux, np.nan)
    flattened[good] = flux[good] / trend[good]
    return flattened, trend


def search_bls(
    time: np.ndarray,
    flux: np.ndarray,
    flux_err: np.ndarray | None = None,
    minimum_period: float = 0.5,
    maximum_period: float | None = None,
    durations_hours: tuple[float, ...] = (0.75, 1.5, 3.0, 5.0),
    frequency_factor: float = 3.0,
) -> tuple[TransitSignal, object]:
    """Search a light curve and return the maximum-power BLS signal."""

    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)
    if flux_err is not None:
        flux_err = np.asarray(flux_err, dtype=float)
        if not np.all(np.isfinite(flux_err)):
            flux_err = None
    finite = np.isfinite(time) & np.isfinite(flux)
    if flux_err is not None:
        finite &= np.isfinite(flux_err) & (flux_err > 0)
    time, flux = time[finite], flux[finite]
    if flux_err is not None:
        flux_err = flux_err[finite]
    baseline = float(np.ptp(time))
    if baseline <= minimum_period * 2:
        raise ValueError("time baseline must span at least two minimum periods")
    if maximum_period is None:
        maximum_period = min(30.0, baseline / 2.0)
    if not minimum_period < maximum_period <= baseline:
        raise ValueError("period bounds must satisfy min < max <= time baseline")

    durations = np.asarray(durations_hours, dtype=float) / 24.0
    durations = durations[(durations > 0) & (durations < minimum_period)]
    if not len(durations):
        raise ValueError("at least one duration must be shorter than minimum_period")

    model = BoxLeastSquares(time, flux, dy=flux_err)
    result = model.autopower(
        durations,
        minimum_period=minimum_period,
        maximum_period=maximum_period,
        frequency_factor=frequency_factor,
        objective="snr",
    )
    index = int(np.nanargmax(result.power))
    period = float(result.period[index])
    epoch = float(result.transit_time[index])
    duration = float(result.duration[index])
    depth = float(result.depth[index])
    depth_error = float(result.depth_err[index])
    n_transits = int(np.floor((time.max() - epoch) / period) - np.ceil((time.min() - epoch) / period) + 1)
    signal = TransitSignal(
        period_days=period,
        epoch_days=epoch,
        duration_days=duration,
        depth_fraction=depth,
        depth_error_fraction=depth_error,
        depth_snr=float(depth / depth_error) if depth_error > 0 else float("nan"),
        power=float(result.power[index]),
        n_transits=max(0, n_transits),
    )
    return signal, result
