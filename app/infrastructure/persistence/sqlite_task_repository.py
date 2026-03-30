from __future__ import annotations

from datetime import datetime
from sqlite3 import Row

from app.domain.entities.task import Task, TaskStatus
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.database.sqlite import SqliteDatabase


class SqliteTaskRepository(TaskRepository):
    def __init__(self, database: SqliteDatabase) -> None:
        self._database = database

    def add(self, task: Task) -> Task:
        with self._database.connection() as connection:
            connection.execute(
                """
                INSERT INTO tasks (
                    id,
                    title,
                    description,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.title,
                    task.description,
                    task.status.value,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                ),
            )

        return task

    def list_all(self) -> list[Task]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """
                SELECT id, title, description, status, created_at, updated_at
                FROM tasks
                ORDER BY created_at ASC
                """
            ).fetchall()

        return [self._map_row(row) for row in rows]

    def get_by_id(self, task_id: str) -> Task | None:
        with self._database.connection() as connection:
            row = connection.execute(
                """
                SELECT id, title, description, status, created_at, updated_at
                FROM tasks
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def update(self, task: Task) -> Task:
        with self._database.connection() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, status = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    task.title,
                    task.description,
                    task.status.value,
                    task.updated_at.isoformat(),
                    task.id,
                ),
            )

        return task

    def delete(self, task_id: str) -> bool:
        with self._database.connection() as connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,),
            )

        return cursor.rowcount > 0

    @staticmethod
    def _map_row(row: Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=TaskStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
