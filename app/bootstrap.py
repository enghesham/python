from __future__ import annotations

from pathlib import Path

from app.config import AppSettings
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.database.postgresql import PostgreSqlDatabase
from app.infrastructure.database.sqlite import SqliteDatabase
from app.infrastructure.persistence.postgresql_task_repository import (
    PostgreSqlTaskRepository,
)
from app.infrastructure.persistence.sqlite_task_repository import SqliteTaskRepository


def build_settings(
    backend: str | None = None,
    database_path: str | Path | None = None,
    postgres_dsn: str | None = None,
    legacy_json_path: str | Path | None = None,
) -> AppSettings:
    settings = AppSettings()

    return AppSettings(
        backend=backend or settings.backend,
        database_path=(
            Path(database_path)
            if database_path is not None
            else settings.database_path
        ),
        postgres_dsn=postgres_dsn or settings.postgres_dsn,
        legacy_json_path=Path(legacy_json_path)
        if legacy_json_path is not None
        else settings.legacy_json_path,
    )


def build_task_repository(
    settings: AppSettings | None = None,
    backend: str | None = None,
    database_path: str | Path | None = None,
    postgres_dsn: str | None = None,
) -> TaskRepository:
    app_settings = settings or build_settings(
        backend=backend,
        database_path=database_path,
        postgres_dsn=postgres_dsn,
    )

    if app_settings.backend == "sqlite":
        database = SqliteDatabase(app_settings.database_path)
        return SqliteTaskRepository(database)

    if app_settings.backend == "postgresql":
        database = PostgreSqlDatabase(app_settings.postgres_dsn)
        return PostgreSqlTaskRepository(database)

    raise ValueError(f"Unsupported backend: {app_settings.backend}")
