"""Resolve the frozen NETS III sample to exact Gaia DR3 source identities."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd
from astroquery.simbad import Simbad

from exolab.gaia import GaiaTapClient, extract_gaia_dr3_identifier
from exolab.provenance import canonical_json_sha256, sha256_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target-table",
        type=Path,
        default=Path("outputs/public_snapshot/nets3_j_aj_170_264_table1.csv"),
    )
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/gaia_dr3_identity")
    )
    parser.add_argument("--software-commit", default="working-tree")
    args = parser.parse_args()

    target_table = pd.read_csv(args.target_table)
    if "Star" not in target_table:
        raise ValueError("target table must contain a Star column")
    targets = target_table["Star"].dropna().astype(str).drop_duplicates().tolist()
    if not targets:
        raise ValueError("target table contains no targets")

    simbad = Simbad()
    simbad.add_votable_fields("ids", "otype")
    simbad_payload = simbad.query_objects(targets, get_query_payload=True)
    simbad_table = simbad.query_objects(targets)
    if simbad_table is None:
        raise RuntimeError("SIMBAD returned no target identities")

    identity_rows: list[dict[str, object]] = []
    for row in simbad_table:
        target_index = int(row["object_number_id"]) - 1
        target = targets[target_index]
        match = extract_gaia_dr3_identifier(str(row["ids"]))
        identity_rows.append(
            {
                "target": target,
                "simbad_main_id": str(row["main_id"]),
                "simbad_object_type": str(row["otype"]),
                "simbad_ra_deg": float(row["ra"]),
                "simbad_dec_deg": float(row["dec"]),
                "simbad_coordinate_bibcode": str(row["coo_bibcode"]),
                "gaia_dr3_source_id": match.source_id,
                "gaia_identifier_count": match.count,
                "identity_status": match.status,
                "match_method": "exact SIMBAD identifier",
                "match_radius_arcsec": None,
            }
        )

    identity = pd.DataFrame(identity_rows)
    if identity["target"].duplicated().any():
        duplicates = sorted(identity.loc[identity["target"].duplicated(), "target"])
        raise RuntimeError(f"SIMBAD returned duplicate target rows: {duplicates}")
    missing_targets = sorted(set(targets) - set(identity["target"]))
    for target in missing_targets:
        identity_rows.append(
            {
                "target": target,
                "identity_status": "unmatched",
                "gaia_identifier_count": 0,
                "match_method": "exact SIMBAD identifier",
                "match_radius_arcsec": None,
            }
        )
    identity = pd.DataFrame(identity_rows)

    unique_ids = identity.loc[
        identity["identity_status"] == "unique", "gaia_dr3_source_id"
    ].astype(str)
    gaia, gaia_query = GaiaTapClient().query_source_ids(unique_ids)
    returned_ids = set(gaia["source_id"].astype(str))
    missing_gaia = sorted(set(unique_ids) - returned_ids)
    if missing_gaia:
        raise RuntimeError(f"Gaia DR3 did not return exact source IDs: {missing_gaia}")
    gaia = gaia.rename(columns={column: f"gaia_{column}" for column in gaia.columns})
    resolved = identity.merge(
        gaia,
        left_on="gaia_dr3_source_id",
        right_on="gaia_source_id",
        how="left",
        validate="one_to_one",
    ).sort_values("target")
    resolved["astrometric_context_boundary"] = (
        "identity/context only; RUWE and other Gaia fields are not companion classifications"
    )

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    table_path = output / "nets3_gaia_dr3_identity.csv"
    resolved.to_csv(table_path, index=False)
    (output / "gaia_query.adql").write_text(gaia_query + "\n", encoding="utf-8")
    query_record = {
        "service": "SIMBAD TAP",
        "endpoint": str(simbad.tap.baseurl),
        "query": simbad_payload["QUERY"],
        "uploaded_targets": targets,
        "fields": ["main_id", "ra", "dec", "coo_bibcode", "otype", "ids"],
    }
    (output / "simbad_query.json").write_text(
        json.dumps(query_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    status_counts = {
        str(key): int(value)
        for key, value in resolved["identity_status"].value_counts().items()
    }
    gaia_rows = int(resolved["gaia_source_id"].notna().sum())
    summary = {
        "schema_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "software_commit": args.software_commit,
        "target_source": "VizieR J/AJ/170/264 table1",
        "target_table_sha256": sha256_file(args.target_table),
        "target_count": len(targets),
        "identity_status_counts": status_counts,
        "gaia_dr3_rows": gaia_rows,
        "simbad_query_hash": canonical_json_sha256(query_record),
        "gaia_query_hash": canonical_json_sha256({"adql": gaia_query}),
        "interpretation": (
            "Exact Gaia DR3 identity and public astrometric context only. "
            "No Gaia field is interpreted as evidence for a companion."
        ),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checksums = {
        path.name: sha256_file(path)
        for path in sorted(output.iterdir())
        if path.is_file() and path.name != "checksums.json"
    }
    (output / "checksums.json").write_text(
        json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
