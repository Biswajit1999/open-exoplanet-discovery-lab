"""Build the versioned, read-only data contract consumed by the web interface."""

from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


RELEASE_DIRECTORY = "nets3_completeness_2026-09-23"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _number(value: str) -> float | None:
    if value == "" or value.lower() == "nan":
        return None
    return float(value)


def build_web_release_data(repository: Path) -> dict[str, Any]:
    """Return a compact web data product derived only from frozen release files."""

    results = repository / "results"
    nets = results / RELEASE_DIRECTORY
    tess = results / "tess_hd10780_2026-09-23"
    atmosphere = results / "atmosphere_55cnce_2026-09-23"
    eso = results / "eso_nirps_harps_2026-09-23"
    gaia = results / "gaia_dr3_identity_2026-09-24"

    nets_summary = _read_json(nets / "summary.json")
    tess_summary = _read_json(tess / "summary.json")
    atmosphere_summary = _read_json(atmosphere / "summary.json")
    eso_summary = _read_json(eso / "census_summary.json")
    eso_manifest = _read_json(eso / "nirps_harps_overlap_manifest.json")
    gaia_summary = _read_json(gaia / "summary.json")
    gaia_by_target = {
        row["target"]: row for row in _read_csv(gaia / "nets3_gaia_dr3_identity.csv")
    }

    target_completeness = _read_csv(nets / "target_completeness.csv")
    completeness_by_target: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    cell_by_target: dict[tuple[str, float, float, str], float] = {}
    for row in target_completeness:
        target = row["target"]
        model = row["model"]
        value = float(row["completeness"])
        completeness_by_target[target][model].append(value)
        cell_by_target[
            (target, float(row["period"]), float(row["semi_amplitude"]), model)
        ] = value

    targets = []
    for row in _read_csv(nets / "target_summary.csv"):
        target = row["target"]
        identity = gaia_by_target[target]
        deltas = []
        for (cell_target, period, amplitude, model), value in cell_by_target.items():
            if cell_target != target or model != "era_activity":
                continue
            baseline = cell_by_target[(target, period, amplitude, "baseline")]
            deltas.append(value - baseline)
        targets.append(
            {
                "id": target.lower().replace(" ", "-"),
                "target": target,
                "observations": int(row["n_observations"]),
                "runs": int(row["n_runs"]),
                "baseline_days": float(row["baseline_days"]),
                "median_formal_error_mps": float(row["median_formal_error_mps"]),
                "mean_completeness": {
                    model: statistics.fmean(values)
                    for model, values in completeness_by_target[target].items()
                },
                "mean_delta_era_activity_minus_baseline": statistics.fmean(deltas),
                "power_thresholds": {
                    "baseline": float(row["baseline_power_threshold"]),
                    "era": float(row["era_power_threshold"]),
                    "era_activity": float(row["era_activity_power_threshold"]),
                },
                "identity": {
                    "simbad_main_id": identity["simbad_main_id"],
                    "gaia_dr3_source_id": identity["gaia_dr3_source_id"],
                    "identity_status": identity["identity_status"],
                    "reference_epoch": float(identity["gaia_ref_epoch"]),
                    "parallax_mas": float(identity["gaia_parallax"]),
                    "parallax_error_mas": float(identity["gaia_parallax_error"]),
                    "phot_g_mean_mag": float(identity["gaia_phot_g_mean_mag"]),
                    "bp_rp_mag": float(identity["gaia_bp_rp"]),
                    "ruwe": float(identity["gaia_ruwe"]),
                    "duplicated_source": identity["gaia_duplicated_source"].lower()
                    == "true",
                },
            }
        )

    population = [
        {
            "model": row["model"],
            "period_days": float(row["period"]),
            "semi_amplitude_mps": float(row["semi_amplitude"]),
            "mean_completeness": float(row["mean_completeness"]),
            "median_completeness": float(row["median_completeness"]),
            "targets": int(row["n_targets"]),
        }
        for row in _read_csv(nets / "population_completeness.csv")
    ]
    delta = [
        {
            "period_days": float(row["period"]),
            "semi_amplitude_mps": float(row["semi_amplitude"]),
            "delta_completeness": float(row["delta_completeness"]),
        }
        for row in _read_csv(nets / "delta_completeness.csv")
    ]
    k_thresholds = [
        {
            "model": row["model"],
            "period_days": float(row["period"]),
            "k50_mps": _number(row["k50"]),
            "k90_mps": _number(row["k90"]),
        }
        for row in _read_csv(nets / "population_k50_k90.csv")
    ]

    transfer_groups: dict[float, dict[str, list[float]]] = defaultdict(
        lambda: {"median": [], "worst": []}
    )
    for row in _read_csv(nets / "leave_one_era_out_transfer.csv"):
        period = float(row["period"])
        transfer_groups[period]["median"].append(float(row["median_k_transfer"]))
        transfer_groups[period]["worst"].append(float(row["worst_phase_k_transfer"]))
    transfer = [
        {
            "period_days": period,
            "median_transfer": statistics.median(values["median"]),
            "worst_phase_median": statistics.median(values["worst"]),
        }
        for period, values in sorted(transfer_groups.items())
    ]

    provenance = [
        {
            "id": "nets3-completeness",
            "title": "NETS III completeness",
            "claim_label": "ROBUSTNESS TEST",
            "evidence_state": "measured sensitivity",
            "archive": "VizieR / NEID Earth Twin Survey III",
            "source_id": "J/AJ/170/264",
            "generated_at_utc": nets_summary["generated_at_utc"],
            "software_commit": nets_summary["software_commit"],
            "configuration_hash": nets_summary["configuration_hash"],
            "primary_output": "results/nets3_completeness_2026-09-23/target_completeness.csv",
            "checksum_record": "results/nets3_completeness_2026-09-23/checksums.json",
            "boundary": "Circular injection/recovery sensitivity; no candidate classification.",
        },
        {
            "id": "tess-hd10780",
            "title": "HD 10780 temporal context",
            "claim_label": "CROSS-ARCHIVE TEST",
            "evidence_state": "activity context",
            "archive": "MAST / TESS SPOC 120 s",
            "source_id": "TESS sectors 24, 25, 85 and 86",
            "generated_at_utc": tess_summary["generated_at_utc"],
            "software_commit": tess_summary["software_commit"],
            "configuration_hash": tess_summary["configuration_hash"],
            "primary_output": "results/tess_hd10780_2026-09-23/summary.json",
            "checksum_record": "results/tess_hd10780_2026-09-23/checksums.json",
            "boundary": "Neither a planet confirmation nor a secure rotation measurement.",
        },
        {
            "id": "atmosphere-55cnce",
            "title": "55 Cnc e reproducibility",
            "claim_label": "ROBUSTNESS TEST",
            "evidence_state": "descriptive reproducibility bound",
            "archive": "NASA Exoplanet Archive atmospheric spectroscopy",
            "source_id": atmosphere_summary["bibcode"],
            "generated_at_utc": atmosphere_summary["generated_at_utc"],
            "software_commit": atmosphere_summary["software_commit"],
            "configuration_hash": atmosphere_summary["configuration_hash"],
            "primary_output": "results/atmosphere_55cnce_2026-09-23/common_band_visit_means.csv",
            "checksum_record": "results/atmosphere_55cnce_2026-09-23/checksums.json",
            "boundary": "No independent-pipeline significance or atmospheric composition claim.",
        },
        {
            "id": "eso-nirps-harps",
            "title": "NIRPS × HARPS overlap",
            "claim_label": "CROSS-ARCHIVE TEST",
            "evidence_state": "archive census",
            "archive": "ESO Science Archive TAP",
            "source_id": eso_manifest["source_id"],
            "generated_at_utc": eso_summary["generated_at_utc"],
            "software_commit": None,
            "configuration_hash": eso_summary["manifest_hash"],
            "primary_output": "results/eso_nirps_harps_2026-09-23/nirps_harps_overlap_summary.csv",
            "checksum_record": "results/eso_nirps_harps_2026-09-23/nirps_harps_overlap_manifest.json",
            "boundary": "Product census only; no homogeneous chromatic RV comparison.",
        },
        {
            "id": "gaia-dr3-identity",
            "title": "NETS III Gaia DR3 identities",
            "claim_label": "IDENTITY LAYER",
            "evidence_state": "canonical archive linkage",
            "archive": "SIMBAD TAP / Gaia Archive DR3",
            "source_id": "41 exact Gaia DR3 source identifiers",
            "generated_at_utc": gaia_summary["generated_at_utc"],
            "software_commit": gaia_summary["software_commit"],
            "configuration_hash": gaia_summary["gaia_query_hash"],
            "primary_output": "results/gaia_dr3_identity_2026-09-24/nets3_gaia_dr3_identity.csv",
            "checksum_record": "results/gaia_dr3_identity_2026-09-24/checksums.json",
            "boundary": "Identity and public astrometric context only; no companion classification.",
        },
    ]

    return {
        "schema_version": "1.0.0",
        "release": "0.3.1",
        "snapshot_date": "2026-09-24",
        "targets": targets,
        "completeness": {
            "models": nets_summary["models"],
            "population": population,
            "delta": delta,
            "k_thresholds": k_thresholds,
            "leave_one_era_out": transfer,
        },
        "provenance": provenance,
        "literature_gates": [
            {
                "stream": "NETS III",
                "status": "bounded",
                "increment": "Completeness sensitivity to alternative run/activity models and held-out eras.",
                "excluded_claim": "No novelty claim for RVSearch or periodogram reproduction.",
            },
            {
                "stream": "NIRPS × HARPS",
                "status": "census only",
                "increment": "Public overlap census with NIRPS reduction provenance encoded.",
                "excluded_claim": "No generic claim that activity weakens in the near infrared.",
            },
            {
                "stream": "Atmospheres",
                "status": "bounded",
                "increment": "Empirical visit/reduction reproducibility floor.",
                "excluded_claim": "No novelty claim for plotting archived spectra or inferring composition.",
            },
            {
                "stream": "SPORES-HWO II / Gaia DR4",
                "status": "gated",
                "increment": "None emitted until the required public data and schema are verified.",
                "excluded_claim": "No result depends on unavailable products.",
            },
        ],
    }


def write_web_release_data(repository: Path, output: Path) -> Path:
    payload = build_web_release_data(repository)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return output

