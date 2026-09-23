"""Machine-readable result envelopes shared by analysis and the web layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping


RESULT_STATES = {"measured", "derived", "fitted", "simulated", "literature", "provisional"}


@dataclass(frozen=True)
class ResultEnvelope:
    result_id: str
    work_package: str
    state: str
    target_id: str | None
    manifest_hash: str
    analysis_commit: str
    values: Mapping[str, Any]
    units: Mapping[str, str] = field(default_factory=dict)
    caveats: tuple[str, ...] = ()
    generated_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if self.state not in RESULT_STATES:
            raise ValueError(f"Unknown result state {self.state!r}")
        if not self.result_id or not self.work_package:
            raise ValueError("result_id and work_package are required")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_result(result: ResultEnvelope, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output
