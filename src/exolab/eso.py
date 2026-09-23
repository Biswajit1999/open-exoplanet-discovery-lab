"""Minimal, auditable ESO TAP client and archive-query builders."""

from __future__ import annotations

from io import StringIO
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


class ESOArchiveClient:
    endpoint = "https://archive.eso.org/tap_obs/sync"

    def __init__(self, timeout: int = 120) -> None:
        self.timeout = int(timeout)

    def query(self, adql: str, *, maxrec: int | None = None) -> pd.DataFrame:
        params = {
            "REQUEST": "doQuery",
            "LANG": "ADQL",
            "FORMAT": "csv",
            "QUERY": " ".join(adql.split()),
        }
        if maxrec is not None:
            params["MAXREC"] = str(int(maxrec))
        request = Request(
            f"{self.endpoint}?{urlencode(params)}",
            headers={"User-Agent": "open-exoplanet-evidence-lab/0.3"},
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = response.read().decode("utf-8")
        return pd.read_csv(StringIO(payload))


def instrument_inventory_query(instrument_name: str) -> str:
    safe = instrument_name.replace("'", "''")
    return f"""
        SELECT
            target_name, s_ra, s_dec, t_min, t_max, t_exptime,
            dp_id, obs_id, obs_collection, instrument_name,
            dataproduct_type, dataproduct_subtype, calib_level,
            access_url, access_estsize, snr, publication_date
        FROM ivoa.ObsCore
        WHERE instrument_name = '{safe}'
          AND data_rights = 'public'
    """


def target_instrument_query(
    instrument_name: str,
    *,
    ra_deg: float,
    dec_deg: float,
    radius_deg: float = 5.0 / 3600.0,
) -> str:
    safe = instrument_name.replace("'", "''")
    return f"""
        SELECT
            target_name, s_ra, s_dec, t_min, t_max, t_exptime,
            dp_id, obs_id, obs_collection, instrument_name,
            dataproduct_type, dataproduct_subtype, calib_level,
            access_url, access_estsize, snr, publication_date
        FROM ivoa.ObsCore
        WHERE instrument_name = '{safe}'
          AND data_rights = 'public'
          AND 1 = CONTAINS(
              POINT('ICRS', s_ra, s_dec),
              CIRCLE('ICRS', {float(ra_deg)}, {float(dec_deg)}, {float(radius_deg)})
          )
    """
