"""Run the public NETS III robustness and circular-completeness experiment.

The three compared pipelines are:
  baseline       one global offset;
  era            published Run offsets plus per-run white jitter;
  era_activity   Run offsets, linear S-index term and per-run white jitter.

All recovery thresholds are calibrated from deterministic residual
permutations. The outputs are sensitivity measurements, not planet claims.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from exolab.nets import (
    calibrated_power_threshold,
    completeness_contours,
    effective_errors,
    fit_group_jitters,
    project_nuisance,
    projected_signal_transfer,
    run_model_completeness,
)
from exolab.periodogram import generalized_lomb_scargle, spectral_window
from exolab.provenance import canonical_json_sha256, sha256_file


def slug(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def numeric(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.copy()
    for column in columns:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    return result


def target_diagnostic_figure(
    target: str,
    time: np.ndarray,
    rv: np.ndarray,
    error: np.ndarray,
    run: np.ndarray,
    activity: np.ndarray,
    path: Path,
) -> dict[str, float]:
    residual = project_nuisance(rv, error, groups=run, activity=activity).residuals
    maximum = min(500.0, max(3.0, float(np.ptp(time)) * 0.8))
    rv_gls = generalized_lomb_scargle(
        time, residual, error, min_period=2.0, max_period=maximum
    )
    activity_error = np.full_like(activity, max(float(np.std(activity)), 1e-6))
    activity_gls = generalized_lomb_scargle(
        time, activity, activity_error, min_period=2.0, max_period=maximum
    )
    window_period, window_power = spectral_window(
        time, min_period=2.0, max_period=maximum, n_frequency=2500
    )

    figure, axes = plt.subplots(2, 2, figsize=(10.5, 7.2))
    for label in sorted(set(run.tolist())):
        mask = run == label
        axes[0, 0].errorbar(
            time[mask] - np.min(time),
            rv[mask],
            yerr=error[mask],
            fmt=".",
            ms=3,
            alpha=0.75,
            label=label,
        )
    axes[0, 0].set(xlabel="Time since first epoch [d]", ylabel="RV [m s$^{-1}$]")
    axes[0, 0].legend(frameon=False, fontsize=7)
    axes[0, 1].plot(window_period, window_power, color="#c47f17", lw=1)
    axes[0, 1].set(xscale="log", xlabel="Period [d]", ylabel="Window power")
    axes[1, 0].plot(rv_gls.period, rv_gls.power, color="#168f9d", lw=1)
    axes[1, 0].set(xscale="log", xlabel="Period [d]", ylabel="RV GLS power")
    axes[1, 1].plot(activity_gls.period, activity_gls.power, color="#7b6fb2", lw=1)
    axes[1, 1].set(xscale="log", xlabel="Period [d]", ylabel="S-index GLS power")
    for axis in axes.ravel():
        axis.grid(alpha=0.18)
    figure.suptitle(f"{target} · public NETS III diagnostics")
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return {
        "rv_gls_best_period_days": rv_gls.best_period,
        "rv_gls_best_power": rv_gls.best_power,
        "rv_gls_analytic_fap": rv_gls.false_alarm_probability,
        "activity_gls_best_period_days": activity_gls.best_period,
        "activity_gls_best_power": activity_gls.best_power,
        "activity_gls_analytic_fap": activity_gls.false_alarm_probability,
    }


def plot_population(
    population: pd.DataFrame,
    delta: pd.DataFrame,
    contours: pd.DataFrame,
    output: Path,
) -> None:
    models = ["baseline", "era_activity"]
    figure, axes = plt.subplots(1, 3, figsize=(15.2, 4.5), sharey=True)
    for axis, model in zip(axes[:2], models):
        table = population[population["model"] == model]
        pivot = table.pivot(
            index="semi_amplitude", columns="period", values="mean_completeness"
        )
        mesh = axis.pcolormesh(
            pivot.columns,
            pivot.index,
            pivot.values,
            shading="nearest",
            vmin=0,
            vmax=1,
            cmap="viridis",
        )
        axis.set_title(model.replace("_", " ").title())
        axis.set(xscale="log", xlabel="Period [d]")
    delta_pivot = delta.pivot(
        index="semi_amplitude", columns="period", values="delta_completeness"
    )
    limit = max(0.05, float(np.nanmax(np.abs(delta_pivot.values))))
    delta_mesh = axes[2].pcolormesh(
        delta_pivot.columns,
        delta_pivot.index,
        delta_pivot.values,
        shading="nearest",
        vmin=-limit,
        vmax=limit,
        cmap="coolwarm",
    )
    axes[2].set(title="Era + activity − baseline", xscale="log", xlabel="Period [d]")
    axes[0].set_ylabel("Injected K [m s$^{-1}$]")
    figure.colorbar(mesh, ax=axes[:2], label="Mean recovery fraction", fraction=0.025)
    figure.colorbar(delta_mesh, ax=axes[2], label="Δ completeness", fraction=0.08)
    figure.suptitle("NETS III circular injection–recovery · permutation-calibrated")
    figure.subplots_adjust(left=0.06, right=0.94, bottom=0.16, top=0.84, wspace=0.22)
    figure.savefig(output / "nets3_population_completeness.png", dpi=220)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8.2, 5.0))
    for model, style in (("baseline", "--"), ("era", ":"), ("era_activity", "-")):
        table = contours[contours["model"] == model].sort_values("period")
        axis.plot(table["period"], table["k50"], style, marker="o", label=f"{model} K50")
        axis.plot(table["period"], table["k90"], style, marker="s", alpha=0.7, label=f"{model} K90")
    axis.set(xscale="log", xlabel="Period [d]", ylabel="K threshold [m s$^{-1}$]")
    axis.grid(alpha=0.2)
    axis.legend(frameon=False, ncol=2, fontsize=8)
    axis.set_title("Population mean K50 and K90")
    figure.tight_layout()
    figure.savefig(output / "nets3_k50_k90.png", dpi=220)
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rv", default="outputs/public_snapshot/nets3_j_aj_170_264_fig8.csv"
    )
    parser.add_argument(
        "--activity", default="outputs/public_snapshot/nets3_j_aj_170_264_fig2.csv"
    )
    parser.add_argument("--output", default="outputs/nets3_completeness")
    parser.add_argument(
        "--periods", nargs="*", type=float, default=[5, 10, 30, 100, 300, 500]
    )
    parser.add_argument(
        "--amplitudes", nargs="*", type=float, default=[0.5, 1, 1.5, 2, 3, 5]
    )
    parser.add_argument("--phases", type=int, default=6)
    parser.add_argument("--permutations", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260923)
    parser.add_argument("--software-commit", default="working-tree")
    parser.add_argument("--max-targets", type=int, default=0)
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    rv = numeric(pd.read_csv(args.rv), ["BJD", "RVel", "e_RVel"])
    activity = numeric(pd.read_csv(args.activity), ["BJD", "SHK", "e_SHK"])
    merged = rv.merge(
        activity[["Star", "BJD", "SHK", "e_SHK"]],
        on=["Star", "BJD"],
        how="left",
        validate="one_to_one",
    )
    merged["rv_mps"] = merged["RVel"] * 1000.0
    merged["erv_mps"] = merged["e_RVel"] * 1000.0
    merged = merged.dropna(subset=["Star", "BJD", "rv_mps", "erv_mps", "Run"])
    merged = merged[merged["erv_mps"] > 0]

    periods = np.asarray(args.periods, dtype=float)
    amplitudes = np.asarray(args.amplitudes, dtype=float)
    phases = np.linspace(0, 2 * np.pi, int(args.phases), endpoint=False)
    configuration = {
        "periods_days": periods.tolist(),
        "semi_amplitudes_mps": amplitudes.tolist(),
        "phases": phases.tolist(),
        "permutations": int(args.permutations),
        "seed": int(args.seed),
        "false_alarm_probability": 0.01,
        "period_tolerance_fraction": 0.05,
        "harmonics": [0.5, 1.0, 2.0],
    }
    (output / "analysis_configuration.json").write_text(
        json.dumps(configuration, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    grids: list[pd.DataFrame] = []
    target_rows: list[dict[str, object]] = []
    jitter_rows: list[dict[str, object]] = []
    heldout_rows: list[dict[str, object]] = []
    diagnostic_rows: list[dict[str, object]] = []

    grouped_targets = list(merged.groupby("Star", sort=True))
    if args.max_targets > 0:
        grouped_targets = grouped_targets[: args.max_targets]
    for target_index, (target, frame) in enumerate(grouped_targets):
        frame = frame.sort_values("BJD").dropna(subset=["SHK"])
        if len(frame) < 20:
            continue
        time = frame["BJD"].to_numpy(float)
        values = frame["rv_mps"].to_numpy(float)
        formal_error = frame["erv_mps"].to_numpy(float)
        run = frame["Run"].astype(str).to_numpy()
        indicator = frame["SHK"].to_numpy(float)
        min_period = max(2.0, float(np.min(periods)) * 0.5)
        max_period = min(max(float(np.max(periods)) * 1.2, 10.0), float(np.ptp(time)) * 0.9)

        definitions = {
            "baseline": {"groups": None, "activity": None},
            "era": {"groups": run, "activity": None},
            "era_activity": {"groups": run, "activity": indicator},
        }
        thresholds: dict[str, float] = {}
        for model_index, (model_name, definition) in enumerate(definitions.items()):
            base = project_nuisance(
                values,
                formal_error,
                groups=definition["groups"],
                activity=definition["activity"],
            ).residuals
            jitter_groups = np.array(["all"] * len(run)) if model_name == "baseline" else run
            jitters = fit_group_jitters(base, formal_error, jitter_groups)
            error = effective_errors(formal_error, jitter_groups, jitters)
            threshold = calibrated_power_threshold(
                time,
                base,
                error,
                min_period=min_period,
                max_period=max_period,
                n_permutations=int(args.permutations),
                seed=int(args.seed + target_index * 101 + model_index),
            )
            thresholds[model_name] = threshold
            grid = run_model_completeness(
                time,
                base,
                error,
                periods=periods,
                amplitudes=amplitudes,
                phases=phases,
                min_period=min_period,
                max_period=max_period,
                power_threshold=threshold,
                groups=definition["groups"],
                activity=definition["activity"],
            )
            grid.insert(0, "model", model_name)
            grid.insert(0, "target", str(target))
            grids.append(grid)
            for label, jitter in jitters.items():
                jitter_rows.append(
                    {"target": str(target), "model": model_name, "run": label, "jitter_mps": jitter}
                )

        for heldout in sorted(set(run.tolist())):
            keep = run != heldout
            if np.count_nonzero(keep) < 20:
                continue
            for period in periods:
                ratio = projected_signal_transfer(
                    time[keep],
                    formal_error[keep],
                    float(period),
                    phases,
                    groups=run[keep],
                    activity=indicator[keep],
                )
                heldout_rows.append(
                    {
                        "target": str(target),
                        "held_out_run": heldout,
                        "n_retained": int(np.count_nonzero(keep)),
                        "period": float(period),
                        "median_k_transfer": float(np.median(ratio)),
                        "worst_phase_k_transfer": float(np.min(ratio)),
                    }
                )

        target_rows.append(
            {
                "target": str(target),
                "n_observations": int(len(frame)),
                "n_runs": int(len(set(run.tolist()))),
                "baseline_days": float(np.ptp(time)),
                "median_formal_error_mps": float(np.median(formal_error)),
                **{f"{name}_power_threshold": value for name, value in thresholds.items()},
            }
        )
        diagnostics = target_diagnostic_figure(
            str(target),
            time,
            values,
            formal_error,
            run,
            indicator,
            output / "figures" / "targets" / f"{slug(target)}.png",
        )
        diagnostic_rows.append({"target": str(target), **diagnostics})

    all_grids = pd.concat(grids, ignore_index=True)
    all_grids.to_csv(output / "target_completeness.csv", index=False)
    pd.DataFrame(target_rows).to_csv(output / "target_summary.csv", index=False)
    pd.DataFrame(jitter_rows).to_csv(output / "per_run_jitter.csv", index=False)
    pd.DataFrame(heldout_rows).to_csv(output / "leave_one_era_out_transfer.csv", index=False)
    pd.DataFrame(diagnostic_rows).to_csv(output / "periodogram_summary.csv", index=False)

    population = (
        all_grids.groupby(["model", "period", "semi_amplitude"], as_index=False)
        .agg(
            mean_completeness=("completeness", "mean"),
            median_completeness=("completeness", "median"),
            n_targets=("target", "nunique"),
        )
    )
    population.to_csv(output / "population_completeness.csv", index=False)
    pivot = population.pivot(
        index=["period", "semi_amplitude"], columns="model", values="mean_completeness"
    ).reset_index()
    delta = pivot[["period", "semi_amplitude"]].copy()
    delta["delta_completeness"] = pivot["era_activity"] - pivot["baseline"]
    delta.to_csv(output / "delta_completeness.csv", index=False)

    contour_frames = []
    for model, table in population.groupby("model", sort=True):
        renamed = table.rename(columns={"mean_completeness": "completeness"})
        contours = completeness_contours(renamed)
        contours.insert(0, "model", model)
        contour_frames.append(contours)
    contours = pd.concat(contour_frames, ignore_index=True)
    contours.to_csv(output / "population_k50_k90.csv", index=False)
    plot_population(population, delta, contours, output / "figures")

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "software_commit": args.software_commit,
        "configuration_hash": canonical_json_sha256(configuration),
        "targets": int(all_grids["target"].nunique()),
        "observations": int(sum(row["n_observations"] for row in target_rows)),
        "models": ["baseline", "era", "era_activity"],
        "grid_cells_per_model": int(len(periods) * len(amplitudes)),
        "injections_per_cell": int(len(phases)),
        "permutations_per_target_model": int(args.permutations),
        "mean_delta_completeness": float(delta["delta_completeness"].mean()),
        "max_absolute_delta_completeness": float(delta["delta_completeness"].abs().max()),
        "interpretation": (
            "Circular injection/recovery sensitivity under three declared nuisance models. "
            "Recovered periodicity is not classified as a planet."
        ),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checksums = {
        path.relative_to(output).as_posix(): sha256_file(path)
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "checksums.json"
    }
    (output / "checksums.json").write_text(
        json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
