"""ESO ObsCore acquisition and overlap-census helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .chromatic import simultaneity_counts
from .tap import TAPClient


class ESOTapClient(TAPClient):
    def __init__(self, timeout: int = 180):
        super().__init__("https://archive.eso.org/tap_obs/sync", timeout=timeout)

    def instrument_products(self, instrument: str, *, public_only: bool = True) -> pd.DataFrame:
        safe = instrument.replace("'", "''")
        rights = " AND data_rights='Public'" if public_only else ""
        adql = f"""
        SELECT
          obs_publisher_did, obs_id, target_name, s_ra, s_dec,
          t_min, t_max, t_exptime, instrument_name, obs_collection,
          dataproduct_type, calib_level, em_min, em_max, em_res_power,
          data_rights, access_url
        FROM ivoa.ObsCore
        WHERE UPPER(instrument_name)=UPPER('{safe}')
          AND dataproduct_type='spectrum'
          {rights}
        """
        return self.query_csv(adql)


def _clean_epoch_rows(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["t_min"] = pd.to_numeric(out["t_min"], errors="coerce")
    out["s_ra"] = pd.to_numeric(out["s_ra"], errors="coerce")
    out["s_dec"] = pd.to_numeric(out["s_dec"], errors="coerce")
    out = out.dropna(subset=["t_min", "s_ra", "s_dec", "target_name"])
    # Phase-3 archives may expose several products per observing epoch.
    out["_epoch_key"] = (
        out["target_name"].astype(str).str.strip().str.upper()
        + "|"
        + out["t_min"].round(7).astype(str)
    )
    return out.drop_duplicates("_epoch_key").reset_index(drop=True)


def _angsep_arcsec(ra1, dec1, ra2, dec2):
    r1, d1, r2, d2 = np.deg2rad([ra1, dec1, ra2, dec2])
    arg = np.sin(d1) * np.sin(d2) + np.cos(d1) * np.cos(d2) * np.cos(r1 - r2)
    return float(np.rad2deg(np.arccos(np.clip(arg, -1, 1))) * 3600.0)


def overlap_census(nirps: pd.DataFrame, harps: pd.DataFrame, *, max_sep_arcsec: float = 3.0) -> pd.DataFrame:
    """Crossmatch NIRPS target groups to the nearest HARPS target by sky position."""
    n = _clean_epoch_rows(nirps)
    h = _clean_epoch_rows(harps)
    rows = []
    hgroups = list(h.groupby(h["target_name"].astype(str).str.strip(), sort=False))

    for nname, ng in n.groupby(n["target_name"].astype(str).str.strip(), sort=True):
        nra, ndec = float(np.median(ng["s_ra"])), float(np.median(ng["s_dec"]))
        best = None
        for hname, hg in hgroups:
            hra, hdec = float(np.median(hg["s_ra"])), float(np.median(hg["s_dec"]))
            sep = _angsep_arcsec(nra, ndec, hra, hdec)
            if best is None or sep < best[0]:
                best = (sep, hname, hg)
        if best is None or best[0] > max_sep_arcsec:
            rows.append(
                {
                    "nirps_target": nname,
                    "harps_target": None,
                    "sep_arcsec": np.nan,
                    "n_nirps": len(ng),
                    "n_harps": 0,
                    "nirps_baseline_days": float(np.ptp(ng["t_min"])) if len(ng) > 1 else 0.0,
                    "harps_baseline_days": np.nan,
                    "pairs_1h": 0,
                    "pairs_6h": 0,
                    "pairs_1d": 0,
                    "pairs_3d": 0,
                    "pairs_7d": 0,
                }
            )
            continue
        sep, hname, hg = best
        counts = simultaneity_counts(
            ng["t_min"].to_numpy(float),
            hg["t_min"].to_numpy(float),
            windows_hours=(1, 6, 24, 72, 168),
        )
        rows.append(
            {
                "nirps_target": nname,
                "harps_target": hname,
                "sep_arcsec": sep,
                "n_nirps": len(ng),
                "n_harps": len(hg),
                "nirps_baseline_days": float(np.ptp(ng["t_min"])) if len(ng) > 1 else 0.0,
                "harps_baseline_days": float(np.ptp(hg["t_min"])) if len(hg) > 1 else 0.0,
                "pairs_1h": counts[1.0],
                "pairs_6h": counts[6.0],
                "pairs_1d": counts[24.0],
                "pairs_3d": counts[72.0],
                "pairs_7d": counts[168.0],
            }
        )
    return pd.DataFrame(rows).sort_values(["n_nirps", "n_harps"], ascending=False).reset_index(drop=True)
