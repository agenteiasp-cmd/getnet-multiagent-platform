import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class ManifestEntry:
    url: str
    topic: str
    ingested_at: str
    chunk_count: int


def write_manifest(entries: list[ManifestEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(entry) for entry in entries], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def read_manifest(path: Path) -> list[ManifestEntry]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [ManifestEntry(**item) for item in raw]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
