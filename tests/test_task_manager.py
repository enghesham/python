from __future__ import annotations

import os
import unittest
from pathlib import Path
from uuid import uuid4

from app.application.exceptions import TaskNotFoundError
from app.application.use_cases.complete_task import CompleteTaskUseCase
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.delete_task import DeleteTaskUseCase
from app.application.use_cases.list_tasks import ListTasksUseCase
from app.application.use_cases.migrate_tasks import MigrateTasksUseCase
from app.bootstrap import build_settings
from app.config import AppSettings
from app.infrastructure.database.sqlite import SqliteDatabase
from app.infrastructure.persistence.json_task_repository import JsonTaskRepository
from app.infrastructure.persistence.sqlite_task_repository import SqliteTaskRepository
from app.presentation.cli import main


class TaskManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(__file__).resolve().parent / ".tmp" / uuid4().hex
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.database_path = self.temp_dir / "tasks.db"
        self.legacy_json_path = self.temp_dir / "tasks.json"
        self.database = SqliteDatabase(self.database_path)
        self.repository = SqliteTaskRepository(self.database)

    def tearDown(self) -> None:
        self.repository.close()
        if self.database_path.exists():
            self.database_path.unlink()
        if self.legacy_json_path.exists():
            self.legacy_json_path.unlink()
        self.temp_dir.rmdir()

    def test_create_and_list_tasks(self) -> None:
        CreateTaskUseCase(self.repository).execute("Write docs", "Document the CLI")

        tasks = ListTasksUseCase(self.repository).execute()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Write docs")

    def test_complete_task(self) -> None:
        task = CreateTaskUseCase(self.repository).execute("Ship release")

        updated = CompleteTaskUseCase(self.repository).execute(task.id)

        self.assertEqual(updated.status.value, "done")

    def test_delete_task(self) -> None:
        task = CreateTaskUseCase(self.repository).execute("Remove me")

        DeleteTaskUseCase(self.repository).execute(task.id)

        self.assertEqual(ListTasksUseCase(self.repository).execute(), [])

    def test_delete_missing_task_raises_error(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            DeleteTaskUseCase(self.repository).execute("missing")

    def test_cli_add_command_persists_task_in_database(self) -> None:
        exit_code = main(
            [
                "--database",
                str(self.database_path),
                "add",
                "Test from CLI",
                "--description",
                "cli flow",
            ]
        )

        tasks = self.repository.list_all()

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Test from CLI")

    def test_json_tasks_can_be_migrated_to_sqlite(self) -> None:
        source_repository = JsonTaskRepository(self.legacy_json_path)
        legacy_task = CreateTaskUseCase(source_repository).execute("Legacy task")

        migrated_count = MigrateTasksUseCase(
            source_repository,
            self.repository,
        ).execute()

        migrated_task = self.repository.get_by_id(legacy_task.id)

        self.assertEqual(migrated_count, 1)
        self.assertIsNotNone(migrated_task)
        self.assertEqual(migrated_task.title, "Legacy task")

    def test_build_settings_can_switch_to_postgresql(self) -> None:
        settings = build_settings(
            backend="postgresql",
            postgres_dsn="postgresql+psycopg://user:pass@localhost:5432/app_db",
        )

        self.assertEqual(settings.backend, "postgresql")
        self.assertEqual(
            settings.postgres_dsn,
            "postgresql+psycopg://user:pass@localhost:5432/app_db",
        )

    def test_app_settings_can_read_runtime_environment(self) -> None:
        previous_env = {
            "APP_BACKEND": os.environ.get("APP_BACKEND"),
            "SQLITE_DATABASE_PATH": os.environ.get("SQLITE_DATABASE_PATH"),
            "POSTGRES_DSN": os.environ.get("POSTGRES_DSN"),
            "LEGACY_JSON_PATH": os.environ.get("LEGACY_JSON_PATH"),
            "APP_ENV": os.environ.get("APP_ENV"),
            "APP_DEBUG": os.environ.get("APP_DEBUG"),
        }

        os.environ["APP_BACKEND"] = "postgresql"
        os.environ["SQLITE_DATABASE_PATH"] = "data/custom.db"
        os.environ["POSTGRES_DSN"] = (
            "postgresql+psycopg://env:env@localhost:5432/env_db"
        )
        os.environ["LEGACY_JSON_PATH"] = "data/custom.json"
        os.environ["APP_ENV"] = "testing"
        os.environ["APP_DEBUG"] = "false"

        settings = AppSettings()

        self.assertEqual(settings.backend, "postgresql")
        self.assertEqual(settings.database_path, Path("data/custom.db"))
        self.assertEqual(
            settings.postgres_dsn,
            "postgresql+psycopg://env:env@localhost:5432/env_db",
        )
        self.assertEqual(settings.legacy_json_path, Path("data/custom.json"))
        self.assertEqual(settings.app_env, "testing")
        self.assertFalse(settings.app_debug)

        for key, value in previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
