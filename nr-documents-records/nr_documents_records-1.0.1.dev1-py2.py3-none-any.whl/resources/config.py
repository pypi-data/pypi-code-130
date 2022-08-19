from invenio_records_resources.resources import (
    RecordResourceConfig as InvenioRecordResourceConfig,
)


class NRDocumentRecordResourceConfig(InvenioRecordResourceConfig):
    """NRDocumentRecord resource config."""

    blueprint_name = "NRDocumentRecord"
    url_prefix = "/nr_documents_records/"
