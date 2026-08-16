"""Small, explicit clients for public exoplanet archive tables."""

from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


@dataclass(frozen=True)
class ArchiveSnapshot:
    confirmed_planets: int
    toi_rows: int
    dispositions: dict[str, int]


class ExoplanetArchiveClient:
    """Query NASA Exoplanet Archive TAP using auditable ADQL strings."""

    endpoint = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

    def __init__(self, timeout: int = 60) -> None:
        self.timeout = timeout

    def query(self, adql: str) -> pd.DataFrame:
        params = urlencode({"query": adql, "format": "csv"})
        request = Request(
            f"{self.endpoint}?{params}",
            headers={"User-Agent": "open-exoplanet-discovery-lab/0.1"},
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = response.read().decode("utf-8")
        return pd.read_csv(StringIO(payload))

    def census(self) -> ArchiveSnapshot:
        confirmed = int(self.query("select count(*) as n from pscomppars").iloc[0]["n"])
        tois = int(self.query("select count(*) as n from toi").iloc[0]["n"])
        disposition_rows = self.query(
            "select tfopwg_disp,count(*) as n from toi group by tfopwg_disp"
        )
        dispositions = {
            ("unclassified" if pd.isna(row.tfopwg_disp) else str(row.tfopwg_disp)): int(row.n)
            for row in disposition_rows.itertuples(index=False)
        }
        return ArchiveSnapshot(confirmed, tois, dispositions)

    def candidate_queue(
        self,
        limit: int = 50,
        max_tmag: float = 12.0,
        max_radius: float = 6.0,
        min_period: float = 0.5,
        max_period: float = 40.0,
    ) -> pd.DataFrame:
        """Return current planet-candidate TOIs, then rank transparent search value.

        This is a target-selection queue, not a novelty or validation claim.
        """

        if not 1 <= limit <= 5000:
            raise ValueError("limit must be between 1 and 5000")
        numeric = [max_tmag, max_radius, min_period, max_period]
        if not all(pd.notna(value) for value in numeric) or min_period >= max_period:
            raise ValueError("candidate bounds must be finite and min_period < max_period")

        adql = f"""
            select top {int(limit * 5)}
                tid,toi,toidisplay,tfopwg_disp,st_tmag,ra,dec,
                pl_orbper,pl_trandurh,pl_trandep,pl_rade,pl_eqt,
                st_rad,st_teff,sectors,rowupdate
            from toi
            where tfopwg_disp='PC'
              and st_tmag <= {float(max_tmag)}
              and pl_rade <= {float(max_radius)}
              and pl_orbper between {float(min_period)} and {float(max_period)}
              and pl_trandep is not null
              and pl_trandurh is not null
        """
        frame = self.query(" ".join(adql.split()))
        if frame.empty:
            return frame

        # Bright, small candidates are accessible; multiple sectors improve
        # repeatability. This score prioritizes work but is not a planet score.
        sector_count = frame["sectors"].fillna("").astype(str).map(
            lambda value: len([part for part in value.split(",") if part.strip()])
        )
        depth = frame["pl_trandep"].clip(lower=1.0)
        frame["selection_score"] = (
            (13.5 - frame["st_tmag"]).clip(lower=0)
            + 1.5 / frame["pl_rade"].clip(lower=0.3)
            + 0.35 * sector_count.clip(upper=10)
            + 0.15 * depth.map(lambda value: min(6.0, max(0.0, value) ** 0.25))
        )
        frame["sector_count"] = sector_count
        return frame.sort_values(
            ["selection_score", "st_tmag"], ascending=[False, True]
        ).head(limit).reset_index(drop=True)

    def confirmed_planet(self, planet_name: str) -> pd.DataFrame:
        safe_name = planet_name.replace("'", "''")
        columns = (
            "pl_name,hostname,ra,dec,pl_orbper,pl_tranmid,pl_trandur,"
            "pl_rade,pl_bmasse,pl_eqt,pl_orbsmax,sy_dist,sy_tmag,"
            "st_teff,st_rad,st_mass,disc_year,discoverymethod"
        )
        return self.query(
            f"select {columns} from pscomppars where pl_name='{safe_name}'"
        )
