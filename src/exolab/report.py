"""Candidate scorecards and compact diagnostic figures."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .search import TransitSignal
from .vetting import VettingResult


def write_candidate_report(
    output_dir: str | Path,
    target: str,
    time: np.ndarray,
    flux: np.ndarray,
    signal: TransitSignal,
    vetting: VettingResult,
) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    slug = "".join(character.lower() if character.isalnum() else "-" for character in target).strip("-")

    phase = ((time - signal.epoch_days + 0.5 * signal.period_days) % signal.period_days) / signal.period_days - 0.5
    order = np.argsort(phase)
    figure_path = output / f"{slug}-diagnostic.png"
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), constrained_layout=True)
    axes[0].plot(time, flux, ".", ms=2, alpha=0.45, color="#5072a7")
    axes[0].set(xlabel="Time [days]", ylabel="Normalized flux", title=f"{target}: searched light curve")
    axes[1].plot(phase[order], flux[order], ".", ms=3, alpha=0.55, color="#7b2cbf")
    axes[1].axvspan(
        -signal.duration_days / signal.period_days / 2,
        signal.duration_days / signal.period_days / 2,
        color="#ffb703",
        alpha=0.2,
    )
    axes[1].set(xlabel="Orbital phase", ylabel="Normalized flux", title="Phase-folded candidate")
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)

    payload = {
        "target": target,
        "classification": "unvalidated transit-like signal",
        "signal": signal.as_dict(),
        "vetting": vetting.as_dict(),
        "warning": "This scorecard is not a planet confirmation or statistical validation.",
    }
    json_path = output / f"{slug}-candidate.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return figure_path, json_path
