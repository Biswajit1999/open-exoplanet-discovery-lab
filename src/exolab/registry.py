"""Data-source registry and release-state gates."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


VALID_STATES = {"ready", "census", "active", "wait", "future"}


@dataclass(frozen=True)
class DataSource:
    source_id: str
    name: str
    status: str
    archive: str | None
    payload: dict[str, Any]

    @property
    def immediately_usable(self) -> bool:
        return self.status in {"ready", "census", "active"}

    @property
    def id(self) -> str:
        return self.source_id

    @property
    def usable_now(self) -> bool:
        return self.immediately_usable

    def require_public(self) -> None:
        if not self.immediately_usable:
            raise RuntimeError(
                f"{self.name} is registered as {self.status!r}; the project will "
                "not treat it as a current public science input."
            )


SourceSpec = DataSource


def default_registry_path() -> Path:
    return Path(__file__).resolve().parents[2] / "configs" / "data_sources.json"


def load_registry(path: str | Path | None = None) -> dict[str, DataSource]:
    registry_path = Path(path) if path is not None else default_registry_path()
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    result: dict[str, DataSource] = {}
    for item in payload.get("sources", []):
        state = str(item["status"]).lower()
        if state not in VALID_STATES:
            raise ValueError(f"Unknown data-source state {state!r}")
        source_id = str(item["id"])
        if source_id in result:
            raise ValueError(f"Duplicate source id {source_id!r}")
        result[source_id] = DataSource(
            source_id=source_id,
            name=str(item["name"]),
            status=state,
            archive=item.get("archive"),
            payload=dict(item),
        )
    return result


def require_source(
    source_id: str,
    path: str | Path | None = None,
    *,
    allow_active: bool = True,
    allow_census: bool = True,
) -> DataSource:
    sources = load_registry(path)
    if source_id not in sources:
        raise KeyError(f"Unknown source {source_id!r}")
    source = sources[source_id]
    allowed = {"ready"}
    if allow_active:
        allowed.add("active")
    if allow_census:
        allowed.add("census")
    if source.status not in allowed:
        raise RuntimeError(
            f"Source {source_id!r} is gated with status={source.status!r}; "
            "the archive state must be verified before analysis."
        )
    return source
