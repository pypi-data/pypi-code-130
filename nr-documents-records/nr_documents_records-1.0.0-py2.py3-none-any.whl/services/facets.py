"""Facet definitions."""

from elasticsearch_dsl import Facet
from elasticsearch_dsl.query import Nested
from invenio_records_resources.services.records.facets import TermsFacet


class NestedLabeledFacet(Facet):
    agg_type = "nested"

    def __init__(self, path, nested_facet, label=""):
        self._path = path
        self._inner = nested_facet
        self._label = label
        super(NestedLabeledFacet, self).__init__(
            path=path,
            aggs={
                "inner": nested_facet.get_aggregation(),
            },
        )

    def get_values(self, data, filter_values):
        return self._inner.get_values(data.inner, filter_values)

    def add_filter(self, filter_values):
        inner_q = self._inner.add_filter(filter_values)
        if inner_q:
            return Nested(path=self._path, query=inner_q)

    def get_labelled_values(self, data, filter_values):
        """Get a labelled version of a bucket."""
        try:
            out = data["buckets"]
        except:
            out = []
        return {"buckets": out, "label": str(self._label)}


metadata_extent = TermsFacet(field="metadata.extent")


metadata_dateIssued = TermsFacet(field="metadata.dateIssued")


metadata_title = TermsFacet(field="metadata.title")


metadata_dateAvailable = TermsFacet(field="metadata.dateAvailable")


metadata_dateModified = TermsFacet(field="metadata.dateModified")


metadata_abstract = TermsFacet(field="metadata.abstract")


metadata_methods = TermsFacet(field="metadata.methods")


metadata_technicalInfo = TermsFacet(field="metadata.technicalInfo")


metadata_version = TermsFacet(field="metadata.version")


metadata_accessibility = TermsFacet(field="metadata.accessibility")


metadata_externalLocation_externalLocationURL = TermsFacet(
    field="metadata.externalLocation.externalLocationURL"
)


metadata_originalRecord = TermsFacet(field="metadata.originalRecord")


metadata_collections = TermsFacet(field="metadata.collections")


metadata_additionalTitles_title = TermsFacet(field="metadata.additionalTitles.title")


metadata_additionalTitles_titleType = TermsFacet(
    field="metadata.additionalTitles.titleType"
)


metadata_additionalTitles = TermsFacet(field="metadata.additionalTitles")


metadata_creators_fullName = TermsFacet(field="metadata.creators.fullName")


metadata_creators_nameType = TermsFacet(field="metadata.creators.nameType")


metadata_creators_authorityIdentifiers_identifier = TermsFacet(
    field="metadata.creators.authorityIdentifiers.identifier"
)


metadata_creators_authorityIdentifiers_scheme = TermsFacet(
    field="metadata.creators.authorityIdentifiers.scheme"
)


metadata_creators_authorityIdentifiers = TermsFacet(
    field="metadata.creators.authorityIdentifiers"
)


metadata_creators_affiliations = TermsFacet(field="metadata.creators.affiliations")


metadata_creators = TermsFacet(field="metadata.creators")


metadata_contributors_fullName = TermsFacet(field="metadata.contributors.fullName")


metadata_contributors_nameType = TermsFacet(field="metadata.contributors.nameType")


metadata_contributors_authorityIdentifiers_identifier = TermsFacet(
    field="metadata.contributors.authorityIdentifiers.identifier"
)


metadata_contributors_authorityIdentifiers_scheme = TermsFacet(
    field="metadata.contributors.authorityIdentifiers.scheme"
)


metadata_contributors_authorityIdentifiers = TermsFacet(
    field="metadata.contributors.authorityIdentifiers"
)


metadata_contributors_affiliations = TermsFacet(
    field="metadata.contributors.affiliations"
)


metadata_contributors = TermsFacet(field="metadata.contributors")


metadata_subjects_subjectScheme = TermsFacet(field="metadata.subjects.subjectScheme")


metadata_subjects_subject = TermsFacet(field="metadata.subjects.subject")


metadata_subjects_valueURI = TermsFacet(field="metadata.subjects.valueURI")


metadata_subjects_classificationCode = TermsFacet(
    field="metadata.subjects.classificationCode"
)


metadata_subjects = TermsFacet(field="metadata.subjects")


metadata_subjectCategories = TermsFacet(field="metadata.subjectCategories")


metadata_languages = TermsFacet(field="metadata.languages")


metadata_rights = TermsFacet(field="metadata.rights")


metadata_relatedItems_itemURL = TermsFacet(field="metadata.relatedItems.itemURL")


metadata_relatedItems_itemYear = TermsFacet(field="metadata.relatedItems.itemYear")


metadata_relatedItems_itemVolume = TermsFacet(field="metadata.relatedItems.itemVolume")


metadata_relatedItems_itemIssue = TermsFacet(field="metadata.relatedItems.itemIssue")


metadata_relatedItems_itemStartPage = TermsFacet(
    field="metadata.relatedItems.itemStartPage"
)


