"""Build a dated public NIRPS/HARPS ObsCore overlap census from ESO TAP."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from exolab.eso import ESOTapClient, overlap_census
from exolab.provenance import DatasetRecord, FileRecord, write_manifest
from exolab.registry import require_source


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/census/eso")
    parser.add_argument("--manifest", default="data/manifests/eso_nirps_harps_census.json")
    parser.add_argument("--max-separation-arcsec", type=float, default=3.0)
    args = parser.parse_args()

    require_source("nirps_phase3")
    require_source("harps")
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    client = ESOTapClient()
    nirps = client.instrument_products("NIRPS")
    harps = client.instrument_products("HARPS")
    npath = out / "nirps_obscore.csv"
    hpath = out / "harps_obscore.csv"
    cpath = out / "overlap_census.csv"
    nirps.to_csv(npath, index=False)
    harps.to_csv(hpath, index=False)
    census = overlap_census(nirps, harps, max_sep_arcsec=args.max_separation_arcsec)
    census.to_csv(cpath, index=False)

    files = [
        FileRecord.from_path(npath, source_product_id="ESO ObsCore NIRPS", source_url="https://archive.eso.org/tap_obs"),
        FileRecord.from_path(hpath, source_product_id="ESO ObsCore HARPS", source_url="https://archive.eso.org/tap_obs"),
        FileRecord.from_path(cpath, source_product_id="derived overlap census", pipeline_version="exolab 0.2"),
    ]
    record = DatasetRecord.create(
        source_id="eso_nirps_harps_overlap",
        source_state="census",
        archive="ESO tap_obs / ivoa.ObsCore",
        query="public spectral products where instrument_name=NIRPS or HARPS",
        files=files,
        selection_rules={
            "public_only": True,
            "dataproduct_type": "spectrum",
            "epoch_deduplication": "target_name + t_min rounded to 1e-7 day",
            "crossmatch_radius_arcsec": args.max_separation_arcsec,
        },
        notes=(
            "ObsCore census establishes public spectral-product overlap only.",
            "Precision-RV science still requires product-level DRS/provenance verification and accepted RV products.",
            "NIRPS DRS 3.2.6 affected-date products are not approved for sub-10 m/s inference.",
        ),
        access_time=datetime.now(timezone.utc),
    )
    write_manifest(record, args.manifest)
    summary = {
        "n_nirps_products": int(len(nirps)),
        "n_harps_products": int(len(harps)),
        "n_nirps_targets_in_census": int(len(census)),
        "n_targets_with_harps_match": int(census["harps_target"].notna().sum()),
    }
    (out / "census_metadata.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
