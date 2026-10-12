"""Acquire the now-public SPORES-HWO II catalogue and archive context.

The catalogue is CC-BY-4.0.  Raw tables are cached locally under data/census;
release outputs retain queries, source identifiers and checksums.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

from astroquery.vizier import Vizier
import pandas as pd

from exolab.archives import ExoplanetArchiveClient
from exolab.provenance import DatasetRecord, FileRecord, canonical_json_sha256, write_manifest


CATALOG = "J/AJ/170/343"
CATALOG_URL = "https://cdsarc.cds.unistra.fr/viz-bin/cat/J/AJ/170/343"
README_URL = "https://cdsarc.cds.unistra.fr/ftp/J/AJ/170/343/ReadMe"
EXPECTED_ROWS = {
    "table3": 141,
    "table5": 153_902,
    "table6": 109,
    "table7": 74,
    "table9": 120,
    "inst": 28,
}
NEA_QUERY = (
    "select pl_name,hostname,hd_name,gaia_dr3_id,sy_pnum,discoverymethod,"
    "pl_orbper,pl_orbeccen,pl_bmasse from pscomppars where hd_name is not null"
)


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "open-exoplanet-evidence-lab/0.4"})
    with urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/census/spores_hwo_2026-10-12")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    acquired_at = datetime.now(timezone.utc)
    tables = Vizier(columns=["**"], row_limit=-1).get_catalogs(CATALOG)
    files: list[FileRecord] = []
    row_counts: dict[str, int] = {}
    for full_name in tables.keys():
        short_name = str(full_name).split("/")[-1]
        frame = tables[full_name].to_pandas()
        expected = EXPECTED_ROWS.get(short_name)
        if expected is None or len(frame) != expected:
            raise RuntimeError(
                f"unexpected {full_name} row count: {len(frame)}; expected {expected}"
            )
        path = output / f"{short_name}.csv"
        frame.to_csv(path, index=False)
        files.append(
            FileRecord.from_path(
                path,
                source_product_id=str(full_name),
                source_url=CATALOG_URL,
                pipeline_version="VizieR J/AJ/170/343 (Harada et al. 2025)",
            )
        )
        row_counts[short_name] = int(len(frame))

    readme = output / "ReadMe.txt"
    readme.write_text(fetch_text(README_URL), encoding="utf-8")
    files.append(
        FileRecord.from_path(
            readme,
            source_product_id=f"{CATALOG}/ReadMe",
            source_url=README_URL,
            pipeline_version="CDS catalogue documentation",
        )
    )

    nea = ExoplanetArchiveClient(timeout=180).query(NEA_QUERY)
    nea_path = output / "nasa_confirmed_planets_with_hd.csv"
    nea.to_csv(nea_path, index=False)
    files.append(
        FileRecord.from_path(
            nea_path,
            source_product_id="NASA Exoplanet Archive pscomppars",
            source_url=ExoplanetArchiveClient.endpoint,
            pipeline_version="NASA Exoplanet Archive composite parameters",
        )
    )

    query = {
        "vizier": f"astroquery.vizier.get_catalogs({CATALOG!r}); columns=**; row_limit=-1",
        "nasa_exoplanet_archive": NEA_QUERY,
    }
    record = DatasetRecord.create(
        source_id="spores_hwo_ii_2026-10-12",
        source_state="ready",
        archive="VizieR/CDS + NASA Exoplanet Archive TAP",
        query=json.dumps(query, sort_keys=True),
        product_ids=[f"{CATALOG}/{name}" for name in EXPECTED_ROWS]
        + ["NASA Exoplanet Archive pscomppars"],
        files=files,
        selection_rules={
            "vizier": "all public rows and all catalogue columns",
            "nasa_exoplanet_archive": "confirmed-planet composite rows with non-null HD identifier",
            "scientific_filtering": "none at acquisition",
        },
        notes=[
            "Catalogue access gate rechecked after 2026-10-04 and found open.",
            "VizieR ReadMe declares the catalogue CC-BY-4.0.",
            "NASA rows provide known-planet context only, not discovery validation.",
        ],
        access_time=acquired_at,
    )
    manifest_path = write_manifest(record, output / "manifest.json")
    summary = {
        "access_time_utc": acquired_at.isoformat(),
        "catalog": CATALOG,
        "catalog_bibcode": "2025AJ....170..343H",
        "catalog_license": "CC-BY-4.0",
        "row_counts": row_counts,
        "nasa_pscomppars_rows_with_hd": int(len(nea)),
        "queries": query,
        "query_hash": canonical_json_sha256(query),
        "manifest_hash": record.manifest_hash,
        "manifest": str(manifest_path),
    }
    (output / "acquisition_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
