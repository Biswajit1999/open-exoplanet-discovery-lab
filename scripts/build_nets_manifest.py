"""Acquire the public NETS III VizieR tables and write a frozen manifest."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from exolab.provenance import DatasetRecord, FileRecord, write_manifest
from exolab.registry import require_source
from exolab.vizier import VizierClient


TABLES = {
    "table1": "J/AJ/170/264/table1",
    "activity": "J/AJ/170/264/fig2",
    "rv": "J/AJ/170/264/fig8",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/raw/nets3")
    parser.add_argument("--manifest", default="data/manifests/nets3.json")
    args = parser.parse_args()

    require_source("nets3")
    out = Path(args.output)
    client = VizierClient()
    files = []
    for name, source in TABLES.items():
        path = client.save_table(source, out / f"{name}.csv")
        files.append(
            FileRecord.from_path(
                path,
                source_product_id=source,
                source_url=f"https://vizier.cds.unistra.fr/viz-bin/VizieR-3?-source={source}",
                pipeline_version="VizieR catalogue J/AJ/170/264",
            )
        )

    record = DatasetRecord.create(
        source_id="nets3",
        source_state="ready",
        archive="VizieR/CDS",
        query="; ".join(TABLES.values()),
        files=files,
        product_ids=TABLES.values(),
        selection_rules={"scope": "all public rows; no local scientific rejection at acquisition"},
        notes=(
            "NETS III catalogue: 41 systems; activity and RV tables each contain 5920 rows according to VizieR metadata.",
            "Instrument-era/quality exclusions are applied downstream and recorded separately.",
        ),
        access_time=datetime.now(timezone.utc),
    )
    path = write_manifest(record, args.manifest)
    print(path)
    print(record.manifest_hash)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
