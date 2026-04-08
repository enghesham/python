from __future__ import annotations

from pathlib import Path

from app.infrastructure.database.sqlalchemy import SqlAlchemyDatabase


class SqliteDatabase(SqlAlchemyDatabase):
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(f"sqlite:///{self._database_path}")
