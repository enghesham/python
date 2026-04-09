from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class SqlAlchemyDatabase:
    def __init__(self, connection_url: str) -> None:
        self._engine = create_engine(connection_url, future=True)
        self._session_factory = sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=Session,
        )
        self.initialize()

    def initialize(self) -> None:
        from app.infrastructure.database.models import Base

        Base.metadata.create_all(self._engine)

    def close(self) -> None:
        self._engine.dispose()

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
