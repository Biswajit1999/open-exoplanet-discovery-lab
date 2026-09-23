"""Reproduce a public 55 Cnc e inter-visit/inter-reduction comparison.

The selected Patel et al. (2024) NIRCam products contain five independent
eclipse visits, each reduced by HANSOLO and stark.  The pipeline pair within a
visit is the same photon set and is therefore treated as an alternate
reduction, not an independent observation.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen

from astropy.table import Table
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from exolab.atmosphere import estimate_extra_scatter, weighted_band_mean
from exolab.provenance import canonical_json_sha256, sha256_file


ARCHIVE_ORIGIN = "https://exoplanetarchive.ipac.caltech.edu"
INDEX_URL = ARCHIVE_ORIGIN + "/cgi-bin/atmospheres/nph-firefly?atmospheres"
BIBCODE = "2024A&A...690A.159P"


def _download(url: str, path: Path, attempts: int = 5) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": "open-exoplanet-evidence-lab/0.3"})
            with urlopen(request, timeout=90) as response:
                payload = response.read()
            if not payload:
                raise RuntimeError("empty archive response")
            path.write_bytes(payload)
            return
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(2**attempt)


def archive_data_root() -> str:
    request = Request(INDEX_URL, headers={"User-Agent": "open-exoplanet-evidence-lab/0.3"})
    with urlopen(request, timeout=90) as response:
        page = response.read().decode("utf-8", errors="replace")
    match = re.search(r"FF_InitPage\s*\('([^']+)'", page)
    if not match:
        raise RuntimeError("could not resolve the Exoplanet Archive atmosphere data root")
    return match.group(1).rstrip("/") + "/data/"


def _numeric(table: Table, name: str) -> np.ndarray:
    column = table[name]
    if hasattr(column, "filled"):
        column = column.filled(np.nan)
    return np.asarray(column, dtype=float)


def _symmetric_error(table: Table) -> np.ndarray:
    upper = np.abs(_numeric(table, "ESPECLIPDEPERR1"))
    lower = np.abs(_numeric(table, "ESPECLIPDEPERR2"))
    error = 0.5 * (upper + lower)
    error[~np.isfinite(error) | (error <= 0)] = np.nan
    return error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metadata", default="outputs/public_snapshot/nea_atmospheric_spectra_metadata.csv"
    )
    parser.add_argument("--cache", default="data/raw/atmospheres/55-cnc-e")
    parser.add_argument("--output", default="outputs/atmosphere_55cnce")
    parser.add_argument("--software-commit", default="working-tree")
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    cache = Path(args.cache)
    metadata = pd.read_csv(args.metadata)
    selected = metadata[
        (metadata["pl_name"] == "55 Cnc e")
        & (metadata["spec_type"] == "Eclipse")
        & (metadata["bibcode"] == BIBCODE)
    ].copy()
    if len(selected) != 15:
        raise RuntimeError(f"expected 15 Patel et al. products, found {len(selected)}")

    root = archive_data_root()
    source_rows: list[dict[str, object]] = []
    spectral: list[dict[str, object]] = []
    broadband: list[dict[str, object]] = []
    for row in selected.itertuples(index=False):
        spec_number = int(re.search(r"_5518_(\d+)\.tbl$", row.spec_path).group(1))
        visit = (spec_number + 1) // 2 if spec_number <= 10 else spec_number - 10
        pipeline = "HANSOLO" if "HANSOLO" in str(row.note) else "stark"
        local = cache / Path(row.spec_path).name
        url = ARCHIVE_ORIGIN + root + row.spec_path
        _download(url, local)
        table = Table.read(local, format="ascii.ipac")
        wavelength = _numeric(table, "CENTRALWAVELNG")
        depth_percent = _numeric(table, "ESPECLIPDEP")
        error_percent = _symmetric_error(table)
        date = float(_numeric(table, "OBS_DATE")[0])
        source_rows.append(
            {
                "spec_number": spec_number,
                "visit": visit,
                "pipeline": pipeline,
                "relationship": "alternate reduction of same photons" if spec_number <= 10 else "independent visit broadband",
                "obs_date_bjd": date,
                "bibcode": row.bibcode,
                "note": row.note,
                "archive_spec_path": row.spec_path,
                "archive_url": url,
                "download_sha256": sha256_file(local),
                "n_rows": len(table),
            }
        )
        destination = spectral if spec_number <= 10 else broadband
        for x, y, e in zip(wavelength, depth_percent, error_percent):
            if np.isfinite(x) and np.isfinite(y) and np.isfinite(e):
                destination.append(
                    {
                        "spec_number": spec_number,
                        "visit": visit,
                        "pipeline": pipeline,
                        "obs_date_bjd": date,
                        "wavelength_micron": x,
                        "eclipse_depth_ppm": y * 10_000.0,
                        "eclipse_depth_error_ppm": e * 10_000.0,
                    }
                )

    source_table = pd.DataFrame(source_rows).sort_values("spec_number")
    spectra = pd.DataFrame(spectral)
    broadband_table = pd.DataFrame(broadband).sort_values(["visit", "wavelength_micron"])
    common_min = float(spectra.groupby("spec_number")["wavelength_micron"].min().max())
    common_max = float(spectra.groupby("spec_number")["wavelength_micron"].max().min())

    band_rows: list[dict[str, object]] = []
    for (visit, pipeline), group in spectra.groupby(["visit", "pipeline"], sort=True):
        estimate = weighted_band_mean(
            group["wavelength_micron"],
            group["eclipse_depth_ppm"],
            group["eclipse_depth_error_ppm"],
            common_min,
            common_max,
        )
        band_rows.append(
            {
                "visit": int(visit),
                "pipeline": pipeline,
                "obs_date_bjd": float(group["obs_date_bjd"].iloc[0]),
                "common_band_min_micron": common_min,
                "common_band_max_micron": common_max,
                "n_bins": estimate.n_bins,
                "band_mean_depth_ppm": estimate.mean,
                "band_mean_error_ppm": estimate.error,
                "covariance_available": False,
                "relationship_across_pipelines": "alternate reduction of same photons",
                "relationship_across_visits": "independent visits",
            }
        )
    band = pd.DataFrame(band_rows).sort_values(["visit", "pipeline"])
    paired = band.pivot(index="visit", columns="pipeline", values=["band_mean_depth_ppm", "band_mean_error_ppm"])
    pair_rows = []
    for visit in paired.index:
        delta = paired.loc[visit, ("band_mean_depth_ppm", "HANSOLO")] - paired.loc[visit, ("band_mean_depth_ppm", "stark")]
        sigma = np.hypot(
            paired.loc[visit, ("band_mean_error_ppm", "HANSOLO")],
            paired.loc[visit, ("band_mean_error_ppm", "stark")],
        )
        pair_rows.append(
            {
                "visit": int(visit),
                "hansolo_minus_stark_ppm": float(delta),
                "naive_independent_error_ppm": float(sigma),
                "standardized_difference": float(delta / sigma),
                "independence_warning": "same photons; standardized value is descriptive only",
            }
        )
    pair_table = pd.DataFrame(pair_rows)

    pipeline_summary: dict[str, dict[str, float | int]] = {}
    for pipeline, group in band.groupby("pipeline"):
        random_effects = estimate_extra_scatter(
            group["band_mean_depth_ppm"], group["band_mean_error_ppm"]
        )
        pipeline_summary[pipeline] = {
            "visits": int(len(group)),
            "mean_depth_ppm": random_effects.mean,
            "mean_error_ppm": random_effects.mean_error,
            "extra_inter_visit_scatter_ppm": random_effects.extra_scatter,
            "reduced_chi2_after_extra_scatter": random_effects.reduced_chi2,
        }

    broadband_summary: dict[str, dict[str, float | int]] = {}
    for wavelength, group in broadband_table.groupby("wavelength_micron"):
        random_effects = estimate_extra_scatter(
            group["eclipse_depth_ppm"], group["eclipse_depth_error_ppm"]
        )
        broadband_summary[f"{wavelength:.2f}_micron"] = {
            "visits": int(len(group)),
            "mean_depth_ppm": random_effects.mean,
            "mean_error_ppm": random_effects.mean_error,
            "extra_inter_visit_scatter_ppm": random_effects.extra_scatter,
            "reduced_chi2_after_extra_scatter": random_effects.reduced_chi2,
        }

    source_table.to_csv(output / "source_provenance.csv", index=False)
    spectra.to_csv(output / "spectral_bins.csv", index=False)
    band.to_csv(output / "common_band_visit_means.csv", index=False)
    pair_table.to_csv(output / "paired_pipeline_differences.csv", index=False)
    broadband_table.to_csv(output / "broadband_visit_depths.csv", index=False)

    configuration = {
        "target": "55 Cnc e",
        "bibcode": BIBCODE,
        "products": source_table["archive_spec_path"].tolist(),
        "error_symmetrization": "mean absolute upper/lower uncertainty",
        "common_band_micron": [common_min, common_max],
    }
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "software_commit": args.software_commit,
        "configuration_hash": canonical_json_sha256(configuration),
        "target": "55 Cnc e",
        "bibcode": BIBCODE,
        "products": int(len(source_table)),
        "independent_visits": 5,
        "alternate_reductions_per_visit": 2,
        "common_band_micron": [common_min, common_max],
        "pipeline_results": pipeline_summary,
        "broadband_results": broadband_summary,
        "median_absolute_pipeline_difference_ppm": float(pair_table["hansolo_minus_stark_ppm"].abs().median()),
        "maximum_absolute_descriptive_z": float(pair_table["standardized_difference"].abs().max()),
        "limitations": [
            "HANSOLO and stark products within a visit are alternate reductions of the same photons, not independent observations.",
            "The archive products do not provide a spectral covariance matrix; common-band errors assume independent bins and are descriptive.",
            "This comparison does not establish atmospheric composition or adjudicate the publication's physical interpretation.",
        ],
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    figure, axes = plt.subplots(1, 2, figsize=(11.5, 4.7))
    colors = {"HANSOLO": "#18b6c9", "stark": "#d89b2b"}
    offsets = {"HANSOLO": -0.07, "stark": 0.07}
    for pipeline, group in band.groupby("pipeline"):
        axes[0].errorbar(
            group["visit"] + offsets[pipeline],
            group["band_mean_depth_ppm"],
            yerr=group["band_mean_error_ppm"],
            fmt="o",
            capsize=3,
            color=colors[pipeline],
            label=pipeline,
        )
    axes[0].set(
        xlabel="Independent eclipse visit",
        ylabel="Common-band eclipse depth [ppm]",
        title=f"Alternate reductions · {common_min:.3f}–{common_max:.3f} μm",
        xticks=range(1, 6),
    )
    axes[0].legend(frameon=False)
    for wavelength, group in broadband_table.groupby("wavelength_micron"):
        axes[1].errorbar(
            group["visit"],
            group["eclipse_depth_ppm"],
            yerr=group["eclipse_depth_error_ppm"],
            marker="o",
            capsize=3,
            label=f"{wavelength:.2f} μm",
        )
    axes[1].set(
        xlabel="Independent eclipse visit",
        ylabel="Broadband eclipse depth [ppm]",
        title="stark broadband visit series",
        xticks=range(1, 6),
    )
    axes[1].legend(frameon=False)
    for axis in axes:
        axis.grid(alpha=0.2)
    figure.suptitle("55 Cnc e · public NIRCam reproducibility diagnostic")
    figure.tight_layout()
    figure.savefig(output / "atmosphere_reproducibility.png", dpi=220)
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
