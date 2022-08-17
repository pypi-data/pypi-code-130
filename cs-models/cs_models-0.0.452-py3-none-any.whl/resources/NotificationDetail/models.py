from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Text,
    ForeignKey,
)
from datetime import datetime

from ...database import Base


class NotificationDetailModel(Base):
    __tablename__ = 'notification_details'

    id = Column(Integer, primary_key=True)
    notification_id = Column(
        Integer,
        ForeignKey('notifications.id'),
        nullable=False,
    )
    company_matches = Column(Text, nullable=True)
    drug_matches = Column(Text, nullable=True)
    disease_matches = Column(Text, nullable=True)
    target_matches = Column(Text, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
