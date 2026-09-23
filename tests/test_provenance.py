from datetime import datetime, timezone
import json

import pytest

from exolab.provenance import (
    DatasetRecord,
    FileRecord,
    canonical_json_sha256,
    verify_manifest,
    write_manifest,
)


def test_canonical_json_hash_is_order_invariant():
    left = {"b": 2, "a": [1, 2, 3]}
    right = {"a": [1, 2, 3], "b": 2}
    assert canonical_json_sha256(left) == canonical_json_sha256(right)


def test_dataset_record_rejects_unknown_state():
    with pytest.raises(ValueError):
        DatasetRecord.create(
            source_id="example",
            source_state="mystery",
            archive="archive",
            query="select *",
        )


def test_manifest_round_trip_and_file_integrity(tmp_path):
    data_file = tmp_path / "rv.csv"
    data_file.write_text("bjd,rv,erv\n2450000.0,0.1,0.3\n", encoding="utf-8")

    record = DatasetRecord.create(
        source_id="nets3",
        source_state="ready",
        archive="VizieR",
        query="fixed test query",
        product_ids=["row-1"],
        files=[
            FileRecord.from_path(
                data_file,
                source_product_id="row-1",
                source_url="https://example.invalid/row-1",
                pipeline_version="test",
            )
        ],
        selection_rules={"include": "all test rows"},
        access_time=datetime(2026, 9, 23, 6, 0, tzinfo=timezone.utc),
    )

    manifest_path = write_manifest(record, tmp_path / "manifest.json")
    assert verify_manifest(manifest_path)

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["source_id"] == "nets3"
    assert payload["access_time_utc"] == "2026-09-23T06:00:00Z"
    assert payload["manifest_hash"] == record.manifest_hash

    data_file.write_text("tampered\n", encoding="utf-8")
    assert not verify_manifest(manifest_path)


def test_manifest_detects_metadata_tampering(tmp_path):
    record = DatasetRecord.create(
        source_id="tess_sector_107",
        source_state="active",
        archive="MAST",
        query="sector=107",
        access_time=datetime(2026, 9, 23, 6, 0, tzinfo=timezone.utc),
    )
    path = write_manifest(record, tmp_path / "manifest.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["query"] = "sector=106"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert not verify_manifest(path)
