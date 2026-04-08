from __future__ import annotations

import json
from pathlib import Path

from app.domain.entities.task import Task, TaskStatus
from app.domain.repositories.task_repository import TaskRepository


class JsonTaskRepository(TaskRepository):
    def __init__(self, storage_path: Path) -> None:
        self._storage_path = storage_path
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._storage_path.exists():
            self._write([])

    def add(self, task: Task) -> Task:
        tasks = self.list_all()
        tasks.append(task)
        self._write(tasks)
        return task

    def list_all(self) -> list[Task]:
        raw_tasks = self._read()
        tasks = [self._deserialize(item) for item in raw_tasks]
        return sorted(tasks, key=lambda item: item.created_at)

    def get_by_id(self, task_id: str) -> Task | None:
        return next((task for task in self.list_all() if task.id == task_id), None)

    def update(self, task: Task) -> Task:
        tasks = self.list_all()
        updated_tasks = [
            task if existing.id == task.id else existing for existing in tasks
        ]
        self._write(updated_tasks)
        return task

    def delete(self, task_id: str) -> bool:
        tasks = self.list_all()
        filtered_tasks = [task for task in tasks if task.id != task_id]
        if len(filtered_tasks) == len(tasks):
            return False

        self._write(filtered_tasks)
        return True

    def _read(self) -> list[dict[str, str]]:
        with self._storage_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write(self, tasks: list[Task]) -> None:
        payload = [self._serialize(task) for task in tasks]
        with self._storage_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    @staticmethod
    def _serialize(task: Task) -> dict[str, str]:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

    @staticmethod
    def _deserialize(payload: dict[str, str]) -> Task:
        from datetime import datetime

        return Task(
            id=payload["id"],
            title=payload["title"],
            description=payload.get("description", ""),
            status=TaskStatus(payload["status"]),
            created_at=datetime.fromisoformat(payload["created_at"]),
            updated_at=datetime.fromisoformat(payload["updated_at"]),
        )
