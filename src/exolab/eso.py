"""Minimal, auditable ESO TAP client and ObsCore query builders."""

from __future__ import annotations

from io import BytesIO
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
from astropy.io.votable import parse_single_table


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
