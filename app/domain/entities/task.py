from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4


class TaskStatus(StrEnum):
    TODO = "todo"
    DONE = "done"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Task:
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.description = self.description.strip()
        if not self.title:
            raise ValueError("Task title cannot be empty.")

    def mark_done(self) -> None:
        self.status = TaskStatus.DONE
        self.updated_at = utc_now()
