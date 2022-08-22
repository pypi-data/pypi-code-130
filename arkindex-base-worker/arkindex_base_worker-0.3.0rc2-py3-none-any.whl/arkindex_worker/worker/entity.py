# -*- coding: utf-8 -*-
"""
ElementsWorker methods for entities.
"""

import os
from enum import Enum

from peewee import IntegrityError

from arkindex_worker import logger
from arkindex_worker.cache import CachedElement, CachedEntity, CachedTranscriptionEntity
from arkindex_worker.models import Element


class EntityType(Enum):
    """
    Type of an entity.
    """

    Person = "person"
    Location = "location"
    Subject = "subject"
    Organization = "organization"
    Misc = "misc"
    Number = "number"
    Date = "date"


class EntityMixin(object):
    """
    Mixin for the :class:`ElementsWorker` to add ``Entity`` helpers.
    """

    def create_entity(
        self, element, name, type, corpus=None, metas=dict(), validated=None
    ):
        """
        Create an entity on the given corpus.
        If cache support is enabled, a :class:`CachedEntity` will also be created.

        :param element: An element on which the entity will be reported with the :class:`Reporter`.
           This does not have any effect on the entity itself.
        :type element: Element or CachedElement
        :param name str: Name of the entity.
        :param type EntityType: Type of the entity.
        :param corpus: UUID of the corpus to create an entity on, or None to use the
           value of the ``ARKINDEX_CORPUS_ID`` environment variable.
        :type corpus: str or None
        """
        if corpus is None:
            corpus = os.environ.get("ARKINDEX_CORPUS_ID")

        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be an Element or CachedElement"
        assert name and isinstance(
            name, str
        ), "name shouldn't be null and should be of type str"
        assert type and isinstance(
            type, EntityType
        ), "type shouldn't be null and should be of type EntityType"
        assert corpus and isinstance(
            corpus, str
        ), "corpus shouldn't be null and should be of type str"
        if metas:
            assert isinstance(metas, dict), "metas should be of type dict"
        if validated is not None:
            assert isinstance(validated, bool), "validated should be of type bool"
        if self.is_read_only:
            logger.warning("Cannot create entity as this worker is in read-only mode")
            return

        entity = self.request(
            "CreateEntity",
            body={
                "name": name,
                "type": type.value,
                "metas": metas,
                "validated": validated,
                "corpus": corpus,
                "worker_version": self.worker_version_id,
            },
        )
        self.report.add_entity(element.id, entity["id"], type.value, name)

        if self.use_cache:
            # Store entity in local cache
            try:
                to_insert = [
                    {
                        "id": entity["id"],
                        "type": type.value,
                        "name": name,
                        "validated": validated if validated is not None else False,
                        "metas": metas,
                        "worker_version_id": self.worker_version_id,
                    }
                ]
                CachedEntity.insert_many(to_insert).execute()
            except IntegrityError as e:
                logger.warning(f"Couldn't save created entity in local cache: {e}")

        return entity["id"]

    def create_transcription_entity(
        self, transcription, entity, offset, length, confidence=None
    ):
        """
        Create a link between an existing entity and an existing transcription.
        If cache support is enabled, a :class:`CachedTranscriptionEntity` will also be created.

        :param transcription str: UUID of the existing transcription.
        :param entity str: UUID of the existing entity.
        :param offset int: Starting position of the entity in the transcription's text,
           as a 0-based index.
        :param length int: Length of the entity in the transcription's text.
        :param confidence: Optional confidence score between 0 or 1.
        :type confidence: float or None
        :returns: A dict as returned by the ``CreateTranscriptionEntity`` API endpoint,
           or None if the worker is in read-only mode.
        :rtype: dict(str, str or int) or None
        """
        assert transcription and isinstance(
            transcription, str
        ), "transcription shouldn't be null and should be of type str"
        assert entity and isinstance(
            entity, str
        ), "entity shouldn't be null and should be of type str"
        assert (
            offset is not None and isinstance(offset, int) and offset >= 0
        ), "offset shouldn't be null and should be a positive integer"
        assert (
            length is not None and isinstance(length, int) and length > 0
        ), "length shouldn't be null and should be a strictly positive integer"
        assert (
            confidence is None or isinstance(confidence, float) and 0 <= confidence <= 1
        ), "confidence should be null or a float in [0..1] range"
        if self.is_read_only:
            logger.warning(
                "Cannot create transcription entity as this worker is in read-only mode"
            )
            return

        body = {
            "entity": entity,
            "length": length,
            "offset": offset,
            "worker_version_id": self.worker_version_id,
        }
        if confidence is not None:
            body["confidence"] = confidence

        transcription_ent = self.request(
            "CreateTranscriptionEntity",
            id=transcription,
            body=body,
        )
        # TODO: Report transcription entity creation

        if self.use_cache:
            # Store transcription entity in local cache
            try:
                CachedTranscriptionEntity.create(
                    transcription=transcription,
                    entity=entity,
                    offset=offset,
                    length=length,
                    worker_version_id=self.worker_version_id,
                    confidence=confidence,
                )
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created transcription entity in local cache: {e}"
                )
        return transcription_ent
