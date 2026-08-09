"""Append-only JSONL storage and task-level resume support."""

from __future__ import annotations

import hashlib
import json
import os
import threading
from pathlib import Path
from typing import Any, Iterable


def make_task_key(
    *,
    model: str,
    country: str,
    scenario_id: str,
    prompt_language: str,
    repeat_id: int,
    scenario_version: str | None = None,
    prompt_template_version: str | None = None,
    prompt_fingerprint: str | None = None,
) -> str:
    """Create a stable key for one reproducible generation task.

    The optional version and fingerprint fields preserve compatibility with
    legacy Phase 1 callers while preventing a changed scenario or prompt from
    being mistaken for an already-completed task in new runs.
    """
    identity = {
        "model": model,
        "country": country,
        "scenario_id": scenario_id,
        "prompt_language": prompt_language,
        "repeat_id": repeat_id,
        "scenario_version": scenario_version,
        "prompt_template_version": prompt_template_version,
        "prompt_fingerprint": prompt_fingerprint,
    }
    encoded = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class JSONLStore:
    """Minimal durable store: one flushed and fsynced JSON object per line."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at {self.path}:{line_number}") from exc
                if not isinstance(record, dict):
                    raise ValueError(f"JSONL record at {self.path}:{line_number} is not an object")
                records.append(record)
        return records

    def completed_task_keys(self) -> set[str]:
        return {
            str(record["task_key"])
            for record in self.read_all()
            if record.get("status") == "success" and record.get("task_key")
        }

    def append(self, record: dict[str, Any]) -> None:
        serialized = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            with self.path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(serialized + "\n")
                handle.flush()
                os.fsync(handle.fileno())

    def __iter__(self) -> Iterable[dict[str, Any]]:
        return iter(self.read_all())
