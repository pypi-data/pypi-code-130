from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
)
from datetime import datetime

from ...database import Base


class NotificationModel(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), nullable=False)
    search_id = Column(
        Integer,
        ForeignKey('user_saved_searches.id'),
        nullable=False,
    )
    source_type = Column(String(50), nullable=False)
    source_id = Column(Integer, nullable=False)
    matches = Column(Text, nullable=True)
    seen = Column(Boolean, nullable=True)
    date = Column(DateTime, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
