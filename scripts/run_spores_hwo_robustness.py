"""Run the SPORES-HWO II habitable-zone robustness experiment.

The experiment is deliberately restricted to a pre-declared control sample:
targets with a published HZ sensitivity row, at least 150 valid nightly RVs,
at least two instruments, and no signal listed in catalogue table 6.  It asks
how the middle-HZ K50/K90 changes under instrument offsets, a
correlation-preserving null, eccentric injections, and dominant-instrument
removal.  It is a sensitivity analysis, not a new signal search.
"""

from __future__ import annotations

import argparse
from concurrent.futures import Future, ProcessPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from exolab.provenance import canonical_json_sha256, sha256_file
from exolab.spores import (
    calibrated_group_power_threshold,
    clean_spores_rv,
    completeness_threshold_with_status,
    effective_group_errors,
    nightly_bin_spores_rv,
    orbital_draws,
    project_spores_nuisance,
    run_hz_injection_grid,
)


MODEL_ORDER = [
    "global_white_circular",
    "instrument_white_circular",
    "instrument_correlated_circular",
    "instrument_correlated_eccentric",
    "leave_dominant_correlated_circular",
]


def target_name(value: object) -> str:
    return str(value).strip()


def hd_number(value: object) -> str | None:
    match = re.search(r"(?:HD\s*)?(\d+)", str(value), flags=re.IGNORECASE)
    return None if match is None else match.group(1)


def trend_degree_for_target(trends: pd.DataFrame, target: str) -> int:
    row = trends[trends["target"] == target]
    if row.empty:
        return 0
    quadratic = float(pd.to_numeric(row.iloc[0]["gammaDdot"], errors="coerce") or 0.0)
    linear = float(pd.to_numeric(row.iloc[0]["gammadot"], errors="coerce") or 0.0)
    if np.isfinite(quadratic) and quadratic != 0.0:
        return 2
    if np.isfinite(linear) and linear != 0.0:
        return 1
    return 0


def fit_base(
    frame: pd.DataFrame,
    *,
    instrument_aware: bool,
    trend_degree: int,
) -> dict[str, object]:
    time = frame["bjd"].to_numpy(float)
    rv = frame["rv_mps"].to_numpy(float)
    formal = frame["rv_error_mps"].to_numpy(float)
    instruments = frame["instrument"].astype(str).to_numpy()
    nuisance_instruments = instruments if instrument_aware else None
    fitted = project_spores_nuisance(
        time,
        rv,
        formal,
        instruments=nuisance_instruments,
        trend_degree=trend_degree if instrument_aware else 0,
    )
    jitter_groups = instruments if instrument_aware else np.repeat("all", len(frame))
    effective, jitters = effective_group_errors(
        fitted.residuals, formal, jitter_groups
    )
    return {
        "time": time,
        "residuals": fitted.residuals,
        "errors": effective,
        "instruments": nuisance_instruments,
        "null_groups": jitter_groups,
        "jitters": jitters,
        "residual_rms_mps": float(np.sqrt(np.mean(np.square(fitted.residuals)))),
        "trend_degree": trend_degree if instrument_aware else 0,
    }


