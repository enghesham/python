from app.core.exceptions import NotFoundError

class TaskNotFoundError(NotFoundError):
    def __init__(self, task_id: str):
        super().__init__(f"Task with id '{task_id}' was not found")