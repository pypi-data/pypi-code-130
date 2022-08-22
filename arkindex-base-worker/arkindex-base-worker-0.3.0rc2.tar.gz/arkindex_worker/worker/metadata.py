# -*- coding: utf-8 -*-
"""
ElementsWorker methods for metadata.
"""

from enum import Enum

from arkindex_worker import logger
from arkindex_worker.models import Element


class MetaType(Enum):
    """
    Type of a metadata.
    """

    Text = "text"
    """
    A regular string with no special interpretation.
    """

    HTML = "html"
    """
    A metadata with a string value that should be interpreted as HTML content.
    The allowed HTML tags are restricted for security reasons.
    """

    Date = "date"
    """
    A metadata with a string value that should be interpreted as a date.
    The date should be formatted as an ISO 8601 date (``YYYY-MM-DD``).
    """

    Location = "location"
    """
    A metadata with a string value that should be interpreted as a location.
    """

    Reference = "reference"
    """
    A metadata with a string value that should be interpreted as an external identifier
    to this element, for example to preserve a link to the original data before it was
    imported into Arkindex.
    """

    Numeric = "numeric"
    """
    A metadata with a floating point value.
    """

    URL = "url"
    """
    A metadata with a string value that should be interpreted as an URL.
    Only the ``http`` and ``https`` schemes are allowed.
    """


class MetaDataMixin(object):
    """
    Mixin for the :class:`ElementsWorker` to add ``MetaData`` helpers.
    """

    def create_metadata(self, element, type, name, value, entity=None):
        """
        Create a metadata on the given element through API.

        :param element Element: The element to create a metadata on.
        :param type MetaType: Type of the metadata.
        :param name str: Name of the metadata.
        :param value str: Value of the metadata.
        :param entity: UUID of an entity this metadata is related to.
        :type entity: str or None
        :returns str: UUID of the created metadata.
        """
        assert element and isinstance(
            element, Element
        ), "element shouldn't be null and should be of type Element"
        assert type and isinstance(
            type, MetaType
        ), "type shouldn't be null and should be of type MetaType"
        assert name and isinstance(
            name, str
        ), "name shouldn't be null and should be of type str"
        assert value and isinstance(
            value, str
        ), "value shouldn't be null and should be of type str"
        if entity:
            assert isinstance(entity, str), "entity should be of type str"
        if self.is_read_only:
            logger.warning("Cannot create metadata as this worker is in read-only mode")
            return

        metadata = self.request(
            "CreateMetaData",
            id=element.id,
            body={
                "type": type.value,
                "name": name,
                "value": value,
                "entity_id": entity,
                "worker_version": self.worker_version_id,
            },
        )
        self.report.add_metadata(element.id, metadata["id"], type.value, name)

        return metadata["id"]
