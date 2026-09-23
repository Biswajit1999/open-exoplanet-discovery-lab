"""Minimal VizieR ASU-TSV client for frozen catalogue acquisition."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


class VizierClient:
    mirrors = (
        "https://vizier.cds.unistra.fr/viz-bin/asu-tsv",
        "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv",
    )

    def __init__(self, timeout: int = 120):
        self.timeout = int(timeout)

    def table(self, source: str, *, all_columns: bool = True) -> pd.DataFrame:
        params = {"-source": source, "-out.max": "unlimited"}
        if all_columns:
            params["-out.all"] = "1"
        last_error = None
        for endpoint in self.mirrors:
            try:
                request = Request(
                    endpoint + "?" + urlencode(params),
                    headers={"User-Agent": "open-exoplanet-evidence-lab/0.2"},
                )
                with urlopen(request, timeout=self.timeout) as response:
                    text = response.read().decode("utf-8", errors="replace")
                return pd.read_csv(StringIO(text), sep="\t", comment="#", na_values=["", "--"])
            except Exception as exc:  # mirrors are an operational fallback
                last_error = exc
        raise RuntimeError(f"All VizieR mirrors failed for {source}: {last_error}")

    def save_table(self, source: str, path: str | Path) -> Path:
        frame = self.table(source)
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output, index=False)
        return output
