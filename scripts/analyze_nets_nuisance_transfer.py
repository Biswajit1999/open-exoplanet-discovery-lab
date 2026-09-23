"""Quantify signal attenuation from sequential per-run de-meaning in NETS III.

This experiment uses the actual public NETS III timestamps, formal errors and
published Run labels. It injects a unit circular signal, removes each run's
weighted mean as a preprocessing step, and measures the recovered amplitude at
the known period. The result is a transfer function for *sequential de-meaning*,
not a substitute for a joint era-offset + Keplerian likelihood.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from exolab.nuisance import group_demean_sinusoid_transfer


DEFAULT_PERIODS = [5.0, 10.0, 30.0, 100.0, 300.0, 600.0, 1000.0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rv",
        default="outputs/public_snapshot/nets3_j_aj_170_264_fig8.csv",
    )
    parser.add_argument("--output", default="outputs/nets_nuisance_transfer")
    parser.add_argument(
        "--periods",
        nargs="*",
        type=float,
        default=DEFAULT_PERIODS,
    )
    parser.add_argument("--phases", type=int, default=16)
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(args.rv)
    required = {"Star", "BJD", "e_RVel", "Run"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"NETS III RV table missing columns {sorted(missing)}")

    frame["BJD"] = pd.to_numeric(frame["BJD"], errors="coerce")
    frame["error_mps"] = pd.to_numeric(frame["e_RVel"], errors="coerce") * 1000.0
    phases = np.linspace(0.0, 2.0 * np.pi, int(args.phases), endpoint=False)

    rows: list[dict[str, object]] = []
    for star, group in frame.groupby("Star", sort=True):
        group = group.dropna(subset=["BJD", "error_mps", "Run"]).copy()
        group = group[group["error_mps"] > 0].sort_values("BJD")
        if len(group) < 5:
            continue
        time = group["BJD"].to_numpy(dtype=float)
        error = group["error_mps"].to_numpy(dtype=float)
        run = group["Run"].astype(str).to_numpy()

        for period in args.periods:
            transfer = group_demean_sinusoid_transfer(
                time,
                error,
                run,
                float(period),
                phases=phases,
            )
            rows.append(
                {
                    "Star": star,
                    "period_days": float(period),
                    "n_epochs": int(len(group)),
                    "n_runs": int(group["Run"].nunique()),
                    "median_recovered_k_over_injected_k": transfer.median_ratio,
                    "worst_phase_recovered_k_over_injected_k": transfer.worst_phase_ratio,
                    "best_phase_recovered_k_over_injected_k": transfer.best_phase_ratio,
                }
            )

    target_table = pd.DataFrame(rows)
    target_table.to_csv(output / "nets3_nuisance_transfer_by_target.csv", index=False)

    aggregate_rows: list[dict[str, object]] = []
    for period, group in target_table.groupby("period_days", sort=True):
        median_ratio = group["median_recovered_k_over_injected_k"]
        worst_ratio = group["worst_phase_recovered_k_over_injected_k"]
        aggregate_rows.append(
            {
                "period_days": float(period),
                "n_targets": int(len(group)),
                "median_of_phase_median_ratio": float(median_ratio.median()),
                "p10_of_phase_median_ratio": float(median_ratio.quantile(0.10)),
                "p90_of_phase_median_ratio": float(median_ratio.quantile(0.90)),
                "median_of_worst_phase_ratio": float(worst_ratio.median()),
                "p10_of_worst_phase_ratio": float(worst_ratio.quantile(0.10)),
                "targets_median_loss_gt_10pct": int((median_ratio < 0.90).sum()),
                "targets_median_loss_gt_20pct": int((median_ratio < 0.80).sum()),
                "targets_worst_phase_loss_gt_20pct": int((worst_ratio < 0.80).sum()),
                "targets_worst_phase_loss_gt_50pct": int((worst_ratio < 0.50).sum()),
            }
        )

    aggregate = pd.DataFrame(aggregate_rows)
    aggregate.to_csv(output / "nets3_nuisance_transfer_population.csv", index=False)

    summary = {
        "experiment": "Sequential weighted per-run de-meaning transfer function",
        "targets": int(target_table["Star"].nunique()),
        "periods_days": [float(value) for value in args.periods],
        "phases_per_period": int(args.phases),
        "important_scope_note": (
            "This quantifies signal attenuation caused by preprocessing each run "
            "independently. It is not the transfer function of a simultaneous "
            "Keplerian + run-offset likelihood, which must be evaluated separately."
        ),
        "population": aggregate.to_dict(orient="records"),
    }
    (output / "nets3_nuisance_transfer_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
