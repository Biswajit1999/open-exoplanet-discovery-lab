"""Minimal, auditable ESO TAP client and ObsCore query builders."""

from __future__ import annotations

from io import BytesIO
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from astropy.io.votable import parse_single_table

from .chromatic import simultaneity_counts


class ESOArchiveClient:
    endpoint = "https://archive.eso.org/tap_obs/sync"

    def __init__(self, timeout: int = 120) -> None:
        self.timeout = int(timeout)

    def query(self, adql: str, *, maxrec: int | None = None) -> pd.DataFrame:
        params = {
            "REQUEST": "doQuery",
            "LANG": "ADQL",
            "FORMAT": "votable",
            "QUERY": " ".join(adql.split()),
        }
        if maxrec is not None:
            params["MAXREC"] = str(int(maxrec))
        request = Request(
            f"{self.endpoint}?{urlencode(params)}",
            headers={"User-Agent": "open-exoplanet-evidence-lab/0.3"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"ESO TAP HTTP {exc.code} for ADQL={params['QUERY']!r}: {detail[:4000]}"
            ) from exc
        table = parse_single_table(BytesIO(payload)).to_table()
        return table.to_pandas()

    def obscore_columns(self) -> list[str]:
        frame = self.query(
            "SELECT column_name FROM TAP_SCHEMA.columns "
            "WHERE table_name='ivoa.ObsCore'"
        )
        column = "column_name" if "column_name" in frame.columns else frame.columns[0]
        return [str(value) for value in frame[column].dropna()]


class ESOTapClient(ESOArchiveClient):
    """Compatibility adapter exposing the release-0.2 inventory method."""

    def instrument_products(
        self, instrument: str, *, public_only: bool = True
    ) -> pd.DataFrame:
        columns = self.obscore_columns()
        query = instrument_inventory_query(instrument, available_columns=columns)
        if not public_only and "data_rights='Public'" in query:
            query = query.replace(" AND data_rights='Public'", "")
        return self.query(query)


PREFERRED_OBSCORE_COLUMNS = (
    "target_name",
    "s_ra",
    "s_dec",
    "t_min",
    "t_max",
    "t_exptime",
    "dp_id",
    "obs_id",
    "obs_publisher_did",
    "obs_collection",
    "instrument_name",
    "dataproduct_type",
    "dataproduct_subtype",
    "calib_level",
    "obs_release_date",
    "access_url",
    "access_estsize",
    "data_rights",
)


def _query_columns(available_columns: list[str] | None = None) -> list[str]:
    if available_columns is None:
        # Defaults are ESO-documented examples plus ObsCore fields. Live archive
        # workflows discover the schema and pass it explicitly.
        return list(PREFERRED_OBSCORE_COLUMNS)
    available = {str(column).lower(): str(column) for column in available_columns}
    selected = [
        available[name.lower()]
        for name in PREFERRED_OBSCORE_COLUMNS
        if name.lower() in available
    ]
    required = {"target_name", "s_ra", "s_dec", "t_min", "instrument_name"}
    if not required.issubset({value.lower() for value in selected}):
        raise RuntimeError(
            "ESO ObsCore schema does not expose the fields required for the census"
        )
    return selected


def instrument_inventory_query(
    instrument_name: str,
    *,
    available_columns: list[str] | None = None,
) -> str:
    safe = instrument_name.replace("'", "''")
    columns = _query_columns(available_columns)
    public_clause = ""
    if any(column.lower() == "data_rights" for column in columns):
        public_clause = " AND data_rights='Public'"
    return f"""
        SELECT {','.join(columns)}
        FROM ivoa.ObsCore
        WHERE instrument_name = '{safe}'
        {public_clause}
    """


def target_instrument_query(
    instrument_name: str,
    *,
    ra_deg: float,
    dec_deg: float,
    radius_deg: float = 5.0 / 3600.0,
    available_columns: list[str] | None = None,
) -> str:
    safe = instrument_name.replace("'", "''")
    columns = _query_columns(available_columns)
    public_clause = ""
    if any(column.lower() == "data_rights" for column in columns):
        public_clause = " AND data_rights='Public'"
    return f"""
        SELECT {','.join(columns)}
        FROM ivoa.ObsCore
        WHERE instrument_name = '{safe}'
          {public_clause}
          AND 1 = CONTAINS(
              POINT('ICRS', s_ra, s_dec),
              CIRCLE('ICRS', {float(ra_deg)}, {float(dec_deg)}, {float(radius_deg)})
          )
    """


def _clean_epoch_rows(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in ("t_min", "s_ra", "s_dec"):
        out[column] = pd.to_numeric(out[column], errors="coerce")
    out = out.dropna(subset=["t_min", "s_ra", "s_dec", "target_name"])
    out["_epoch_key"] = (
        out["target_name"].astype(str).str.strip().str.upper()
        + "|"
        + out["t_min"].round(7).astype(str)
    )
    return out.drop_duplicates("_epoch_key").reset_index(drop=True)


def _angsep_arcsec(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    r1, d1, r2, d2 = np.deg2rad([ra1, dec1, ra2, dec2])
    argument = np.sin(d1) * np.sin(d2) + np.cos(d1) * np.cos(d2) * np.cos(r1 - r2)
    return float(np.rad2deg(np.arccos(np.clip(argument, -1, 1))) * 3600.0)


def overlap_census(
    nirps: pd.DataFrame,
    harps: pd.DataFrame,
    *,
    max_sep_arcsec: float = 3.0,
) -> pd.DataFrame:
    """Crossmatch NIRPS target groups to the nearest HARPS sky position."""
    near_ir = _clean_epoch_rows(nirps)
    optical = _clean_epoch_rows(harps)
    optical_groups = list(
        optical.groupby(optical["target_name"].astype(str).str.strip(), sort=False)
    )
    rows: list[dict[str, object]] = []
    for nirps_name, nirps_group in near_ir.groupby(
        near_ir["target_name"].astype(str).str.strip(), sort=True
    ):
        nra = float(np.median(nirps_group["s_ra"]))
        ndec = float(np.median(nirps_group["s_dec"]))
        matches = []
        for harps_name, harps_group in optical_groups:
            hra = float(np.median(harps_group["s_ra"]))
            hdec = float(np.median(harps_group["s_dec"]))
            matches.append(
                (_angsep_arcsec(nra, ndec, hra, hdec), harps_name, harps_group)
            )
        best = min(matches, key=lambda item: item[0]) if matches else None
        if best is None or best[0] > max_sep_arcsec:
            rows.append(
                {
                    "nirps_target": nirps_name,
                    "harps_target": None,
                    "sep_arcsec": np.nan,
                    "n_nirps": len(nirps_group),
                    "n_harps": 0,
                    "nirps_baseline_days": float(np.ptp(nirps_group["t_min"]))
                    if len(nirps_group) > 1
                    else 0.0,
                    "harps_baseline_days": np.nan,
                    "pairs_1h": 0,
                    "pairs_6h": 0,
                    "pairs_1d": 0,
                    "pairs_3d": 0,
                    "pairs_7d": 0,
                }
            )
            continue
        separation, harps_name, harps_group = best
        counts = simultaneity_counts(
            nirps_group["t_min"].to_numpy(float),
            harps_group["t_min"].to_numpy(float),
            windows_hours=(1, 6, 24, 72, 168),
        )
        rows.append(
            {
                "nirps_target": nirps_name,
                "harps_target": harps_name,
                "sep_arcsec": separation,
                "n_nirps": len(nirps_group),
                "n_harps": len(harps_group),
                "nirps_baseline_days": float(np.ptp(nirps_group["t_min"]))
                if len(nirps_group) > 1
                else 0.0,
                "harps_baseline_days": float(np.ptp(harps_group["t_min"]))
                if len(harps_group) > 1
                else 0.0,
                "pairs_1h": counts[1.0],
                "pairs_6h": counts[6.0],
                "pairs_1d": counts[24.0],
                "pairs_3d": counts[72.0],
                "pairs_7d": counts[168.0],
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["n_nirps", "n_harps"], ascending=False
    ).reset_index(drop=True)
