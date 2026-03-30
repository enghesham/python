from __future__ import annotations

import argparse
from pathlib import Path

from app.application.exceptions import TaskManagerError
from app.application.use_cases.complete_task import CompleteTaskUseCase
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.delete_task import DeleteTaskUseCase
from app.application.use_cases.list_tasks import ListTasksUseCase
from app.application.use_cases.migrate_tasks import MigrateTasksUseCase
from app.bootstrap import build_settings, build_task_repository
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.persistence.json_task_repository import JsonTaskRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean architecture task manager")
    parser.add_argument(
        "--database",
        default="data/tasks.db",
        help="Path to the SQLite database file.",
    )
    parser.add_argument(
        "--legacy-json",
        default="data/tasks.json",
        help="Path to the legacy JSON storage file used for migration.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Create a new task.")
    add_parser.add_argument("title", help="Task title.")
    add_parser.add_argument("-d", "--description", default="", help="Task description.")

    subparsers.add_parser("list", help="List all tasks.")

    complete_parser = subparsers.add_parser("complete", help="Mark a task as done.")
    complete_parser.add_argument("task_id", help="Task identifier.")

    delete_parser = subparsers.add_parser("delete", help="Delete a task.")
    delete_parser.add_argument("task_id", help="Task identifier.")

    subparsers.add_parser("init-db", help="Initialize the SQLite database schema.")
    subparsers.add_parser(
        "migrate-json",
        help="Import tasks from the legacy JSON file into SQLite.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    settings = build_settings(
        database_path=args.database,
        legacy_json_path=args.legacy_json,
    )
    repository = build_task_repository(settings.database_path)

    handlers = {
        "add": lambda: _handle_add(repository, args.title, args.description),
        "list": lambda: _handle_list(repository),
        "complete": lambda: _handle_complete(repository, args.task_id),
        "delete": lambda: _handle_delete(repository, args.task_id),
        "init-db": lambda: _handle_init_db(settings.database_path),
        "migrate-json": lambda: _handle_migrate_json(
            repository,
            settings.legacy_json_path,
        ),
    }

    try:
        handlers[args.command]()
    except (TaskManagerError, ValueError) as error:
        parser.exit(status=1, message=f"Error: {error}\n")
    finally:
        _close_repository(repository)

    return 0


def _handle_add(repository: TaskRepository, title: str, description: str) -> None:
    task = CreateTaskUseCase(repository).execute(title=title, description=description)
    print(f"Created task {task.id}: {task.title}")


def _handle_list(repository: TaskRepository) -> None:
    tasks = ListTasksUseCase(repository).execute()
    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        print(f"[{task.status.value}] {task.id} | {task.title} | {task.description}")


def _handle_complete(repository: TaskRepository, task_id: str) -> None:
    task = CompleteTaskUseCase(repository).execute(task_id)
    print(f"Completed task {task.id}: {task.title}")


def _handle_delete(repository: TaskRepository, task_id: str) -> None:
    DeleteTaskUseCase(repository).execute(task_id)
    print(f"Deleted task {task_id}")


def _handle_init_db(database_path: Path) -> None:
    build_task_repository(database_path)
    print(f"Database initialized at {database_path}")


def _handle_migrate_json(repository: TaskRepository, legacy_json_path: Path) -> None:
    if not legacy_json_path.exists():
        raise ValueError(f"Legacy JSON file was not found: {legacy_json_path}")

    migrated = MigrateTasksUseCase(
        JsonTaskRepository(legacy_json_path),
        repository,
    ).execute()
    print(f"Migrated {migrated} task(s) into the database.")


def _close_repository(repository: TaskRepository) -> None:
    close = getattr(repository, "close", None)
    if callable(close):
        close()
