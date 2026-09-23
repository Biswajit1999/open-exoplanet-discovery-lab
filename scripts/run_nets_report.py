"""Generate auditable NETS III descriptive diagnostics from frozen local inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from exolab.periodogram import gls
from exolab.rv import weighted_mean


def pick(frame: pd.DataFrame, names):
    lower = {str(c).strip().lower(): c for c in frame.columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    raise KeyError(f"None of {names} found in columns: {list(frame.columns)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rv", default="data/raw/nets3/rv.csv")
    parser.add_argument("--output", default="outputs/nets3")
    parser.add_argument("--min-period", type=float, default=1.0)
    parser.add_argument("--max-period", type=float, default=500.0)
    args = parser.parse_args()

    frame = pd.read_csv(args.rv)
    star_col = pick(frame, ["Star", "Name", "Target"])
    time_col = pick(frame, ["BJD", "BJD_TDB", "Time"])
    rv_col = pick(frame, ["RV", "RadVel", "vrad"])
    err_col = pick(frame, ["e_RV", "ERV", "RVerr", "eRV"])

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for star, group in frame.groupby(star_col, sort=True):
        g = group[[time_col, rv_col, err_col]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(g) < 5:
            continue
        t = g[time_col].to_numpy(float)
        y = g[rv_col].to_numpy(float)
        e = g[err_col].to_numpy(float)
        good = np.isfinite(t) & np.isfinite(y) & np.isfinite(e) & (e > 0)
        t, y, e = t[good], y[good], e[good]
        if len(t) < 5:
            continue
        mean, mean_err = weighted_mean(y, e)
        max_period = min(float(args.max_period), max(float(args.min_period) * 1.1, float(np.ptp(t))))
        pg = gls(t, y, e, min_period=args.min_period, max_period=max_period)
        rows.append(
            {
                "target": str(star),
                "n": len(t),
                "baseline_days": float(np.ptp(t)),
                "weighted_mean_rv": mean,
                "weighted_mean_rv_error": mean_err,
                "rms": float(np.std(y, ddof=1)),
                "median_formal_error": float(np.median(e)),
                "gls_best_period_days": pg.best_period,
                "gls_best_power": pg.best_power,
                "gls_analytic_fap": pg.false_alarm_probability,
            }
        )

    summary = pd.DataFrame(rows)
    summary.to_csv(out / "descriptive_summary.csv", index=False)
    metadata = {
        "n_targets_analyzed": int(len(summary)),
        "input": str(args.rv),
        "note": "GLS peaks are diagnostics, not planet claims. Analytic FAP is retained as a baseline and must be supplemented by null calibration for scientific interpretation.",
    }
    (out / "report_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
