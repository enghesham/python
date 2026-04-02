from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppSettings:
    backend: str = "sqlite"
    database_path: Path = Path("data/tasks.db")
    postgres_dsn: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/task_manager"
    )
    legacy_json_path: Path = Path("data/tasks.json")
