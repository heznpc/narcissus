"""Atomic JSON checkpoint store for resumable experiments.

Idempotent by design: each cell is keyed by a string; mark_done is safe to
call repeatedly. Writes are atomic (write-to-tmp + os.replace).
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class Checkpoint:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._state: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"completed": [], "failed": [], "meta": {}}
        try:
            with self.path.open(encoding="utf-8") as f:
                state = json.load(f)
        except json.JSONDecodeError:
            # Corrupt file: back up, start fresh
            backup = self.path.with_suffix(self.path.suffix + ".corrupt")
            self.path.replace(backup)
            return {"completed": [], "failed": [], "meta": {}}
        state.setdefault("completed", [])
        state.setdefault("failed", [])
        state.setdefault("meta", {})
        return state

    def is_done(self, key: str) -> bool:
        return key in self._state["completed"]

    def mark_done(self, key: str, payload: dict[str, Any] | None = None) -> None:
        if key not in self._state["completed"]:
            self._state["completed"].append(key)
        if payload is not None:
            self._state["meta"][key] = payload
        # Clear any previous failure record for this key.
        self._state["failed"] = [f for f in self._state["failed"] if f.get("key") != key]
        self._save()

    def mark_failed(self, key: str, reason: str) -> None:
        # Append-only failure log; keeps history of attempts.
        self._state["failed"].append({"key": key, "reason": reason})
        self._save()

    def _save(self) -> None:
        # Atomic: write to tmp in the same directory, then os.replace.
        fd, tmp_path = tempfile.mkstemp(
            prefix=self.path.name + ".", suffix=".tmp", dir=self.path.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2, sort_keys=True, ensure_ascii=False)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.path)
        except BaseException:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    @property
    def completed_count(self) -> int:
        return len(self._state["completed"])

    @property
    def failed(self) -> list[dict[str, Any]]:
        return list(self._state["failed"])
