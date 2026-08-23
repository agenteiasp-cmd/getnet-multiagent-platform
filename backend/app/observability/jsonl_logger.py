import json
from dataclasses import asdict
from pathlib import Path

from app.observability.models import StepRecord


class JsonlLogger:
    """Append-only JSONL log of every step record - the human-diffable
    source of truth. SQLite (store.py) is a derived index built from the
    same records, kept in sync by ObservabilityRecorder."""

    def __init__(self, path: Path):
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: StepRecord) -> None:
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False, default=str) + "\n")

    def read_all(self) -> list[dict]:
        if not self._path.exists():
            return []
        with self._path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
