class TaskManagerError(Exception):
    """Base exception for application errors."""


class TaskNotFoundError(TaskManagerError):
    """Raised when the requested task does not exist."""
