from invenio_records.dumpers import ElasticsearchDumper as InvenioElasticsearchDumper


class NRDocumentRecordDumper(InvenioElasticsearchDumper):
    """NRDocumentRecord elasticsearch dumper."""
