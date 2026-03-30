from __future__ import annotations

from pathlib import Path

from app.config import AppSettings
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.database.sqlite import SqliteDatabase
from app.infrastructure.persistence.sqlite_task_repository import SqliteTaskRepository


def build_settings(
    database_path: str | Path | None = None,
    legacy_json_path: str | Path | None = None,
) -> AppSettings:
    settings = AppSettings()

    if database_path is not None:
        settings = AppSettings(
            database_path=Path(database_path),
            legacy_json_path=settings.legacy_json_path,
        )

    if legacy_json_path is not None:
        settings = AppSettings(
            database_path=settings.database_path,
            legacy_json_path=Path(legacy_json_path),
        )

    return settings


def build_task_repository(
    database_path: str | Path | None = None,
) -> TaskRepository:
    settings = build_settings(database_path=database_path)
    database = SqliteDatabase(settings.database_path)
    return SqliteTaskRepository(database)
