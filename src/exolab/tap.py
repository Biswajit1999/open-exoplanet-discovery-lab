"""Small synchronous TAP client used by public archive adapters."""

from __future__ import annotations

from io import StringIO
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


class TAPClient:
    def __init__(self, endpoint: str, *, timeout: int = 120, user_agent: str = "open-exoplanet-evidence-lab/0.2"):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = int(timeout)
        self.user_agent = user_agent

    def query_csv(self, adql: str, *, maxrec: int | None = None) -> pd.DataFrame:
        params = {
            "REQUEST": "doQuery",
            "LANG": "ADQL",
            "FORMAT": "csv",
            "QUERY": " ".join(str(adql).split()),
        }
        if maxrec is not None:
            params["MAXREC"] = str(int(maxrec))
        request = Request(
            self.endpoint + "?" + urlencode(params),
            headers={"User-Agent": self.user_agent},
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = response.read().decode("utf-8", errors="replace")
        return pd.read_csv(StringIO(payload))
