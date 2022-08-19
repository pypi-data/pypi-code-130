from invenio_db import db
from invenio_records.models import RecordMetadataBase


class NRDocumentRecordMetadata(db.Model, RecordMetadataBase):
    """Model for NRDocumentRecord metadata."""

    __tablename__ = "nrdocumentrecord_metadata"

    # Enables SQLAlchemy-Continuum versioning
    __versioned__ = {}
