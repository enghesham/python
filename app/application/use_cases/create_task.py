from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository


class CreateTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, title: str, description: str = "") -> Task:
        task = Task(title=title, description=description)
        return self._repository.add(task)
