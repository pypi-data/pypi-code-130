from typing import Callable
from sqlalchemy import create_engine, orm, MetaData
from sqlalchemy.orm import Session


class Database:
    """Database session manager"""

    def __init__(self, db_url: str, sa_future: bool = False, sa_echo: bool = False,
                 sa_session_autocommit=False, sa_session_autoflush=False,
                 sa_session_expire_on_commit=True) -> None:
        self._database_created = False
        self._engine = create_engine(
            db_url,
            pool_pre_ping=True,
            echo=sa_echo,
            future=sa_future)
        self._session_factory = orm.sessionmaker(
            autocommit=sa_session_autocommit,
            autoflush=sa_session_autoflush,
            expire_on_commit=sa_session_expire_on_commit,
            bind=self._engine)
        self.current_session = None

    def create_database(self, metadata: MetaData, start_mappers: Callable) -> None:
        if not self._database_created:
            metadata.create_all(self._engine, checkfirst=True)
            start_mappers()
            self._database_created = True

    def session(self, expire_on_commit=True) -> Session:
        if self.current_session is None:
            self.current_session = self._session_factory()
            self.current_session.expire_on_commit = expire_on_commit

        return self.current_session

    def close_session(self):
        if self.current_session is not None:
            self.current_session.close()
            self.current_session = None
