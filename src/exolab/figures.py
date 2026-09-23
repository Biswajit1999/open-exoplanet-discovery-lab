"""Canonical static figures for papers, reports and archival releases."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(fig: plt.Figure, path: str | Path | None) -> plt.Figure:
    if path is not None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=200, bbox_inches="tight")
    return fig


def plot_rv_timeseries(
    time: Iterable[float],
    rv: Iterable[float],
    error: Iterable[float],
    *,
    groups: Iterable[str] | None = None,
    title: str = "Radial velocity time series",
    path: str | Path | None = None,
) -> plt.Figure:
    t = np.asarray(time, dtype=float)
    y = np.asarray(rv, dtype=float)
    e = np.asarray(error, dtype=float)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    if groups is None:
        ax.errorbar(t, y, yerr=e, fmt=".", capsize=0, alpha=0.85)
    else:
        g = np.asarray(list(groups), dtype=object)
        for label in sorted({str(x) for x in g}):
            mask = g.astype(str) == label
            ax.errorbar(t[mask], y[mask], yerr=e[mask], fmt=".", capsize=0, alpha=0.85, label=label)
        ax.legend(frameon=False, fontsize=8)
    ax.set_xlabel("Time [days]")
    ax.set_ylabel("Radial velocity [m s$^{-1}$]")
    ax.set_title(title)
    ax.grid(alpha=0.2)
    return _save(fig, path)


def plot_periodogram(
    period: Iterable[float],
    power: Iterable[float],
    *,
    best_period: float | None = None,
    title: str = "Generalized Lomb–Scargle periodogram",
    path: str | Path | None = None,
) -> plt.Figure:
    p = np.asarray(period, dtype=float)
    z = np.asarray(power, dtype=float)
    order = np.argsort(p)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.plot(p[order], z[order], lw=1.1)
    if best_period is not None:
        ax.axvline(float(best_period), ls="--", lw=1)
    ax.set_xscale("log")
    ax.set_xlabel("Period [days]")
    ax.set_ylabel("Power")
    ax.set_title(title)
    ax.grid(alpha=0.2)
    return _save(fig, path)


def plot_completeness(
    table: pd.DataFrame,
    *,
    value_column: str = "completeness",
    path: str | Path | None = None,
) -> plt.Figure:
    required = {"period", "semi_amplitude", value_column}
    if not required.issubset(table.columns):
        raise ValueError(f"completeness table must contain {sorted(required)}")
    pivot = table.pivot(index="semi_amplitude", columns="period", values=value_column)
    x = pivot.columns.to_numpy(dtype=float)
    y = pivot.index.to_numpy(dtype=float)
    z = pivot.to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    image = ax.pcolormesh(x, y, z, shading="auto", vmin=0.0, vmax=1.0)
    ax.set_xscale("log")
    ax.set_xlabel("Period [days]")
    ax.set_ylabel("Semi-amplitude K [m s$^{-1}$]")
    ax.set_title("Injection–recovery completeness")
    fig.colorbar(image, ax=ax, label="Recovery fraction")
    return _save(fig, path)


def plot_chromatic_amplitudes(
    labels: Iterable[str],
    optical_k: Iterable[float],
    optical_error: Iterable[float],
    nir_k: Iterable[float],
    nir_error: Iterable[float],
    *,
    path: str | Path | None = None,
) -> plt.Figure:
    names = list(labels)
    ko = np.asarray(optical_k, dtype=float)
    eo = np.asarray(optical_error, dtype=float)
    kn = np.asarray(nir_k, dtype=float)
    en = np.asarray(nir_error, dtype=float)
    index = np.arange(len(names), dtype=float)
    fig, ax = plt.subplots(figsize=(max(7.5, len(names) * 0.55), 4.8))
    ax.errorbar(index - 0.08, ko, yerr=eo, fmt="o", label="Optical")
    ax.errorbar(index + 0.08, kn, yerr=en, fmt="o", label="Near-IR")
    ax.set_xticks(index, names, rotation=45, ha="right")
    ax.set_ylabel("Semi-amplitude K [m s$^{-1}$]")
    ax.set_title("Optical / near-infrared signal coherence")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    return _save(fig, path)


def plot_repeatability(
    labels: Iterable[str],
    value: Iterable[float],
    error: Iterable[float],
    *,
    mean: float | None = None,
    extra_scatter: float | None = None,
    unit: str = "",
    path: str | Path | None = None,
) -> plt.Figure:
    names = list(labels)
    y = np.asarray(value, dtype=float)
    e = np.asarray(error, dtype=float)
    index = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.errorbar(index, y, yerr=e, fmt="o", capsize=3)
    if mean is not None:
        ax.axhline(float(mean), lw=1)
        if extra_scatter is not None and extra_scatter > 0:
            ax.axhspan(float(mean) - float(extra_scatter), float(mean) + float(extra_scatter), alpha=0.12)
    ax.set_xticks(index, names, rotation=35, ha="right")
    ax.set_ylabel(f"Measurement{f' [{unit}]' if unit else ''}")
    ax.set_title("Repeated-measurement reproducibility")
    ax.grid(axis="y", alpha=0.2)
    return _save(fig, path)