def one_model(
    frame: pd.DataFrame,
    *,
    period_days: float,
    amplitudes: np.ndarray,
    draws: pd.DataFrame,
    instrument_aware: bool,
    trend_degree: int,
    null: str,
    permutations: int,
    seed: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    base = fit_base(
        frame,
        instrument_aware=instrument_aware,
        trend_degree=trend_degree,
    )
    minimum = 2.0
    maximum = min(
        float(np.ptp(base["time"])) * 0.9,
        max(float(period_days) * 2.0, 30.0),
    )
    threshold = calibrated_group_power_threshold(
        base["time"],
        base["residuals"],
        base["errors"],
        base["null_groups"],
        min_period=minimum,
        max_period=maximum,
        n_permutations=int(permutations),
        seed=int(seed),
        null=null,
    )
    grid = run_hz_injection_grid(
        base["time"],
        base["residuals"],
        base["errors"],
        base["instruments"],
        period=float(period_days),
        amplitudes=amplitudes,
        draws=draws,
        trend_degree=int(base["trend_degree"]),
        power_threshold=threshold,
        min_period=minimum,
        max_period=maximum,
    )
    diagnostics = {
        "power_threshold": float(threshold),
        "residual_rms_mps": base["residual_rms_mps"],
        "trend_degree": int(base["trend_degree"]),
        "jitters_mps": base["jitters"],
    }
    return grid, diagnostics


def plot_published_sensitivity(sample: pd.DataFrame, output: Path) -> None:
    figure, axis = plt.subplots(figsize=(8.8, 5.4))
    scatter = axis.scatter(
        sample["n_nights"],
        sample["published_k50_mps"],
        c=np.log10(sample["baseline_days"] / 365.25),
        s=35 + 12 * sample["n_instruments"],
        cmap="viridis",
        edgecolor="white",
        linewidth=0.5,
    )
    axis.set(
        xscale="log",
        yscale="log",
        xlabel="Valid nightly RV epochs",
        ylabel="Published middle-HZ K50 [m s$^{-1}$]",
        title="SPORES-HWO II control sample · published sensitivity context",
    )
    axis.grid(alpha=0.2, which="both")
    color = figure.colorbar(scatter, ax=axis)
    color.set_label("log$_{10}$ baseline [yr]")
    figure.tight_layout()
    figure.savefig(output, dpi=220)
    plt.close(figure)


def plot_k50_robustness(thresholds: pd.DataFrame, output: Path) -> None:
    pivot = thresholds.pivot(index="target", columns="model", values="k50_mps")
    reference = pivot["instrument_correlated_circular"]
    ratio = pivot.div(reference, axis=0)
    models = MODEL_ORDER
    figure, axis = plt.subplots(figsize=(10.4, 5.5))
    for row in ratio.itertuples():
        axis.plot(
            range(len(models)),
            [getattr(row, model) for model in models],
            color="#7a8791",
            alpha=0.28,
            linewidth=0.8,
        )
    medians = [float(ratio[model].median()) for model in models]
    axis.plot(
        range(len(models)),
        medians,
        color="#0b7785",
        marker="o",
        linewidth=2.4,
        label="sample median",
    )
    axis.axhline(1.0, color="#202d38", linewidth=1, linestyle="--")
    axis.set_xticks(range(len(models)))
    axis.set_xticklabels(
        [
            "global\nwhite",
            "instrument\nwhite",
            "instrument\ncorrelated",
            "eccentric\ncorrelated",
            "remove dominant\ninstrument",
        ]
    )
    axis.set(
        ylabel="K50 / instrument-correlated circular K50",
        title="Middle-HZ sensitivity changes when assumptions change",
    )
    axis.grid(alpha=0.2, axis="y")
    axis.legend(frameon=False)
    figure.tight_layout()
    figure.savefig(output, dpi=220)
    plt.close(figure)


def plot_population_distribution(thresholds: pd.DataFrame, output: Path) -> None:
    values = [
        thresholds.loc[thresholds["model"] == model, "k50_mps"].dropna().to_numpy()
        for model in MODEL_ORDER
    ]
    figure, axis = plt.subplots(figsize=(10.2, 5.3))
    boxes = axis.boxplot(values, patch_artist=True, showfliers=False)
    colors = ["#d7d6cc", "#a8d6d8", "#55aeb5", "#d8a14b", "#bd7067"]
    for patch, color in zip(boxes["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.82)
    axis.set_yscale("log")
    axis.set_xticklabels(
        ["global\nwhite", "instrument\nwhite", "instrument\ncorrelated", "eccentric\ncorrelated", "remove dominant\ninstrument"]
    )
    axis.set(
        ylabel="Middle-HZ K50 [m s$^{-1}$]",
        title="Control-sample sensitivity distribution",
    )
    axis.grid(alpha=0.2, axis="y", which="both")
    figure.tight_layout()
    figure.savefig(output, dpi=220)
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/census/spores_hwo_2026-10-12")
    parser.add_argument("--output", default="outputs/spores_hwo_robustness")
    parser.add_argument("--min-nights", type=int, default=150)
    parser.add_argument("--draws", type=int, default=8)
    parser.add_argument("--permutations", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261012)
    parser.add_argument("--max-targets", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--software-commit", default="working-tree")
    args = parser.parse_args()

    source = Path(args.input)
    output = Path(args.output)
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    table3 = pd.read_csv(source / "table3.csv")
    table5 = pd.read_csv(source / "table5.csv", low_memory=False)
    table6 = pd.read_csv(source / "table6.csv")
    table7 = pd.read_csv(source / "table7.csv")
    table9 = pd.read_csv(source / "table9.csv")
    nea = pd.read_csv(source / "nasa_confirmed_planets_with_hd.csv")
    acquisition = json.loads((source / "acquisition_summary.json").read_text(encoding="utf-8"))
    shutil.copy2(source / "acquisition_summary.json", output / "source_acquisition_summary.json")
    shutil.copy2(source / "manifest.json", output / "source_manifest.json")

    for frame in (table3, table6, table7, table9):
        frame["target"] = frame["HD"].map(target_name)
    clean, qc = clean_spores_rv(table5)
    nightly = nightly_bin_spores_rv(table5)
    target_metrics = (
        nightly.groupby("target", as_index=False)
        .agg(
            n_nights=("night", "size"),
            n_instruments=("instrument", "nunique"),
            baseline_days=("bjd", lambda value: float(value.max() - value.min())),
            median_formal_error_mps=("rv_error_mps", "median"),
        )
    )

    hz = table9.copy()
    numeric_hz = ["PerMHZ", "MpMHZ", "E_MpMHZ", "KMHZ", "E_KMHZ"]
    for column in numeric_hz:
        hz[column] = pd.to_numeric(hz[column], errors="coerce")
    hz["mhz_period_days"] = hz["PerMHZ"] * 365.25
    signal_targets = set(table6["target"])
    sample = target_metrics.merge(
        hz[["target", "mhz_period_days", "MpMHZ", "E_MpMHZ", "KMHZ", "E_KMHZ"]],
        on="target",
        how="left",
        validate="one_to_one",
    )
    sample["has_catalogued_signal"] = sample["target"].isin(signal_targets)
    sample["selection_status"] = "excluded"
    sample["exclusion_reason"] = ""
    sample.loc[sample["KMHZ"].isna(), "exclusion_reason"] = "no table9 HZ sensitivity row"
    sample.loc[
        sample["KMHZ"].notna() & (sample["n_nights"] < args.min_nights),
        "exclusion_reason",
    ] = f"fewer than {args.min_nights} valid nightly RVs"
    sample.loc[
        sample["KMHZ"].notna()
        & (sample["n_nights"] >= args.min_nights)
        & (sample["n_instruments"] < 2),
        "exclusion_reason",
    ] = "fewer than two instruments"
    sample.loc[
        sample["KMHZ"].notna()
        & (sample["n_nights"] >= args.min_nights)
        & (sample["n_instruments"] >= 2)
        & sample["has_catalogued_signal"],
        "exclusion_reason",
    ] = "signal listed in VizieR table6"
    selected = (
        sample["KMHZ"].notna()
        & (sample["n_nights"] >= args.min_nights)
        & (sample["n_instruments"] >= 2)
        & ~sample["has_catalogued_signal"]
    )
    sample.loc[selected, "selection_status"] = "included"
    sample.loc[selected, "exclusion_reason"] = ""
    sample = sample.rename(
        columns={
            "KMHZ": "published_k50_mps",
            "E_KMHZ": "published_k90_mps",
            "MpMHZ": "published_m50_earth",
            "E_MpMHZ": "published_m90_earth",
        }
    )

    selected_targets = sample.loc[selected].sort_values("target")["target"].tolist()
    if args.max_targets > 0:
        selected_targets = selected_targets[: args.max_targets]
        sample.loc[
            (sample["selection_status"] == "included")
            & ~sample["target"].isin(selected_targets),
            ["selection_status", "exclusion_reason"],
        ] = ["excluded", "max-targets development cap"]
    selected_sample = sample[sample["target"].isin(selected_targets)].copy()

    nea["hd_key"] = nea["hd_name"].map(hd_number)
    table3["hd_key"] = table3["target"].map(hd_number)
    nea_context = (
        nea.dropna(subset=["hd_key"])
        .groupby("hd_key", as_index=False)
        .agg(
            nasa_confirmed_planets=("pl_name", "nunique"),
            nasa_planet_names=("pl_name", lambda value: ";".join(sorted(set(map(str, value))))),
            nasa_discovery_methods=("discoverymethod", lambda value: ";".join(sorted(set(map(str, value))))),
        )
    )
    target_context = table3[["target", "OName1", "OName2", "Teff", "_RA", "_DE", "hd_key"]].merge(
        nea_context, on="hd_key", how="left", validate="many_to_one"
    )
    target_context["nasa_confirmed_planets"] = target_context["nasa_confirmed_planets"].fillna(0).astype(int)
    target_context.to_csv(output / "target_archive_context.csv", index=False)

    configuration = {
        "catalog": "J/AJ/170/343",
        "selection": {
            "minimum_valid_nightly_rvs": int(args.min_nights),
            "minimum_instruments": 2,
            "requires_table9_hz_row": True,
            "requires_no_table6_signal": True,
        },
        "quality": "finite BJD/RVel/e_RVel; catalogue -1 sentinels excluded; e_RVel > 0",
        "nightly_bin": "inverse-variance mean within target/instrument/floor(BJD)",
        "amplitude_multipliers_of_published_k50": [
            0.25,
            0.5,
            0.75,
            1.0,
            1.5,
            2.0,
            3.0,
            5.0,
            8.0,
            12.0,
            20.0,
        ],
        "orbital_draws": int(args.draws),
        "eccentricity_distribution": {"family": "Beta", "a": 0.867, "b": 3.03, "reference": "Kipping 2013, MNRAS 434, L51"},
        "null_calibration": {
            "permutations": int(args.permutations),
            "false_alarm_probability": 0.01,
            "white": "within-instrument standardized-residual permutation",
            "correlated": "within-instrument time-ordered circular shift",
        },
        "recovery": {"period_tolerance_fraction": 0.05, "harmonics": [0.5, 1.0, 2.0]},
        "seed": int(args.seed),
    }
    (output / "analysis_configuration.json").write_text(
        json.dumps(configuration, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    grids: list[pd.DataFrame] = []
    threshold_rows: list[dict[str, object]] = []
    jitter_rows: list[dict[str, object]] = []
    executor = ProcessPoolExecutor(max_workers=args.jobs) if args.jobs > 1 else None
    for target_index, target in enumerate(selected_targets):
        print(f"[{target_index + 1}/{len(selected_targets)}] {target}", flush=True)
        frame = nightly[nightly["target"] == target].sort_values("bjd").reset_index(drop=True)
        meta = selected_sample[selected_sample["target"] == target].iloc[0]
        period = float(meta["mhz_period_days"])
        published_k50 = float(meta["published_k50_mps"])
        amplitudes = published_k50 * np.asarray(configuration["amplitude_multipliers_of_published_k50"], dtype=float)
        amplitudes = np.unique(np.round(amplitudes, 6))
        degree = trend_degree_for_target(table7, target)
        circular = orbital_draws(args.draws, seed=args.seed + target_index * 17, eccentric=False)
        eccentric = orbital_draws(args.draws, seed=args.seed + target_index * 17, eccentric=True)

        model_definitions = [
            ("global_white_circular", frame, False, 0, "white", circular),
            ("instrument_white_circular", frame, True, degree, "white", circular),
            ("instrument_correlated_circular", frame, True, degree, "correlated", circular),
            ("instrument_correlated_eccentric", frame, True, degree, "correlated", eccentric),
        ]
        dominant = str(frame["instrument"].value_counts().index[0])
        without_dominant = frame[frame["instrument"] != dominant].copy()
        if len(without_dominant) >= 50:
            model_definitions.append(
                (
                    "leave_dominant_correlated_circular",
                    without_dominant,
                    True,
                    degree,
                    "correlated",
                    circular,
                )
            )

        jobs: list[
            tuple[
                str,
                pd.DataFrame,
                Future[tuple[pd.DataFrame, dict[str, object]]] | None,
                dict[str, object],
            ]
        ] = []
        for model_index, (model, model_frame, aware, model_degree, null, draws) in enumerate(model_definitions):
            kwargs: dict[str, object] = {
                "period_days": period,
                "amplitudes": amplitudes,
                "draws": draws,
                "instrument_aware": aware,
                "trend_degree": model_degree,
                "null": null,
                "permutations": args.permutations,
                "seed": args.seed + target_index * 101 + model_index,
            }
            future = (
                executor.submit(one_model, model_frame, **kwargs)
                if executor is not None
                else None
            )
            jobs.append((model, model_frame, future, kwargs))

        for model, model_frame, future, kwargs in jobs:
            grid, diagnostics = (
                future.result()
                if future is not None
                else one_model(model_frame, **kwargs)
            )
            grid.insert(0, "model", model)
            grid.insert(0, "target", target)
            grids.append(grid)
            k50, k50_status = completeness_threshold_with_status(
                grid["semi_amplitude_mps"], grid["completeness"], 0.5
            )
            k90, k90_status = completeness_threshold_with_status(
                grid["semi_amplitude_mps"], grid["completeness"], 0.9
            )
            threshold_rows.append(
                {
                    "target": target,
                    "model": model,
                    "n_nights": int(len(model_frame)),
                    "n_instruments": int(model_frame["instrument"].nunique()),
                    "mhz_period_days": period,
                    "published_k50_mps": published_k50,
                    "published_k90_mps": float(meta["published_k90_mps"]),
                    "k50_mps": k50,
                    "k90_mps": k90,
                    "k50_status": k50_status,
                    "k90_status": k90_status,
                    "k50_over_published": k50 / published_k50,
                    "power_threshold": diagnostics["power_threshold"],
                    "residual_rms_mps": diagnostics["residual_rms_mps"],
                    "trend_degree": diagnostics["trend_degree"],
                    "dominant_instrument_removed": dominant if model.startswith("leave_") else "",
                }
            )
            for label, jitter in diagnostics["jitters_mps"].items():
                jitter_rows.append(
                    {
                        "target": target,
                        "model": model,
                        "instrument": label,
                        "jitter_mps": jitter,
                    }
                )

    if executor is not None:
        executor.shutdown()

    all_grids = pd.concat(grids, ignore_index=True)
    thresholds = pd.DataFrame(threshold_rows)
    sample.to_csv(output / "analysis_sample.csv", index=False)
    nightly[nightly["target"].isin(selected_targets)].to_csv(
        output / "control_sample_nightly_rv.csv", index=False
    )
    all_grids.to_csv(output / "target_completeness.csv", index=False)
    thresholds.to_csv(output / "target_k50_k90.csv", index=False)
    pd.DataFrame(jitter_rows).to_csv(output / "per_instrument_jitter.csv", index=False)

    reference = thresholds[
        thresholds["model"] == "instrument_correlated_circular"
    ][["target", "k50_mps"]].rename(columns={"k50_mps": "reference_k50_mps"})
    comparison = thresholds.merge(reference, on="target", validate="many_to_one")
    comparison["k50_over_reference"] = comparison["k50_mps"] / comparison["reference_k50_mps"]
    population = (
        comparison.groupby("model", as_index=False)
        .agg(
            n_targets=("target", "nunique"),
            n_k50_bracketed=("k50_status", lambda x: int((x == "bracketed").sum())),
            n_k50_left_censored=("k50_status", lambda x: int((x == "left_censored_at_grid").sum())),
            n_k50_right_censored=("k50_status", lambda x: int((x == "right_censored_above_grid").sum())),
            n_k90_bracketed=("k90_status", lambda x: int((x == "bracketed").sum())),
            n_k90_left_censored=("k90_status", lambda x: int((x == "left_censored_at_grid").sum())),
            n_k90_right_censored=("k90_status", lambda x: int((x == "right_censored_above_grid").sum())),
            median_k50_mps=("k50_mps", "median"),
            median_k90_mps=("k90_mps", "median"),
            median_k50_over_published=("k50_over_published", "median"),
            median_k50_over_reference=("k50_over_reference", "median"),
            p16_k50_over_reference=("k50_over_reference", lambda x: float(np.nanpercentile(x, 16))),
            p84_k50_over_reference=("k50_over_reference", lambda x: float(np.nanpercentile(x, 84))),
        )
    )
    population.to_csv(output / "population_model_summary.csv", index=False)

    published_median_m50 = float(pd.to_numeric(table9["MpMHZ"], errors="coerce").median())
    published_median_k50 = float(pd.to_numeric(table9["KMHZ"], errors="coerce").median())
    reproduction = {
        "catalog_targets": int(len(table3)),
        "catalog_raw_rv_rows": int(len(table5)),
        "catalog_signal_rows": int(len(table6)),
        "catalog_trend_rows": int(len(table7)),
        "catalog_hz_sensitivity_rows": int(len(table9)),
        "catalog_instrument_rows": int(pd.read_csv(source / "inst.csv").shape[0]),
        "table3_reported_nightly_rv_sum": int(pd.to_numeric(table3["nRV"], errors="coerce").sum()),
        "quality_accepted_raw_rv_rows": int(len(clean)),
        "quality_accepted_nightly_rv_rows": int(len(nightly)),
        "published_middle_hz_median_m50_earth": published_median_m50,
        "published_middle_hz_median_k50_mps": published_median_k50,
        "paper_abstract_middle_hz_median_m50_earth": 48.0,
        "median_reproduction_difference_earth": published_median_m50 - 48.0,
        "quality_diagnostics": qc,
    }
    (output / "catalog_reproduction.json").write_text(
        json.dumps(reproduction, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    plot_published_sensitivity(selected_sample, figures / "published_hz_sensitivity_context.png")
    plot_k50_robustness(thresholds, figures / "k50_assumption_robustness.png")
    plot_population_distribution(thresholds, figures / "k50_population_distribution.png")

    by_model = population.set_index("model")
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "software_commit": args.software_commit,
        "catalog": "J/AJ/170/343",
        "catalog_bibcode": "2025AJ....170..343H",
        "catalog_manifest_hash": acquisition["manifest_hash"],
        "configuration_hash": canonical_json_sha256(configuration),
        "selected_control_targets": int(len(selected_targets)),
        "selected_nightly_rvs": int(nightly["target"].isin(selected_targets).sum()),
        "selection_definition": "table9 HZ row; >=150 valid nightly RVs; >=2 instruments; no table6 signal",
        "orbital_draws_per_amplitude": int(args.draws),
        "null_permutations_per_model": int(args.permutations),
        "empirical_fap": 0.01,
        "amplitude_grid_max_published_k50": float(max(configuration["amplitude_multipliers_of_published_k50"])),
        "published_middle_hz_median_m50_earth": published_median_m50,
        "published_middle_hz_median_k50_mps": published_median_k50,
        "control_median_instrument_correlated_circular_k50_mps": float(by_model.loc["instrument_correlated_circular", "median_k50_mps"]),
        "median_eccentric_to_circular_k50_ratio": float(by_model.loc["instrument_correlated_eccentric", "median_k50_over_reference"]),
        "median_global_white_to_instrument_correlated_k50_ratio": float(by_model.loc["global_white_circular", "median_k50_over_reference"]),
        "median_leave_dominant_to_full_k50_ratio": float(by_model.loc["leave_dominant_correlated_circular", "median_k50_over_reference"]),
        "interpretation": (
            "Middle-HZ detection sensitivity for a pre-declared no-catalogued-signal control sample. "
            "Values compare nuisance, null, eccentricity and instrument-removal assumptions; they are not companion detections."
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
