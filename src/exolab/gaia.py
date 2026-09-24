"""Gaia DR3 identity and public astrometric-context helpers.

The module resolves only exact, already identified Gaia source IDs.  It does
not perform an unconstrained positional crossmatch and it does not interpret
astrometric quality fields as companion detections.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
import re
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


GAIA_DR3_IDENTIFIER = re.compile(r"^Gaia DR3 ([0-9]+)$")


@dataclass(frozen=True)
class GaiaIdentifierMatch:
    source_id: str | None
    count: int
    status: str


def extract_gaia_dr3_identifier(identifiers: str | None) -> GaiaIdentifierMatch:
    """Extract a unique Gaia DR3 source ID from a SIMBAD identifier list."""

    matches = []
    for value in str(identifiers or "").split("|"):
        match = GAIA_DR3_IDENTIFIER.fullmatch(value.strip())
        if match:
            matches.append(match.group(1))
    unique = sorted(set(matches))
    if not unique:
        return GaiaIdentifierMatch(None, 0, "unmatched")
    if len(unique) > 1:
        return GaiaIdentifierMatch(None, len(unique), "ambiguous")
    return GaiaIdentifierMatch(unique[0], 1, "unique")


class GaiaTapClient:
    """Minimal read-only client for exact-source queries against Gaia TAP."""

    endpoint = "https://gea.esac.esa.int/tap-server/tap/sync"
    columns = (
        "source_id",
        "ref_epoch",
        "ra",
        "ra_error",
        "dec",
        "dec_error",
        "parallax",
        "parallax_error",
        "pmra",
        "pmra_error",
        "pmdec",
        "pmdec_error",
        "ruwe",
        "duplicated_source",
        "phot_g_mean_mag",
        "bp_rp",
        "radial_velocity",
        "radial_velocity_error",
    )

    def __init__(self, timeout: int = 120):
        self.timeout = int(timeout)

    @classmethod
    def exact_source_query(cls, source_ids: Iterable[str | int]) -> str:
        identifiers = sorted({str(value).strip() for value in source_ids})
        if not identifiers or any(not value.isdigit() for value in identifiers):
            raise ValueError("source_ids must be a non-empty collection of digits")
        return (
            f"select {','.join(cls.columns)} from gaiadr3.gaia_source "
            f"where source_id in ({','.join(identifiers)})"
        )

    def query_source_ids(self, source_ids: Iterable[str | int]) -> tuple[pd.DataFrame, str]:
        query = self.exact_source_query(source_ids)
        url = self.endpoint + "?" + urlencode(
            {"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": query}
        )
        request = Request(
            url,
            headers={"User-Agent": "open-exoplanet-evidence-lab/0.3"},
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = response.read().decode("utf-8", errors="strict")
        frame = pd.read_csv(StringIO(payload), dtype={"source_id": "string"})
        missing = set(self.columns) - set(frame.columns)
        if missing:
            raise RuntimeError(f"Gaia TAP response is missing columns: {sorted(missing)}")
        frame["source_id"] = frame["source_id"].astype("string")
        return frame, query
