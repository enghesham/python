from app.application.exceptions import TaskNotFoundError
from app.domain.repositories.task_repository import TaskRepository


class DeleteTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, task_id: str) -> None:
        deleted = self._repository.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(f"Task '{task_id}' was not found.")
