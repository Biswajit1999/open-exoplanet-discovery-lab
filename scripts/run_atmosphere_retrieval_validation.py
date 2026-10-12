"""Run a bounded thermal-retrieval validation on public 55 Cnc e spectra.

The forward model is an isothermal planet blackbody divided by a stellar
blackbody.  It is compared with constant and linear empirical spectra, and its
visit/pipeline stability is tested.  This is deliberately not a molecular
abundance retrieval: the archive products do not publish wavelength covariance
and the 3.95--4.92 micron band alone cannot identify a unique atmosphere.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from io import StringIO
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from exolab.atmosphere import (
    blackbody_eclipse_depth_ppm,
    estimate_extra_scatter,
    fit_blackbody_temperature,
    weighted_polynomial_fit_statistics,
)
from exolab.provenance import canonical_json_sha256, sha256_file


NEA_TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
SYSTEM_QUERY = (
    "select pl_name,st_teff,st_rad,pl_rade,pl_ratror,pl_orbsmax,pl_eqt "
    "from pscomppars where pl_name='55 Cnc e'"
)


def query_system_parameters() -> pd.DataFrame:
    url = f"{NEA_TAP}?query={quote(SYSTEM_QUERY)}&format=csv"
    request = Request(url, headers={"User-Agent": "open-exoplanet-evidence-lab/0.4"})
    with urlopen(request, timeout=90) as response:
        payload = response.read().decode("utf-8")
    frame = pd.read_csv(StringIO(payload))
    if len(frame) != 1:
        raise RuntimeError(f"expected one NASA composite row for 55 Cnc e, found {len(frame)}")
    required = ["st_teff", "pl_ratror", "pl_eqt"]
    if frame[required].isna().any().any():
        raise RuntimeError("NASA composite row is missing a required thermal-model parameter")
    return frame


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", default="results/atmosphere_55cnce_2026-09-23"
    )
    parser.add_argument("--output", default="outputs/atmosphere_retrieval_validation")
    parser.add_argument("--software-commit", default="working-tree")
    args = parser.parse_args()

    source = Path(args.input)
    output = Path(args.output)
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    spectra = pd.read_csv(source / "spectral_bins.csv")
    broadband = pd.read_csv(source / "broadband_visit_depths.csv")
    system = query_system_parameters()
    system.to_csv(output / "nasa_system_parameters.csv", index=False)

    stellar_temperature = float(system.loc[0, "st_teff"])
    radius_ratio = float(system.loc[0, "pl_ratror"])
    equilibrium_temperature = float(system.loc[0, "pl_eqt"])
    paper_stellar_temperature = 5269.0

    retrieval_rows: list[dict[str, object]] = []
    for (pipeline, visit), group in spectra.groupby(["pipeline", "visit"], sort=True):
        wavelength = group["wavelength_micron"].to_numpy(float)
        depth = group["eclipse_depth_ppm"].to_numpy(float)
        error = group["eclipse_depth_error_ppm"].to_numpy(float)
        thermal = fit_blackbody_temperature(
            wavelength,
            depth,
            error,
            stellar_temperature_k=stellar_temperature,
            radius_ratio=radius_ratio,
        )
        stellar_sensitivity = fit_blackbody_temperature(
            wavelength,
            depth,
            error,
            stellar_temperature_k=paper_stellar_temperature,
            radius_ratio=radius_ratio,
        )
        flat = weighted_polynomial_fit_statistics(wavelength, depth, error, degree=0)
        linear = weighted_polynomial_fit_statistics(wavelength, depth, error, degree=1)
        model_bics = {
            "blackbody": float(thermal.bic),
            "constant": float(flat["bic"]),
            "linear": float(linear["bic"]),
        }
        retrieval_rows.append(
            {
                "pipeline": pipeline,
                "visit": int(visit),
                "obs_date_bjd": float(group["obs_date_bjd"].iloc[0]),
                "n_bins": thermal.n_bins,
                "stellar_temperature_k": stellar_temperature,
                "radius_ratio": radius_ratio,
                "brightness_temperature_k": thermal.temperature_k,
                "temperature_error_minus_k": thermal.error_minus_k,
                "temperature_error_plus_k": thermal.error_plus_k,
                "temperature_lower_status": thermal.lower_status,
                "temperature_upper_status": thermal.upper_status,
                "stellar_temperature_sensitivity_k": (
                    stellar_sensitivity.temperature_k - thermal.temperature_k
                ),
                "blackbody_chi2": thermal.chi2,
                "blackbody_dof": thermal.dof,
                "blackbody_reduced_chi2": thermal.chi2 / thermal.dof,
                "blackbody_bic": thermal.bic,
                "constant_bic": flat["bic"],
                "linear_bic": linear["bic"],
                "delta_bic_blackbody_minus_constant": thermal.bic - float(flat["bic"]),
                "delta_bic_blackbody_minus_linear": thermal.bic - float(linear["bic"]),
                "preferred_of_three_by_bic": min(model_bics, key=model_bics.get),
                "linear_slope_ppm_per_micron": float(linear["coefficients"][1]),
                "covariance_available": False,
            }
        )
    retrievals = pd.DataFrame(retrieval_rows).sort_values(["pipeline", "visit"])
    retrievals.to_csv(output / "visit_thermal_retrievals.csv", index=False)

    pipeline_rows: list[dict[str, object]] = []
    loo_rows: list[dict[str, object]] = []
    for pipeline, group in retrievals.groupby("pipeline", sort=True):
        group = group.sort_values("visit")
        temperature_error = 0.5 * (
            group["temperature_error_minus_k"] + group["temperature_error_plus_k"]
        )
        random_effects = estimate_extra_scatter(
            group["brightness_temperature_k"], temperature_error
        )
        pipeline_rows.append(
            {
                "pipeline": pipeline,
                "visits": int(len(group)),
                "mean_brightness_temperature_k": random_effects.mean,
                "mean_error_k": random_effects.mean_error,
                "extra_inter_visit_scatter_k": random_effects.extra_scatter,
                "reduced_chi2_after_extra_scatter": random_effects.reduced_chi2,
                "blackbody_bic_preferred_visits": int(
                    (group["preferred_of_three_by_bic"] == "blackbody").sum()
                ),
                "constant_bic_preferred_visits": int(
                    (group["preferred_of_three_by_bic"] == "constant").sum()
                ),
                "linear_bic_preferred_visits": int(
                    (group["preferred_of_three_by_bic"] == "linear").sum()
                ),
            }
        )
        for held_index in group.index:
            training = group.drop(index=held_index)
            training_error = 0.5 * (
                training["temperature_error_minus_k"]
                + training["temperature_error_plus_k"]
            )
            fitted = estimate_extra_scatter(
                training["brightness_temperature_k"], training_error
            )
            held = group.loc[held_index]
            held_error = 0.5 * (
                held["temperature_error_minus_k"] + held["temperature_error_plus_k"]
            )
            predictive_error = float(
                np.sqrt(held_error**2 + fitted.mean_error**2 + fitted.extra_scatter**2)
            )
            loo_rows.append(
                {
                    "pipeline": pipeline,
                    "held_out_visit": int(held["visit"]),
                    "held_out_temperature_k": float(held["brightness_temperature_k"]),
                    "training_mean_temperature_k": fitted.mean,
                    "training_extra_scatter_k": fitted.extra_scatter,
                    "predictive_error_k": predictive_error,
                    "predictive_z": float(
                        (held["brightness_temperature_k"] - fitted.mean) / predictive_error
                    ),
                }
            )
    pipeline_summary = pd.DataFrame(pipeline_rows)
    leave_one_out = pd.DataFrame(loo_rows)
    pipeline_summary.to_csv(output / "pipeline_temperature_summary.csv", index=False)
    leave_one_out.to_csv(output / "leave_one_visit_out.csv", index=False)

    two_band_rows: list[dict[str, object]] = []
    for visit, group in broadband.groupby("visit", sort=True):
        thermal = fit_blackbody_temperature(
            group["wavelength_micron"],
            group["eclipse_depth_ppm"],
            group["eclipse_depth_error_ppm"],
            stellar_temperature_k=stellar_temperature,
            radius_ratio=radius_ratio,
        )
        flat = weighted_polynomial_fit_statistics(
            group["wavelength_micron"],
            group["eclipse_depth_ppm"],
            group["eclipse_depth_error_ppm"],
            degree=0,
        )
        two_band_rows.append(
            {
                "visit": int(visit),
                "brightness_temperature_k": thermal.temperature_k,
                "temperature_error_minus_k": thermal.error_minus_k,
                "temperature_error_plus_k": thermal.error_plus_k,
                "blackbody_chi2": thermal.chi2,
                "blackbody_dof": thermal.dof,
                "blackbody_bic": thermal.bic,
                "constant_bic": flat["bic"],
                "delta_bic_blackbody_minus_constant": thermal.bic - float(flat["bic"]),
                "note": "2.12 and 4.50 micron stark broadband depths; same visit, separate channels",
            }
        )
    two_band = pd.DataFrame(two_band_rows)
    two_band.to_csv(output / "two_band_thermal_retrievals.csv", index=False)

    configuration = {
        "forward_model": "isothermal planet blackbody / stellar blackbody",
        "stellar_temperature_k": stellar_temperature,
        "stellar_temperature_sensitivity_k": paper_stellar_temperature,
        "radius_ratio": radius_ratio,
        "temperature_prior_k": [300.0, 5000.0],
        "uncertainty": "delta-chi-square=1 profile interval; diagonal published errors",
        "comparators": ["constant eclipse depth", "linear eclipse depth vs wavelength"],
        "model_score": "BIC",
        "nasa_query": SYSTEM_QUERY,
    }
    (output / "analysis_configuration.json").write_text(
        json.dumps(configuration, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "nasa_query.json").write_text(
        json.dumps(
            {
                "endpoint": NEA_TAP,
                "query": SYSTEM_QUERY,
                "query_hash": canonical_json_sha256({"query": SYSTEM_QUERY}),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    paired = retrievals.pivot(
        index="visit", columns="pipeline", values="brightness_temperature_k"
    )
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "software_commit": args.software_commit,
        "configuration_hash": canonical_json_sha256(configuration),
        "target": "55 Cnc e",
        "spectral_retrievals": int(len(retrievals)),
        "independent_visits": int(retrievals["visit"].nunique()),
        "archive_stellar_temperature_k": stellar_temperature,
        "archive_radius_ratio": radius_ratio,
        "archive_equilibrium_temperature_k": equilibrium_temperature,
        "pipeline_results": {
            row.pipeline: {
                "mean_brightness_temperature_k": row.mean_brightness_temperature_k,
                "mean_error_k": row.mean_error_k,
                "extra_inter_visit_scatter_k": row.extra_inter_visit_scatter_k,
                "bic_preferred_visit_counts": {
                    "blackbody": int(row.blackbody_bic_preferred_visits),
                    "constant": int(row.constant_bic_preferred_visits),
                    "linear": int(row.linear_bic_preferred_visits),
                },
            }
            for row in pipeline_summary.itertuples()
        },
        "median_same_visit_hansolo_minus_stark_temperature_k": float(
            (paired["HANSOLO"] - paired["stark"]).median()
        ),
        "maximum_absolute_leave_one_visit_out_predictive_z": float(
            leave_one_out["predictive_z"].abs().max()
        ),
        "two_band_blackbody_preferred_visits": int(
            (two_band["delta_bic_blackbody_minus_constant"] < 0).sum()
        ),
        "source_checksums": {
            "spectral_bins": sha256_file(source / "spectral_bins.csv"),
            "broadband_visit_depths": sha256_file(source / "broadband_visit_depths.csv"),
        },
        "claim_boundary": (
            "Brightness-temperature and model-adequacy validation only. No molecular "
            "abundance or atmospheric-composition posterior is reported because the narrow "
            "band and unpublished spectral covariance do not support a unique retrieval."
        ),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    figure, axes = plt.subplots(1, 2, figsize=(11.2, 4.8))
    colors = {"HANSOLO": "#1c7f89", "stark": "#a66216"}
    offsets = {"HANSOLO": -0.08, "stark": 0.08}
    for pipeline, group in retrievals.groupby("pipeline"):
        axes[0].errorbar(
            group["visit"] + offsets[pipeline],
            group["brightness_temperature_k"],
            yerr=np.vstack(
                [group["temperature_error_minus_k"], group["temperature_error_plus_k"]]
            ),
            fmt="o",
            capsize=3,
            color=colors[pipeline],
            label=pipeline,
        )
    axes[0].axhline(
        equilibrium_temperature, color="#687783", linestyle="--", linewidth=1,
        label="archive equilibrium T",
    )
    axes[0].set(
        xlabel="Independent eclipse visit",
        ylabel="Blackbody brightness temperature [K]",
        title="Retrieval changes with reduction and visit",
        xticks=range(1, 6),
    )
    axes[0].legend(frameon=False, fontsize=8)

    for pipeline, group in retrievals.groupby("pipeline"):
        axes[1].plot(
            group["visit"],
            group["delta_bic_blackbody_minus_constant"],
            marker="o",
            color=colors[pipeline],
            label=pipeline,
        )
    axes[1].axhline(0.0, color="#202d38", linewidth=1)
    axes[1].set(
        xlabel="Independent eclipse visit",
        ylabel="BIC(blackbody) − BIC(constant)",
        title="Narrow-band shape rarely identifies a thermal model",
        xticks=range(1, 6),
    )
    axes[1].legend(frameon=False)
    for axis in axes:
        axis.grid(alpha=0.2)
    figure.suptitle("55 Cnc e · bounded thermal-retrieval validation")
    figure.tight_layout()
    figure.savefig(figures / "atmosphere_retrieval_validation.png", dpi=220)
    plt.close(figure)

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
