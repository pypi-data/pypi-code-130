import marshmallow as ma
import marshmallow.fields as ma_fields
import marshmallow.validate as ma_valid
from invenio_records_resources.services.records.schema import BaseRecordSchema
from invenio_records_resources.services.records.schema import (
    BaseRecordSchema as InvenioBaseRecordSchema,
)
from marshmallow import ValidationError
from marshmallow import validates as ma_validates
from nr_vocabularies.services.schema import NRVocabularySchema
from oarepo_vocabularies.services.schema import VocabularyRelationField

from nr_documents_records.records.api import NRDocumentRecord
from nr_documents_records.services.multilingual_schema import MultilingualSchema


class NRDocumentRecordMetadataSchema(
    ma.Schema,
):
    """NRDocumentRecordMetadataSchema schema."""

    extent = ma_fields.String()

    dateIssued = ma_fields.String(required=True)

    title = ma_fields.List(
        ma_fields.Nested(lambda: MultilingualSchema(required=True), required=True)
    )

    resourceType = VocabularyRelationField(
        NRVocabularySchema,
        required=True,
        related_field=NRDocumentRecord.relations.resourceType,
        many=False,
    )

    dateAvailable = ma_fields.String()

    dateModified = ma_fields.String()

    abstract = ma_fields.List(ma_fields.Nested(lambda: MultilingualSchema()))

    methods = ma_fields.List(ma_fields.Nested(lambda: MultilingualSchema()))

    technicalInfo = ma_fields.List(ma_fields.Nested(lambda: MultilingualSchema()))

    accessRights = VocabularyRelationField(
        NRVocabularySchema,
        related_field=NRDocumentRecord.relations.accessRights,
        many=False,
    )

    version = ma_fields.String()

    accessibility = ma_fields.List(ma_fields.Nested(lambda: MultilingualSchema()))

    externalLocation = ma_fields.Nested(ExternalLocationSchema)

    originalRecord = ma_fields.String()

    collections = ma_fields.List(ma_fields.String())

    additionalTitles = ma_fields.List(ma_fields.Nested(AdditionalTitlesSchema))

    creators = ma_fields.List(ma_fields.Nested(CreatorsSchema))

    contributors = ma_fields.List(ma_fields.Nested(ContributorsSchema))

    subjects = ma_fields.List(ma_fields.Nested(SubjectsSchema))

    publishers = ma_fields.List(ma_fields.String())

    subjectCategories = VocabularyRelationField(
        NRVocabularySchema,
        related_field=NRDocumentRecord.relations.subjectCategories,
        many=True,
    )

    languages = VocabularyRelationField(
        NRVocabularySchema,
        required=True,
        related_field=NRDocumentRecord.relations.languages,
        many=True,
    )

    notes = ma_fields.List(ma_fields.String())

    rights = VocabularyRelationField(
        NRVocabularySchema, related_field=NRDocumentRecord.relations.rights, many=True
    )

    relatedItems = ma_fields.List(ma_fields.Nested(RelatedItemsSchema))

    fundingReferences = ma_fields.List(ma_fields.Nested(FundingReferencesSchema))

    geoLocations = ma_fields.List(ma_fields.Nested(GeoLocationsSchema))

    series = ma_fields.List(ma_fields.Nested(SeriesSchema))

    objectIdentifiers = ma_fields.List(ma_fields.Nested(ObjectIdentifiersSchema))

    systemIdentifiers = ma_fields.List(ma_fields.Nested(SystemIdentifiersSchema))

    events = ma_fields.List(ma_fields.Nested(EventsSchema))


class NRDocumentSchema(
    BaseRecordSchema,
):
    """NRDocumentSchema schema."""

    metadata = ma_fields.Nested(NRDocumentRecordMetadataSchema)

    created = ma_fields.Date(dump_only=True)

    updated = ma_fields.Date(dump_only=True)
