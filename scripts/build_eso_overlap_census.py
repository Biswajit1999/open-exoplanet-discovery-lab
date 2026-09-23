"""Build a public NIRPS/HARPS metadata overlap census from ESO TAP.

The census starts from public NIRPS products. HARPS searches are coordinate
based rather than name based, and independent targets are queried in a bounded
worker pool. This is a metadata-level census; precision-RV science still
requires product-level FITS/PROCSOFT verification and RV extraction.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np
import pandas as pd

from exolab.chromatic import simultaneity_counts
from exolab.eso import ESOArchiveClient, instrument_inventory_query, target_instrument_query
from exolab.provenance import DatasetRecord, FileRecord, write_manifest


def unique_epochs(frame: pd.DataFrame) -> np.ndarray:
    if frame.empty or "t_min" not in frame.columns:
        return np.array([], dtype=float)
    values = pd.to_numeric(frame["t_min"], errors="coerce").dropna().to_numpy(dtype=float)
    if not values.size:
        return values
    return np.unique(np.round(values, 8))


def query_harps(
    row: object,
    radius_arcsec: float,
    timeout: int,
    available_columns: list[str],
) -> tuple[object, pd.DataFrame, str]:
    client = ESOArchiveClient(timeout=timeout)
    query = target_instrument_query(
        "HARPS",
        ra_deg=float(row.s_ra),
        dec_deg=float(row.s_dec),
        radius_deg=float(radius_arcsec) / 3600.0,
        available_columns=available_columns,
    )
    try:
        return row, client.query(query), ""
    except Exception as exc:
        return row, pd.DataFrame(), repr(exc)


def product_id_column(frame: pd.DataFrame) -> str:
    for name in ("dp_id", "obs_publisher_did", "obs_id"):
        if name in frame.columns:
            return name
    raise RuntimeError("ESO ObsCore result lacks dp_id, obs_publisher_did and obs_id")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/eso_overlap_census")
    parser.add_argument("--radius-arcsec", type=float, default=5.0)
    parser.add_argument("--max-targets", type=int, default=0)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    client = ESOArchiveClient(timeout=args.timeout)

    available_columns = client.obscore_columns()
    (output / "eso_obscore_columns.json").write_text(
        json.dumps(sorted(available_columns), indent=2) + "\n",
        encoding="utf-8",
    )

    nirps_query = instrument_inventory_query(
        "NIRPS",
        available_columns=available_columns,
    )
    nirps = client.query(nirps_query)
    if nirps.empty:
        raise RuntimeError(
            "ESO ObsCore returned no public rows with instrument_name='NIRPS'; "
            "the live instrument naming/schema must be inspected before proceeding"
        )

    pid = product_id_column(nirps)
    nirps_path = output / "nirps_public_products.csv"
    nirps.to_csv(nirps_path, index=False)

    target_rows = (
        nirps.dropna(subset=["s_ra", "s_dec"])
        .groupby("target_name", dropna=False)
        .agg(
            s_ra=("s_ra", "median"),
            s_dec=("s_dec", "median"),
            n_nirps_products=(pid, "nunique"),
            nirps_t_min=("t_min", "min"),
            nirps_t_max=("t_max", "max"),
        )
        .reset_index()
        .sort_values(["n_nirps_products", "target_name"], ascending=[False, True])
    )
    if args.max_targets > 0:
        target_rows = target_rows.head(args.max_targets)

    raw_results: list[tuple[object, pd.DataFrame, str]] = []
    workers = max(1, min(int(args.workers), 12))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(
                query_harps,
                row,
                args.radius_arcsec,
                args.timeout,
                available_columns,
            )
            for row in target_rows.itertuples(index=False)
        ]
        for future in as_completed(futures):
            raw_results.append(future.result())

    raw_results.sort(key=lambda item: str(item[0].target_name))
    harps_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []

    for row, harps, query_error in raw_results:
        if not harps.empty:
            harps = harps.copy()
            harps["nirps_anchor_target"] = row.target_name
            harps_frames.append(harps)

        nirps_target = nirps[nirps["target_name"] == row.target_name]
        tn = unique_epochs(nirps_target)
        th = unique_epochs(harps)
        pairs = (
            simultaneity_counts(th, tn)
            if th.size and tn.size
            else {"1h": 0, "6h": 0, "1d": 0, "3d": 0, "7d": 0}
        )

        hpid = product_id_column(harps) if not harps.empty else None
        summary_rows.append(
            {
                "target_name": row.target_name,
                "s_ra": row.s_ra,
                "s_dec": row.s_dec,
                "n_nirps_products": int(row.n_nirps_products),
                "n_harps_products": int(harps[hpid].nunique()) if hpid else 0,
                "n_nirps_epochs": int(tn.size),
                "n_harps_epochs": int(th.size),
                "nirps_first_mjd": float(np.min(tn)) if tn.size else np.nan,
                "nirps_last_mjd": float(np.max(tn)) if tn.size else np.nan,
                "harps_first_mjd": float(np.min(th)) if th.size else np.nan,
                "harps_last_mjd": float(np.max(th)) if th.size else np.nan,
                "pair_1h": pairs["1h"],
                "pair_6h": pairs["6h"],
                "pair_1d": pairs["1d"],
                "pair_3d": pairs["3d"],
                "pair_7d": pairs["7d"],
                "query_error": query_error,
            }
        )

    harps_all = (
        pd.concat(harps_frames, ignore_index=True)
        if harps_frames
        else pd.DataFrame()
    )
    harps_path = output / "harps_public_matches.csv"
    harps_all.to_csv(harps_path, index=False)

    summary = pd.DataFrame(summary_rows)
    summary_path = output / "nirps_harps_overlap_summary.csv"
    summary.to_csv(summary_path, index=False)

    files = [
        FileRecord.from_path(nirps_path, source_product_id="NIRPS-ObsCore"),
        FileRecord.from_path(harps_path, source_product_id="HARPS-cone-matches"),
        FileRecord.from_path(
            summary_path,
            source_product_id="NIRPS-HARPS-overlap-summary",
        ),
    ]
    record = DatasetRecord.create(
        source_id="nirps_harps_overlap",
        source_state="census",
        archive="ESO Science Archive TAP",
        query=nirps_query,
        files=files,
        selection_rules={
            "nirps_instrument_name": "NIRPS",
            "harps_instrument_name": "HARPS",
            "public_only_when_data_rights_exposed": True,
            "coordinate_match_radius_arcsec": args.radius_arcsec,
            "epoch_dedup_round_days": 8,
            "simultaneity_windows": ["1h", "6h", "1d", "3d", "7d"],
            "max_targets": args.max_targets,
            "workers": workers,
        },
        notes=[
            "ObsCore product/epoch census; it is not a precision-RV table.",
            "FITS PROCSOFT must be inspected before using NIRPS velocities.",
            "The documented DRS 3.2.6 precision-RV interval remains excluded by policy.",
        ],
    )
    write_manifest(record, output / "nirps_harps_overlap_manifest.json")

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "nirps_products": int(len(nirps)),
        "nirps_targets_in_census": int(len(target_rows)),
        "targets_queried": int(len(summary)),
        "targets_with_harps_products": int(
            (summary["n_harps_products"] > 0).sum()
        )
        if len(summary)
        else 0,
        "targets_with_1h_pairs": int((summary["pair_1h"] > 0).sum())
        if len(summary)
        else 0,
        "targets_with_1d_pairs": int((summary["pair_1d"] > 0).sum())
        if len(summary)
        else 0,
        "query_errors": int(
            (summary["query_error"].astype(str).str.len() > 0).sum()
        )
        if len(summary)
        else 0,
        "manifest_hash": record.manifest_hash,
    }
    (output / "census_summary.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
