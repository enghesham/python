from app.infrastructure.database.sqlite import SqliteDatabase
from app.infrastructure.persistence.sqlalchemy_task_repository import (
    SqlAlchemyTaskRepository,
)


class SqliteTaskRepository(SqlAlchemyTaskRepository):
    def __init__(self, database: SqliteDatabase) -> None:
        super().__init__(database)
