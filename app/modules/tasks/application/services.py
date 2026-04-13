from app.modules.tasks.application.schemas import TaskCreateSchema, TaskUpdateSchema
from app.modules.tasks.infrastructure.repositories import TaskRepository
from app.modules.tasks.infrastructure.models import TaskModel


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

    def get_task(self, task_id: str) -> TaskModel | None:
        return self.repository.get_by_id(task_id)

    def update_task(self, task_id: str, payload: TaskUpdateSchema) -> TaskModel | None:
        task = self.repository.get_by_id(task_id)
        if not task:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        return self.repository.update(task, update_data)

    def delete_task(self, task_id: str) -> bool:
        task = self.repository.get_by_id(task_id)
        if not task:
            return False

        self.repository.delete(task)
        return True