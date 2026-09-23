"""Build a dated public-data snapshot from authoritative exoplanet archives.

This script is intentionally archive-facing and does not make discovery claims.
It writes compact tables plus provenance manifests. Large raw spectra are not
mirrored into the repository.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from astroquery.vizier import Vizier

from exolab.archives import ExoplanetArchiveClient
from exolab.provenance import DatasetRecord, FileRecord, write_manifest


VIZIER_RELEASES = {
    "nets3": "J/AJ/170/264",
    "nets4_hd190360": "J/AJ/171/286",
}


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_").lower()


def fetch_vizier_catalog(source_id: str, catalog: str, output: Path) -> dict[str, object]:
    client = Vizier(columns=["**"], row_limit=-1)
    tables = client.get_catalogs(catalog)
    files: list[FileRecord] = []
    rows: dict[str, int] = {}
    for key in tables.keys():
        table = tables[key]
        filename = output / f"{source_id}_{safe_name(key)}.csv"
        table.to_pandas().to_csv(filename, index=False)
        files.append(
            FileRecord.from_path(
                filename,
                source_product_id=str(key),
                source_url=f"https://vizier.cds.unistra.fr/viz-bin/VizieR?-source={catalog}",
            )
        )
        rows[str(key)] = int(len(table))
    record = DatasetRecord.create(
        source_id=source_id,
        source_state="ready",
        archive="VizieR/CDS",
        query=f"astroquery.vizier.get_catalogs({catalog!r}); columns=**; row_limit=-1",
        product_ids=rows.keys(),
        files=files,
        selection_rules={"catalog": catalog, "all_rows": True},
        notes=["Source catalogue tables copied without scientific filtering."],
    )
    write_manifest(record, output / f"{source_id}_manifest.json")
    return {"catalog": catalog, "tables": rows, "manifest_hash": record.manifest_hash}


def fetch_exoplanet_archive(output: Path) -> dict[str, object]:
    client = ExoplanetArchiveClient(timeout=120)
    census = client.census()
    spectra_query = (
        "select pl_name,spec_type,bibcode,authors,num_datapoints,instrument,"
        "facility,minwavelng,maxwavelng,mintranmid,maxtranmid,note,spec_path "
        "from spectra"
    )
    spectra = client.query(spectra_query)
    spectra_path = output / "nea_atmospheric_spectra_metadata.csv"
    spectra.to_csv(spectra_path, index=False)
    record = DatasetRecord.create(
        source_id="nasa_atmospheres",
        source_state="ready",
        archive="NASA Exoplanet Archive TAP",
        query=spectra_query,
        product_ids=tuple(str(x) for x in spectra["spec_path"].dropna().astype(str)),
        files=[
            FileRecord.from_path(
                spectra_path,
                source_product_id="spectra",
                source_url="https://exoplanetarchive.ipac.caltech.edu/",
            )
        ],
        selection_rules={"all_spectra_metadata_rows": True},
        notes=[
            "Only the spectrum-level metadata panel is accessible through TAP.",
            "Spectral datapoints remain publication/archive-native inputs.",
        ],
    )
    write_manifest(record, output / "nasa_atmospheres_manifest.json")
    return {
        "confirmed_planets": census.confirmed_planets,
        "toi_rows": census.toi_rows,
        "toi_dispositions": census.dispositions,
        "atmospheric_spectra_rows": int(len(spectra)),
        "unique_atmospheric_planets": int(spectra["pl_name"].nunique(dropna=True)),
        "manifest_hash": record.manifest_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/public_snapshot")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    summary: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "vizier": {},
    }
    for source_id, catalog in VIZIER_RELEASES.items():
        summary["vizier"][source_id] = fetch_vizier_catalog(source_id, catalog, output)
    summary["nasa_exoplanet_archive"] = fetch_exoplanet_archive(output)

    summary_path = output / "snapshot_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(summary_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
