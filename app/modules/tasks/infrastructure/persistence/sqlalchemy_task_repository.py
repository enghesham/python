from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.domain.entities.task import Task, TaskStatus
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.database.models import TaskModel
from app.infrastructure.database.sqlalchemy import SqlAlchemyDatabase


class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, database: SqlAlchemyDatabase) -> None:
        self._database = database

    def close(self) -> None:
        self._database.close()

    def add(self, task: Task) -> Task:
        with self._database.session() as session:
            session.add(self._to_model(task))

        return task

    def list_all(self) -> list[Task]:
        with self._database.session() as session:
            rows = session.scalars(
                select(TaskModel).order_by(TaskModel.created_at.asc())
            ).all()

        return [self._to_entity(row) for row in rows]

    def get_by_id(self, task_id: str) -> Task | None:
        with self._database.session() as session:
            row = session.get(TaskModel, task_id)

        if row is None:
            return None

        return self._to_entity(row)

    def update(self, task: Task) -> Task:
        with self._database.session() as session:
            row = session.get(TaskModel, task.id)
            if row is None:
                return task

            row.title = task.title
            row.description = task.description
            row.status = task.status.value
            row.updated_at = task.updated_at

        return task

    def delete(self, task_id: str) -> bool:
        with self._database.session() as session:
            row = session.get(TaskModel, task_id)
            if row is None:
                return False

            session.delete(row)

        return True

    @staticmethod
    def _to_model(task: Task) -> TaskModel:
        return TaskModel(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    @staticmethod
    def _to_entity(model: TaskModel) -> Task:
        created_at = model.created_at
        updated_at = model.updated_at

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            status=TaskStatus(model.status),
            created_at=created_at,
            updated_at=updated_at,
        )
