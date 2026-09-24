import json
from pathlib import Path

from exolab.web_release import build_web_release_data, write_web_release_data


REPOSITORY = Path(__file__).resolve().parents[1]


def test_web_release_contract_matches_frozen_results(tmp_path):
    payload = build_web_release_data(REPOSITORY)

    assert payload["schema_version"] == "1.0.0"
    assert len(payload["targets"]) == 40
    assert all(target["identity"]["identity_status"] == "unique" for target in payload["targets"])
    assert len({target["identity"]["gaia_dr3_source_id"] for target in payload["targets"]}) == 40
    assert {row["model"] for row in payload["completeness"]["population"]} == {
        "baseline",
        "era",
        "era_activity",
    }
    assert len(payload["completeness"]["delta"]) == 36
    assert all(row["k90_mps"] is None for row in payload["completeness"]["k_thresholds"])
    assert len(payload["provenance"]) == 5

    output = write_web_release_data(REPOSITORY, tmp_path / "lab.json")
    decoded = json.loads(output.read_text(encoding="utf-8"))
    assert decoded == payload
    assert "NaN" not in output.read_text(encoding="utf-8")

    committed = json.loads(
        (REPOSITORY / "web" / "public" / "data" / "lab.json").read_text(
            encoding="utf-8"
        )
    )
    assert committed == payload
