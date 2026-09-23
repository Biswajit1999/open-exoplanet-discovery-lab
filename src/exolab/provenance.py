"""Provenance primitives for reproducible archive-based exoplanet research.

The functions in this module are deliberately small and dependency-free so they
can be used by every work package before specialist science libraries are
installed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


ALLOWED_SOURCE_STATES = {"ready", "census", "active", "wait", "future"}


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 digest of a local file without loading it all at once."""
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    """Serialise JSON deterministically for hashing and release comparisons."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_json_sha256(value: Any) -> str:
    """Return a stable SHA-256 digest for JSON-compatible data."""
    return sha256(canonical_json_bytes(value)).hexdigest()


@dataclass(frozen=True)
class FileRecord:
    """Lineage for one local file acquired from a public archive."""

    path: str
    sha256: str
    size_bytes: int
    source_product_id: str | None = None
    source_url: str | None = None
    pipeline_version: str | None = None

    @classmethod
    def from_path(
        cls,
        path: str | Path,
        *,
        source_product_id: str | None = None,
        source_url: str | None = None,
        pipeline_version: str | None = None,
    ) -> "FileRecord":
        p = Path(path)
        return cls(
            path=str(p),
            sha256=sha256_file(p),
            size_bytes=p.stat().st_size,
            source_product_id=source_product_id,
            source_url=source_url,
            pipeline_version=pipeline_version,
        )


@dataclass(frozen=True)
class DatasetRecord:
    """Frozen description of one archive acquisition event."""

    source_id: str
    source_state: str
    archive: str
    query: str
    access_time_utc: str
    product_ids: tuple[str, ...] = ()
    files: tuple[FileRecord, ...] = ()
    selection_rules: Mapping[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.source_state not in ALLOWED_SOURCE_STATES:
            raise ValueError(
                f"Unknown source_state={self.source_state!r}; "
                f"expected one of {sorted(ALLOWED_SOURCE_STATES)}"
            )
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")
        if not self.archive.strip():
            raise ValueError("archive must not be empty")

    @classmethod
    def create(
        cls,
        *,
        source_id: str,
        source_state: str,
        archive: str,
        query: str,
        product_ids: Iterable[str] = (),
        files: Iterable[FileRecord] = (),
        selection_rules: Mapping[str, Any] | None = None,
        notes: Iterable[str] = (),
        access_time: datetime | None = None,
    ) -> "DatasetRecord":
        when = access_time or datetime.now(timezone.utc)
        if when.tzinfo is None:
            raise ValueError("access_time must be timezone-aware")
        return cls(
            source_id=source_id,
            source_state=source_state,
            archive=archive,
            query=query,
            access_time_utc=when.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            product_ids=tuple(product_ids),
            files=tuple(files),
            selection_rules=dict(selection_rules or {}),
            notes=tuple(notes),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def manifest_hash(self) -> str:
        """Stable digest that changes when any recorded provenance changes."""
        return canonical_json_sha256(self.to_dict())


def write_manifest(record: DatasetRecord, path: str | Path) -> Path:
    """Write a human-readable manifest while preserving deterministic content."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = record.to_dict()
    payload["manifest_hash"] = record.manifest_hash
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output


def verify_manifest(path: str | Path) -> bool:
    """Verify both the stored manifest hash and any local file checksums.

    Missing local files make verification fail. This is intentional: the caller
    should reacquire archive products rather than silently treating a missing
    input as valid.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    stored_hash = payload.pop("manifest_hash", None)
    if stored_hash is None:
        return False
    if canonical_json_sha256(payload) != stored_hash:
        return False

    for file_info in payload.get("files", []):
        local_path = Path(file_info["path"])
        if not local_path.exists():
            return False
        if sha256_file(local_path) != file_info["sha256"]:
            return False
    return True
