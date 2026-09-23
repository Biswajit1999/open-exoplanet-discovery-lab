"""Versioned source-registry helpers and access-state gates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_ALLOWED = {"ready", "census", "active", "wait", "future"}


@dataclass(frozen=True)
class SourceSpec:
    id: str
    name: str
    status: str
    payload: dict[str, Any]

    @property
    def usable_now(self) -> bool:
        return self.status in {"ready", "census", "active"}

    def require_public(self) -> None:
        if not self.usable_now:
            raise RuntimeError(
                f"{self.name} is registered as {self.status!r}; "
                "the project will not treat it as a current public science input."
            )


def load_registry(path: str | Path = "configs/data_sources.json") -> dict[str, SourceSpec]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    sources: dict[str, SourceSpec] = {}
    for row in payload.get("sources", []):
        status = str(row["status"])
        if status not in _ALLOWED:
            raise ValueError(f"Unknown source status {status!r}")
        spec = SourceSpec(
            id=str(row["id"]),
            name=str(row["name"]),
            status=status,
            payload=dict(row),
        )
        if spec.id in sources:
            raise ValueError(f"Duplicate source id {spec.id!r}")
        sources[spec.id] = spec
    return sources


def require_source(source_id: str, path: str | Path = "configs/data_sources.json") -> SourceSpec:
    registry = load_registry(path)
    try:
        source = registry[source_id]
    except KeyError as exc:
        raise KeyError(f"Unknown source id {source_id!r}") from exc
    source.require_public()
    return source
