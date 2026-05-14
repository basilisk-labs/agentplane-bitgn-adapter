from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class ProofRecorder:
    artifact_dir: Path
    run: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def start(self, metadata: dict[str, Any]) -> None:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.run = {"started_at": utc_now(), **metadata}
        self.flush()

    def record(self, event: str, **payload: Any) -> None:
        self.events.append({"ts": utc_now(), "event": event, **payload})
        self.flush()

    def finish(self, **payload: Any) -> None:
        self.run.update({"finished_at": utc_now(), **payload})
        self.flush()

    def flush(self) -> None:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        data = {"run": self.run, "events": self.events}
        (self.artifact_dir / "proof.json").write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
