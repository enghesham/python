from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_POSTGRES_DSN = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/task_manager"
)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value

    return values


def load_env_files(project_root: Path | None = None) -> None:
    root = project_root or _project_root()
    base_values = _parse_env_file(root / ".env")
    app_env = os.environ.get("APP_ENV") or base_values.get("APP_ENV", "development")
    scoped_values = _parse_env_file(root / f".env.{app_env}")

    merged_values = {**base_values, **scoped_values}
    for key, value in merged_values.items():
        if key not in os.environ:
            os.environ[key] = value


load_env_files()


@dataclass(frozen=True, slots=True)
class AppSettings:
    backend: str = field(default_factory=lambda: os.getenv("APP_BACKEND", "sqlite"))
    database_path: Path = field(
        default_factory=lambda: Path(
            os.getenv("SQLITE_DATABASE_PATH", "data/tasks.db")
        )
    )
    postgres_dsn: str = field(
        default_factory=lambda: os.getenv("POSTGRES_DSN", DEFAULT_POSTGRES_DSN)
    )
    legacy_json_path: Path = field(
        default_factory=lambda: Path(os.getenv("LEGACY_JSON_PATH", "data/tasks.json"))
    )
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    app_debug: bool = field(
        default_factory=lambda: os.getenv("APP_DEBUG", "true").lower() == "true"
    )
