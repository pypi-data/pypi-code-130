from sqlalchemy import String, Column, DateTime

from ..database import DB

Base = DB.Base


class TaskLog(Base):
    __tablename__ = "task_log"
    datetime = Column("datetime", DateTime, primary_key=True, unique=True, index=True)
    id = Column("id", String, index=True)
    log = Column("log", String)
