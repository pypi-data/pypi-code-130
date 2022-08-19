import nr_vocabularies.records.api
import oarepo_vocabularies.records.system_fields.pid_hierarchy_relation
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import ConstantField, RelationsField
from invenio_records_resources.records.api import Record as InvenioBaseRecord
from invenio_records_resources.records.systemfields import IndexField
from invenio_records_resources.records.systemfields.pid import PIDField, PIDFieldContext

from nr_documents_records.records.dumper import NRDocumentRecordDumper
from nr_documents_records.records.models import NRDocumentRecordMetadata
from nr_documents_records.records.multilingual_dumper import MultilingualDumper


class NRDocumentRecord(InvenioBaseRecord):
    model_cls = NRDocumentRecordMetadata
    schema = ConstantField("$schema", "local://nr-documents-records-1.0.0.json")
    index = IndexField("nr_documents_records-nr-documents-records-1.0.0")

    pid = PIDField(
        create=True, provider=RecordIdProviderV2, context_cls=PIDFieldContext
    )

    dumper_extensions = [
        RelationDumperExt("relations"),
    ]
    dumper = NRDocumentRecordDumper(extensions=dumper_extensions)

    relations = RelationsField(
        resourceType=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "metadata.resourceType",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="resourceType-relation",
        ),
        accessRights=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "metadata.accessRights",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="accessRights-relation",
        ),
        affiliations=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyListRelation(
            "metadata.creators.affiliations",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="affiliations-relation",
        ),
        role=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "metadata.contributors.role",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="role-relation",
        ),
        affiliations=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyListRelation(
            "metadata.contributors.affiliations",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="affiliations-relation",
        ),
        subjectCategories=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyListRelation(
            "metadata.subjectCategories",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="subjectCategories-relation",
        ),
        languages=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyListRelation(
            "metadata.languages",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="languages-relation",
        ),
        rights=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyListRelation(
            "metadata.rights",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="rights-relation",
        ),
        itemRelationType=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "metadata.relatedItems.itemRelationType",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="itemRelationType-relation",
        ),
        itemResourceType=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "metadata.relatedItems.itemResourceType",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="itemResourceType-relation",
        ),
        affiliations=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyListRelation(
            "metadata.relatedItems.itemCreators.affiliations",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="affiliations-relation",
        ),
        role=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "metadata.relatedItems.itemContributors.role",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="role-relation",
        ),
        affiliations=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyListRelation(
            "metadata.relatedItems.itemContributors.affiliations",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="affiliations-relation",
        ),
        funder=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "metadata.fundingReferences.funder",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="funder-relation",
        ),
        country=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "metadata.events.eventLocation.country",
            keys=["id", "title"],
            pid_field=nr_vocabularies.records.api.NRVocabulary.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="country-relation",
        ),
    )


NRDocumentRecord.dumper_extensions.append(MultilingualDumper)
