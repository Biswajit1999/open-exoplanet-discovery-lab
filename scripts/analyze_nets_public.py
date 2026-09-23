"""Analyse public NETS III and NETS IV tables produced by build_public_snapshot.py.

The output is a reproducible diagnostic report, not a planet-discovery claim.
NETS III velocities are de-meaned by published survey run before period/activity
diagnostics so known run-to-run offsets do not masquerade as long-period power.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from exolab.activity import weighted_activity_regression
from exolab.periodogram import generalized_lomb_scargle
from exolab.timeseries import fit_sinusoid, weighted_rms


def _required(path: Path, columns: set[str]) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = columns - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing columns {sorted(missing)}")
    return frame


def _era_demean(frame: pd.DataFrame) -> np.ndarray:
    y = frame["rv_mps"].to_numpy(dtype=float)
    e = frame["erv_mps"].to_numpy(dtype=float)
    run = frame["Run"].astype(str).to_numpy()
    residual = y.copy()
    for label in sorted(set(run)):
        mask = run == label
        w = 1.0 / np.square(e[mask])
        mean = np.sum(w * y[mask]) / np.sum(w)
        residual[mask] -= mean
    return residual


def analyse_nets3(snapshot: Path, output: Path) -> dict[str, object]:
    rv = _required(
        snapshot / "nets3_j_aj_170_264_fig8.csv",
        {"Star", "BJD", "RVel", "e_RVel", "Run"},
    ).copy()
    activity = _required(
        snapshot / "nets3_j_aj_170_264_fig2.csv",
        {"Star", "BJD", "SHK", "e_SHK"},
    ).copy()
    survey = _required(
        snapshot / "nets3_j_aj_170_264_table1.csv",
        {"Star", "Nobs0.5", "Nobs1", "Nobs2"},
    ).copy()

    rv["rv_mps"] = pd.to_numeric(rv["RVel"], errors="coerce") * 1000.0
    rv["erv_mps"] = pd.to_numeric(rv["e_RVel"], errors="coerce") * 1000.0
    rv["BJD"] = pd.to_numeric(rv["BJD"], errors="coerce")
    rows: list[dict[str, object]] = []

    for star, group in rv.groupby("Star", sort=True):
        group = group.dropna(subset=["BJD", "rv_mps", "erv_mps"]).copy()
        group = group[group["erv_mps"] > 0].sort_values("BJD")
        if len(group) < 5:
            continue
        group["rv_era_resid_mps"] = _era_demean(group)
        t = group["BJD"].to_numpy(dtype=float)
        y = group["rv_era_resid_mps"].to_numpy(dtype=float)
        e = group["erv_mps"].to_numpy(dtype=float)
        baseline = float(np.ptp(t))
        max_period = min(500.0, max(3.0, baseline * 0.8))
        gls = generalized_lomb_scargle(
            t,
            y,
            e,
            min_period=2.0,
            max_period=max_period,
        )

        raw_centered = group["rv_mps"].to_numpy(dtype=float)
        raw_centered = raw_centered - np.average(
            raw_centered, weights=1.0 / np.square(e)
        )
        row: dict[str, object] = {
            "Star": star,
            "n_rv": int(len(group)),
            "n_runs": int(group["Run"].astype(str).nunique()),
            "baseline_days": baseline,
            "median_internal_error_mps": float(np.median(e)),
            "raw_wrms_mps": weighted_rms(raw_centered, e),
            "era_demeaned_wrms_mps": weighted_rms(y, e),
            "gls_best_period_days": gls.best_period,
            "gls_best_power": gls.best_power,
            "gls_analytic_fap": gls.false_alarm_probability,
            "activity_pairs": 0,
            "shk_slope_mps_per_unit": np.nan,
            "shk_slope_error": np.nan,
            "activity_corrected_wrms_mps": np.nan,
        }

        act = activity[activity["Star"].astype(str) == str(star)].copy()
        act["BJD"] = pd.to_numeric(act["BJD"], errors="coerce")
        act["SHK"] = pd.to_numeric(act["SHK"], errors="coerce")
        merged = group[["BJD", "rv_era_resid_mps", "erv_mps"]].merge(
            act[["BJD", "SHK"]], on="BJD", how="inner"
        ).dropna()
        if len(merged) >= 10 and merged["SHK"].nunique() > 2:
            regression = weighted_activity_regression(
                merged["rv_era_resid_mps"],
                merged["erv_mps"],
                merged["SHK"],
            )
            row.update(
                {
                    "activity_pairs": int(len(merged)),
                    "shk_slope_mps_per_unit": regression.slope,
                    "shk_slope_error": regression.slope_error,
                    "activity_corrected_wrms_mps": regression.corrected_wrms,
                }
            )
        rows.append(row)

    diagnostics = pd.DataFrame(rows).sort_values("Star")
    diagnostics.to_csv(output / "nets3_target_diagnostics.csv", index=False)

    summary = {
        "catalog_targets": int(len(survey)),
        "rv_rows": int(len(rv)),
        "activity_rows": int(len(activity)),
        "analysed_targets": int(len(diagnostics)),
        "median_observations_per_target": float(diagnostics["n_rv"].median()),
        "median_baseline_days": float(diagnostics["baseline_days"].median()),
        "median_internal_error_mps": float(diagnostics["median_internal_error_mps"].median()),
        "median_raw_wrms_mps": float(diagnostics["raw_wrms_mps"].median()),
        "median_era_demeaned_wrms_mps": float(diagnostics["era_demeaned_wrms_mps"].median()),
        "targets_with_shk_regression": int((diagnostics["activity_pairs"] >= 10).sum()),
        "targets_where_linear_shk_regression_reduces_wrms": int(
            (
                diagnostics["activity_corrected_wrms_mps"]
                < diagnostics["era_demeaned_wrms_mps"]
            ).fillna(False).sum()
        ),
        "interpretation": (
            "Exploratory diagnostics only. Periodogram peaks and linear activity "
            "correlations are not planet classifications."
        ),
    }
    return summary


def analyse_nets4(snapshot: Path, output: Path) -> dict[str, object]:
    frame = _required(
        snapshot / "nets4_hd190360_j_aj_171_286_table1.csv",
        {"BJD", "RVel", "e_RVel"},
    ).copy()
    for column in ("BJD", "RVel", "e_RVel"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["BJD", "RVel", "e_RVel"])
    frame = frame[frame["e_RVel"] > 0].sort_values("BJD")

    # VizieR J/AJ/171/286/table1 reports RV in m/s.
    t = frame["BJD"].to_numpy(dtype=float)
    y = frame["RVel"].to_numpy(dtype=float)
    e = frame["e_RVel"].to_numpy(dtype=float)
    groups = (
        frame["Run"].astype(str).to_numpy()
        if "Run" in frame.columns
        else np.array(["NEID"] * len(frame), dtype=object)
    )
    published_period = 88.69
    fit = fit_sinusoid(t, y, e, published_period, groups=groups, include_trend=True)
    residual_wrms = weighted_rms(fit.residuals, e)
    table = pd.DataFrame(
        [{
            "target": "HD 190360",
            "n_neid": int(len(frame)),
            "baseline_days": float(np.ptp(t)),
            "fixed_period_days": published_period,
            "neid_only_circular_k_mps": fit.semi_amplitude,
            "neid_only_circular_k_error_mps": fit.semi_amplitude_error,
            "phase_rad": fit.phase_radians,
            "trend_mps_per_day": fit.trend_per_day,
            "residual_wrms_mps": residual_wrms,
            "published_context_k_mps": 1.48,
            "published_context_period_days": 88.69,
        }]
    )
    table.to_csv(output / "nets4_hd190360_fixed_period_check.csv", index=False)
    return table.iloc[0].to_dict()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default="outputs/public_snapshot")
    parser.add_argument("--output", default="outputs/nets_analysis")
    args = parser.parse_args()
    snapshot = Path(args.snapshot)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    payload = {
        "nets3": analyse_nets3(snapshot, output),
        "nets4_hd190360": analyse_nets4(snapshot, output),
        "scope_note": (
            "These outputs validate public-data ingestion and transparent baseline "
            "diagnostics. They do not constitute new-planet discovery claims."
        ),
    }
    path = output / "analysis_summary.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
