"""Cross-link SPORES-HWO targets to the public MAST TESS-SVC catalogue.

TESS-SVC contains significant 0.01--13 day variability measurements from one
selected Prime-Mission sector.  A match is activity/variability context; a
non-match is not evidence that a star is photometrically quiet.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from astroquery.simbad import Simbad
import pandas as pd

from exolab.provenance import canonical_json_sha256, sha256_file
from exolab.spores import extract_tic_identifier


SVC_URL = "https://archive.stsci.edu/hlsps/tess-svc/hlsp_tess-svc_tess_lcf_all-s0001-s0026_tess_v1.0_cat.csv"
SVC_DOI = "10.17909/f8pz-vj63"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spores", default="data/census/spores_hwo_2026-10-12/table3.csv")
    parser.add_argument(
        "--svc",
        default="data/census/tess_svc_v1/hlsp_tess-svc_tess_lcf_all-s0001-s0026_tess_v1.0_cat.csv",
    )
    parser.add_argument("--output", default="outputs/spores_tess_svc_context")
    parser.add_argument("--software-commit", default="working-tree")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    targets = pd.read_csv(args.spores)
    targets["target"] = targets["HD"].astype(str).str.strip()
    names = targets["SimbadName"].fillna(targets["target"].map(lambda x: f"HD {x}"))
    names = names.astype(str).map(lambda value: " ".join(value.split()))
    targets["simbad_query_name"] = names
    targets["_spores_row"] = range(len(targets))
    simbad = Simbad()
    simbad.add_votable_fields("ids")
    identifiers = simbad.query_objects(names.tolist()).to_pandas()
    identifiers = identifiers.rename(
        columns={
            "user_specified_id": "simbad_returned_name",
            "main_id": "simbad_main_id",
            "object_number_id": "_simbad_object_number",
        }
    )
    identifiers["tic_id"] = identifiers["ids"].map(extract_tic_identifier)
    if len(identifiers) != len(targets):
        raise RuntimeError(
            f"SIMBAD returned {len(identifiers)} rows for {len(targets)} target queries"
        )
    identifiers["_spores_row"] = identifiers["_simbad_object_number"].astype(int) - 1
    if set(identifiers["_spores_row"]) != set(targets["_spores_row"]):
        raise RuntimeError("SIMBAD object-number identifiers do not cover every SPORES query row")
    returned_names = identifiers.sort_values("_spores_row")["simbad_returned_name"].map(
        lambda value: " ".join(str(value).split())
    )
    if returned_names.tolist() != names.tolist():
        raise RuntimeError("SIMBAD response order/name alignment failed")
    targets = targets.merge(
        identifiers[["_spores_row", "simbad_returned_name", "simbad_main_id", "tic_id"]],
        on="_spores_row",
        how="left",
        validate="one_to_one",
    ).drop(columns="_spores_row")

    usecols = [
        "tess_id",
        "Solution",
        "Sector",
        "period_var_1",
        "period_var_2",
        "period_var_uncert_1",
        "period_var_uncert_2",
        "amp_var_1",
        "amp_var_2",
        "amp_var_uncert_1",
        "amp_var_uncert_2",
        "power_1",
        "power_2",
        "ra",
        "dec",
        "GAIA",
        "Tmag",
        "Teff",
    ]
    svc = pd.read_csv(args.svc, usecols=usecols, low_memory=False)
    svc["tic_id"] = svc["tess_id"].astype("Int64").astype(str)
    if svc["tic_id"].duplicated().any():
        raise RuntimeError("TESS-SVC combined catalogue contains duplicate TIC identifiers")
    # pandas treats missing values as equal merge keys.  Six SPORES targets do
    # not currently resolve to a TIC identifier, so a direct merge on tic_id
    # would create a many-to-many block of false matches.  Give every unresolved
    # target a deliberately non-catalogue join key while retaining tic_id as NA.
    targets["_tic_join_key"] = targets["tic_id"]
    missing_tic = targets["tic_id"].isna()
    targets.loc[missing_tic, "_tic_join_key"] = targets.loc[missing_tic].apply(
        lambda row: f"unresolved-spores-row-{row.name}", axis=1
    )
    svc["_tic_join_key"] = svc["tic_id"]
    joined = targets.merge(
        svc.drop(columns=["tess_id", "tic_id"]),
        on="_tic_join_key",
        how="left",
        validate="many_to_one",
        suffixes=("_spores", "_svc"),
    ).drop(columns="_tic_join_key")
    if len(joined) != len(targets):
        raise RuntimeError(
            f"TESS-SVC join changed the SPORES row count: {len(targets)} -> {len(joined)}"
        )
    joined["context_state"] = "no_tic_identifier"
    joined.loc[joined["tic_id"].notna(), "context_state"] = "no_tess_svc_variability_match"
    joined.loc[joined["Solution"].notna(), "context_state"] = "tess_svc_variability_match"
    joined["claim_boundary"] = (
        "TESS-SVC single-sector 0.01-13 d periodic-variability context only; "
        "not a rotation or planet classification. Non-match is not a quiet-star label."
    )
    joined.to_csv(output / "spores_tess_svc_context.csv", index=False)

    query_record = {
        "simbad_objects": names.tolist(),
        "simbad_fields": ["main_id", "ids"],
        "mast_hlsp": SVC_URL,
        "mast_doi": SVC_DOI,
        "mast_release": "TESS-SVC v1.0; TESS Prime Mission sectors 1-26",
        "scope": "significant periodic variability on 0.01-13 day timescales from one selected sector",
        "match": "exact TIC identifier extracted from SIMBAD identifier list",
        "selected_field_semantics": {
            "period_var_1/2": "catalogue variability periods in days",
            "amp_var_1/2": "catalogue fitted variability amplitudes in ppm",
            "power_1/2": "catalogue variability signal powers",
            "Solution": "1sin, 2sin, or acf catalogue solution family",
        },
    }
    (output / "query.json").write_text(
        json.dumps(query_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    counts = joined["context_state"].value_counts().sort_index().to_dict()
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "software_commit": args.software_commit,
        "spores_targets": int(len(targets)),
        "tess_svc_catalog_rows": int(len(svc)),
        "context_state_counts": {key: int(value) for key, value in counts.items()},
        "query_hash": canonical_json_sha256(query_record),
        "source_checksums": {
            "spores_table3": sha256_file(args.spores),
            "tess_svc_v1": sha256_file(args.svc),
        },
        "interpretation": (
            "Independent MAST periodic-variability context. Matches are not assigned "
            "a stellar-rotation or planetary interpretation; non-matches are not null detections."
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
