from datetime import datetime
from pydantic import BaseModel, Field


class TaskCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class TaskUpdateSchema(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_completed: bool | None = None


class TaskResponseSchema(BaseModel):
    id: str
    title: str
    description: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }