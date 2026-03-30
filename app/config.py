from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppSettings:
    database_path: Path = Path("data/tasks.db")
    legacy_json_path: Path = Path("data/tasks.json")
