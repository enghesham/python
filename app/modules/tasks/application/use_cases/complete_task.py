from app.application.exceptions import TaskNotFoundError
from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository


class CompleteTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, task_id: str) -> Task:
        task = self._repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task '{task_id}' was not found.")

        task.mark_done()
        return self._repository.update(task)
