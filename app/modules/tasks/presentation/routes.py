from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.tasks.application.schemas import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
)
from app.modules.tasks.application.services import TaskService
from app.modules.tasks.infrastructure.repositories import TaskRepository

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    repository = TaskRepository(db)
    return TaskService(repository)


@router.post("/", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreateSchema,
    service: TaskService = Depends(get_task_service),
):
    return service.create_task(payload)


@router.get("/", response_model=list[TaskResponseSchema])
def list_tasks(
    service: TaskService = Depends(get_task_service),
):
    return service.list_tasks()


@router.get("/{task_id}", response_model=TaskResponseSchema)
def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.put("/{task_id}", response_model=TaskResponseSchema)
def update_task(
    task_id: str,
    payload: TaskUpdateSchema,
    service: TaskService = Depends(get_task_service),
):
    task = service.update_task(task_id, payload)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
):
    deleted = service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return None