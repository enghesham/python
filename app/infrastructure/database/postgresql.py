from __future__ import annotations

from app.infrastructure.database.sqlalchemy import SqlAlchemyDatabase


class PostgreSqlDatabase(SqlAlchemyDatabase):
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        super().__init__(self._dsn)
