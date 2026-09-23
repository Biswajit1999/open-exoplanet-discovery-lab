"""Run a public TESS out-of-sample activity-period comparison."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import lightkurve as lk
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from exolab.provenance import FileRecord, canonical_json_sha256, sha256_file
from exolab.tess import activity_periodogram, quality_normalize, temporal_coherence, time_bin


def sector_number(mission: object) -> int:
    return int(str(mission).split()[-1])


def select_products(search: lk.SearchResult, sectors: set[int], author: str, cadence: float) -> lk.SearchResult:
    table = search.table
    mask = np.array([sector_number(value) in sectors for value in table["mission"]])
    mask &= np.asarray(table["author"], dtype=str) == author
    mask &= np.isclose(np.asarray(table["exptime"], dtype=float), cadence)
    selected = search[mask]
    if len(selected) != len(sectors):
        found = sorted({sector_number(value) for value in selected.table["mission"]})
        raise RuntimeError(f"requested sectors {sorted(sectors)}, found {found} for {author} {cadence:g}s")
    return selected


def acquire_group(
    selected: lk.SearchResult,
    cache: Path,
    label: str,
) -> tuple[pd.DataFrame, pd.DataFrame, list[FileRecord]]:
    collection = selected.download_all(download_dir=str(cache), quality_bitmask="none")
    if collection is None:
        raise RuntimeError(f"MAST returned no light curves for {label}")
    samples: list[pd.DataFrame] = []
    provenance: list[dict[str, object]] = []
    files: list[FileRecord] = []
    search_table = selected.table
    for index, lightcurve in enumerate(collection):
        time = np.asarray(lightcurve.time.value, dtype=float)
        flux = np.asarray(lightcurve.flux.value, dtype=float)
        error = np.asarray(lightcurve.flux_err.value, dtype=float)
        quality = np.asarray(lightcurve.quality, dtype=int)
        clean_time, clean_flux, clean_error, accepted = quality_normalize(
            time, flux, error, quality, accepted_quality=0
        )
        clean_time, clean_flux, clean_error = time_bin(
            clean_time, clean_flux, clean_error, width_minutes=30
        )
        sector = sector_number(search_table["mission"][index])
        samples.append(
            pd.DataFrame(
                {
                    "time_btjd": clean_time,
                    "relative_flux_ppm": clean_flux,
                    "relative_flux_error_ppm": clean_error,
                    "sector": sector,
                    "sample": label,
                }
            )
        )
        filename = Path(lightcurve.filename)
        files.append(
            FileRecord.from_path(
                filename,
                source_product_id=str(search_table["obs_id"][index]),
                source_url=str(search_table["dataURI"][index]),
                pipeline_version=f"{search_table['author'][index]} light curve",
            )
        )
        provenance.append(
            {
                "sample": label,
                "sector": sector,
                "mission": str(search_table["mission"][index]),
                "author": str(search_table["author"][index]),
                "exptime_seconds": float(search_table["exptime"][index]),
                "obs_id": str(search_table["obs_id"][index]),
                "data_uri": str(search_table["dataURI"][index]),
                "product_filename": str(search_table["productFilename"][index]),
                "download_sha256": files[-1].sha256,
                "cadences_total": int(len(time)),
                "cadences_quality_zero_and_sigma_clip": int(len(accepted)),
                "quality_rule": "TESS QUALITY == 0; finite positive errors; 7-MAD flux clip",
            }
        )
    return pd.concat(samples, ignore_index=True), pd.DataFrame(provenance), files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="HD 10780")
    parser.add_argument("--control-sectors", nargs="+", type=int, default=[24, 25])
    parser.add_argument("--test-sectors", nargs="+", type=int, default=[85, 86])
    parser.add_argument("--author", default="SPOC")
    parser.add_argument("--cadence", type=float, default=120.0)
    parser.add_argument("--cache", default="data/raw/tess")
    parser.add_argument("--output", default="outputs/tess_temporal")
    parser.add_argument("--software-commit", default="working-tree")
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    search = lk.search_lightcurve(args.target, mission="TESS")
    control_search = select_products(
        search, set(args.control_sectors), args.author, args.cadence
    )
    test_search = select_products(search, set(args.test_sectors), args.author, args.cadence)
    control, control_provenance, control_files = acquire_group(
        control_search, Path(args.cache), "control"
    )
    test, test_provenance, test_files = acquire_group(
        test_search, Path(args.cache), "test"
    )
    samples = pd.concat([control, test], ignore_index=True)
    provenance = pd.concat([control_provenance, test_provenance], ignore_index=True)
    samples.to_csv(output / "lightcurve_30min.csv", index=False)
    provenance.to_csv(output / "product_provenance.csv", index=False)

    control_pg = activity_periodogram(
        control["time_btjd"], control["relative_flux_ppm"], control["relative_flux_error_ppm"]
    )
    test_pg = activity_periodogram(
        test["time_btjd"], test["relative_flux_ppm"], test["relative_flux_error_ppm"]
    )
    coherence = temporal_coherence(
        control["time_btjd"],
        control["relative_flux_ppm"],
        control["relative_flux_error_ppm"],
        test["time_btjd"],
        test["relative_flux_ppm"],
        test["relative_flux_error_ppm"],
        period_days=control_pg.best_period,
    )
    configuration = {
        "target": args.target,
        "control_sectors": args.control_sectors,
        "test_sectors": args.test_sectors,
        "author": args.author,
        "cadence_seconds": args.cadence,
        "quality_rule": "QUALITY == 0, finite positive errors, 7-MAD clip, 30-min weighted bins",
        "period_search_days": [2.0, 30.0],
    }
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "software_commit": args.software_commit,
        "configuration_hash": canonical_json_sha256(configuration),
        "target": args.target,
        "control_sectors": args.control_sectors,
        "test_sectors": args.test_sectors,
        "control_period_days": control_pg.best_period,
        "control_analytic_fap": control_pg.false_alarm_probability,
        "test_period_days": test_pg.best_period,
        "test_analytic_fap": test_pg.false_alarm_probability,
        "test_to_control_amplitude_ratio_at_control_period": coherence.amplitude_ratio,
        "phase_difference_radians_at_control_period": coherence.phase_difference_radians,
        "interpretation": (
            "Photometric activity-period and temporal-coherence diagnostic. Periodogram peaks are not planet confirmations."
        ),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    figure, axes = plt.subplots(2, 2, figsize=(11, 7.2))
    for sample, axis, title in (
        (control, axes[0, 0], f"Control sectors {args.control_sectors}"),
        (test, axes[0, 1], f"Test sectors {args.test_sectors}"),
    ):
        for sector, group in sample.groupby("sector"):
            axis.plot(
                group["time_btjd"] - sample["time_btjd"].min(),
                group["relative_flux_ppm"],
                ".",
                ms=2,
                alpha=0.55,
                label=f"S{sector}",
            )
        axis.set(title=title, xlabel="Time from sample start [d]", ylabel="Relative flux [ppm]")
        axis.legend(frameon=False, fontsize=8)
    axes[1, 0].plot(control_pg.period, control_pg.power, label="control")
    axes[1, 0].plot(test_pg.period, test_pg.power, label="test", alpha=0.8)
    axes[1, 0].set(xscale="log", xlabel="Period [d]", ylabel="GLS power")
    axes[1, 0].legend(frameon=False)
    axes[1, 1].axis("off")
    axes[1, 1].text(
        0.02,
        0.92,
        f"Control best period: {control_pg.best_period:.3f} d\n"
        f"Test best period: {test_pg.best_period:.3f} d\n"
        f"K_test / K_control: {coherence.amplitude_ratio:.3f}\n"
        f"Phase difference: {coherence.phase_difference_radians:.3f} rad",
        va="top",
        family="monospace",
    )
    for axis in axes.ravel()[:3]:
        axis.grid(alpha=0.18)
    figure.suptitle(f"{args.target} · public TESS temporal activity context")
    figure.tight_layout()
    figure.savefig(output / "tess_temporal_context.png", dpi=220)
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
