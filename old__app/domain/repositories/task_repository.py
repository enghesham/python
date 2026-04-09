from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.task import Task


class TaskRepository(ABC):
    @abstractmethod
    def add(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Task]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, task_id: str) -> Task | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def delete(self, task_id: str) -> bool:
        raise NotImplementedError
