from app.infrastructure.database.postgresql import PostgreSqlDatabase
from app.infrastructure.persistence.sqlalchemy_task_repository import (
    SqlAlchemyTaskRepository,
)


class PostgreSqlTaskRepository(SqlAlchemyTaskRepository):
    def __init__(self, database: PostgreSqlDatabase) -> None:
        super().__init__(database)
