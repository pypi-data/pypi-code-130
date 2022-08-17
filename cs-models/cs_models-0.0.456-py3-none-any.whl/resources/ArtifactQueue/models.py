from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Text,
    String,
)

from ...database import Base


class ArtifactQueueModel(Base):
    __tablename__ = "artifact_queue"

    id = Column(Integer, primary_key=True)
    source_type = Column(String(50), nullable=False)
    source_table = Column(String(50), nullable=False)
    source_id = Column(Integer, nullable=False)
    artifact_mappings = Column(Text, nullable=True)
    date = Column(DateTime, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
