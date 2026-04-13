from sqlalchemy.orm import Session

from app.modules.tasks.infrastructure.models import TaskModel


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, description: str | None = None) -> TaskModel:
        task = TaskModel(
            title=title,
            description=description,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_all(self) -> list[TaskModel]:
        return self.db.query(TaskModel).order_by(TaskModel.created_at.desc()).all()

    def get_by_id(self, task_id: str) -> TaskModel | None:
        return self.db.query(TaskModel).filter(TaskModel.id == task_id).first()

    def update(self, task: TaskModel, data: dict) -> TaskModel:
        for key, value in data.items():
            setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: TaskModel) -> None:
        self.db.delete(task)
        self.db.commit()