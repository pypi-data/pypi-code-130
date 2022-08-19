from invenio_records_resources.services import RecordLink
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
from invenio_records_resources.services import pagination_links

from nr_documents_records.records.api import NRDocumentRecord
from nr_documents_records.services.permissions import NRDocumentRecordPermissionPolicy
from nr_documents_records.services.schema import NRDocumentSchema
from nr_documents_records.services.search import NRDocumentRecordSearchOptions


class NRDocumentRecordServiceConfig(InvenioRecordServiceConfig):
    """NRDocumentRecord service config."""

    permission_policy_cls = NRDocumentRecordPermissionPolicy
    schema = NRDocumentSchema
    search = NRDocumentRecordSearchOptions
    record_cls = NRDocumentRecord

    components = [*InvenioRecordServiceConfig.components]

    model = "nr_documents_records"

    @property
    def links_item(self):
        return {
            "self": RecordLink("/nr_documents_records/{id}"),
        }

    links_search = pagination_links("/nr_documents_records/{?args*}")