metadata_relatedItems_itemEndPage = TermsFacet(
    field="metadata.relatedItems.itemEndPage"
)


metadata_relatedItems_itemPublisher = TermsFacet(
    field="metadata.relatedItems.itemPublisher"
)


metadata_relatedItems_itemCreators_fullName = TermsFacet(
    field="metadata.relatedItems.itemCreators.fullName"
)


metadata_relatedItems_itemCreators_nameType = TermsFacet(
    field="metadata.relatedItems.itemCreators.nameType"
)


metadata_relatedItems_itemCreators_authorityIdentifiers_identifier = TermsFacet(
    field="metadata.relatedItems.itemCreators.authorityIdentifiers.identifier"
)


metadata_relatedItems_itemCreators_authorityIdentifiers_scheme = TermsFacet(
    field="metadata.relatedItems.itemCreators.authorityIdentifiers.scheme"
)


metadata_relatedItems_itemCreators_authorityIdentifiers = TermsFacet(
    field="metadata.relatedItems.itemCreators.authorityIdentifiers"
)


metadata_relatedItems_itemCreators_affiliations = TermsFacet(
    field="metadata.relatedItems.itemCreators.affiliations"
)


metadata_relatedItems_itemCreators = TermsFacet(
    field="metadata.relatedItems.itemCreators"
)


metadata_relatedItems_itemContributors_fullName = TermsFacet(
    field="metadata.relatedItems.itemContributors.fullName"
)


metadata_relatedItems_itemContributors_nameType = TermsFacet(
    field="metadata.relatedItems.itemContributors.nameType"
)


metadata_relatedItems_itemContributors_authorityIdentifiers_identifier = TermsFacet(
    field="metadata.relatedItems.itemContributors.authorityIdentifiers.identifier"
)


metadata_relatedItems_itemContributors_authorityIdentifiers_scheme = TermsFacet(
    field="metadata.relatedItems.itemContributors.authorityIdentifiers.scheme"
)


metadata_relatedItems_itemContributors_authorityIdentifiers = TermsFacet(
    field="metadata.relatedItems.itemContributors.authorityIdentifiers"
)


metadata_relatedItems_itemContributors_affiliations = TermsFacet(
    field="metadata.relatedItems.itemContributors.affiliations"
)


metadata_relatedItems_itemContributors = TermsFacet(
    field="metadata.relatedItems.itemContributors"
)


metadata_relatedItems_itemPIDs_identifier = TermsFacet(
    field="metadata.relatedItems.itemPIDs.identifier"
)


metadata_relatedItems_itemPIDs_scheme = TermsFacet(
    field="metadata.relatedItems.itemPIDs.scheme"
)


metadata_relatedItems_itemPIDs = TermsFacet(field="metadata.relatedItems.itemPIDs")


metadata_relatedItems = TermsFacet(field="metadata.relatedItems")


metadata_fundingReferences_projectID = TermsFacet(
    field="metadata.fundingReferences.projectID"
)


metadata_fundingReferences = TermsFacet(field="metadata.fundingReferences")


metadata_geoLocations_geoLocationPlace = TermsFacet(
    field="metadata.geoLocations.geoLocationPlace"
)


metadata_geoLocations_geoLocationPoint_pointLongitude = TermsFacet(
    field="metadata.geoLocations.geoLocationPoint.pointLongitude"
)


metadata_geoLocations_geoLocationPoint_pointLatitude = TermsFacet(
    field="metadata.geoLocations.geoLocationPoint.pointLatitude"
)


metadata_geoLocations = TermsFacet(field="metadata.geoLocations")


metadata_series_seriesTitle = TermsFacet(field="metadata.series.seriesTitle")


metadata_series_seriesVolume = TermsFacet(field="metadata.series.seriesVolume")


metadata_series = TermsFacet(field="metadata.series")


metadata_objectIdentifiers_identifier = TermsFacet(
    field="metadata.objectIdentifiers.identifier"
)


metadata_objectIdentifiers_scheme = TermsFacet(
    field="metadata.objectIdentifiers.scheme"
)


metadata_objectIdentifiers = TermsFacet(field="metadata.objectIdentifiers")


metadata_systemIdentifiers_identifier = TermsFacet(
    field="metadata.systemIdentifiers.identifier"
)


metadata_systemIdentifiers_scheme = TermsFacet(
    field="metadata.systemIdentifiers.scheme"
)


metadata_systemIdentifiers = TermsFacet(field="metadata.systemIdentifiers")


metadata_events_eventDate = TermsFacet(field="metadata.events.eventDate")


metadata_events_eventLocation_place = TermsFacet(
    field="metadata.events.eventLocation.place"
)


metadata_events = TermsFacet(field="metadata.events")


_id = TermsFacet(field="id")


created = TermsFacet(field="created")


updated = TermsFacet(field="updated")


_schema = TermsFacet(field="$schema")
