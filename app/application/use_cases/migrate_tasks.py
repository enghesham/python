from app.domain.repositories.task_repository import TaskRepository


class MigrateTasksUseCase:
    def __init__(
        self,
        source_repository: TaskRepository,
        destination_repository: TaskRepository,
    ) -> None:
        self._source_repository = source_repository
        self._destination_repository = destination_repository

    def execute(self) -> int:
        migrated = 0
        for task in self._source_repository.list_all():
            if self._destination_repository.get_by_id(task.id) is not None:
                continue

            self._destination_repository.add(task)
            migrated += 1

        return migrated
