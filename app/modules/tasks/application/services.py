from app.modules.tasks.application.exceptions import TaskNotFoundError
from app.modules.tasks.application.schemas import TaskCreateSchema, TaskUpdateSchema
from app.modules.tasks.infrastructure.models import TaskModel
from app.modules.tasks.infrastructure.repositories import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, payload: TaskCreateSchema) -> TaskModel:
        return self.repository.create(
            title=payload.title,
            description=payload.description,
        )

    def list_tasks(self) -> list[TaskModel]:
        return self.repository.get_all()

    def get_task(self, task_id: str) -> TaskModel:
        task = self.repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    def update_task(self, task_id: str, payload: TaskUpdateSchema) -> TaskModel:
        task = self.repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)

        update_data = payload.model_dump(exclude_unset=True)
        return self.repository.update(task, update_data)

    def delete_task(self, task_id: str) -> None:
        task = self.repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)

        self.repository.delete(task)