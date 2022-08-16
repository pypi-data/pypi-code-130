#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Mongo API for Basic Operations """


from baseblock import BaseObject

from mongodb_cloud_helper.svc import FindDocuments
from mongodb_cloud_helper.svc import PersistDocuments
from mongodb_cloud_helper.svc import FindDocumentsByQuery


class MongoBaseAPI(BaseObject):
    """ Mongo API for Basic Operations """

    def __init__(self):
        """
        Created:
            16-Aug-2022
            craigtrim@gmail.com
        """
        BaseObject.__init__(self, __name__)
        from mongodb_cloud_helper import MongoConnector
        self._client = MongoConnector().client()

    def all(self,
            database: str,
            collection: str) -> list:

        svc = FindDocuments(
            database=database,
            collection=collection,
            client=self._client)

        return svc.find()

    def query(self,
              database: str,
              collection: str,
              query: dict,
              sort_field: str = None) -> list:
        """ Query MongoDB in the Cloud

        Args:
            database (str): the mongoDB database
            collection (str): the mongoDB collection
            query (dict): the query to execute against mongoDB

        Returns:
            list: the mongoDB results
        """

        svc = FindDocumentsByQuery(
            database=database,
            collection=collection,
            client=self._client)

        return svc.process(
            query=query,
            sort_field=sort_field)

    def persist_many(self,
                     database: str,
                     collection: str,
                     documents: list) -> str:
        """ Persist Multiple Documents to MongoDB

        Args:
            database (str): the mongoDB database
            collection (str): the mongoDB collection
            document (dict): the documents to persist

        Returns:
            str: membership ID
        """

        svc = PersistDocuments(
            database=database,
            collection=collection,
            client=self._client)

        return svc.many(documents)

    def persist_one(self,
                    database: str,
                    collection: str,
                    document: dict) -> int:
        """ Perist a Single Document to MongoDB

        Args:
            database (str): the mongoDB database
            collection (str): the mongoDB collection
            document (dict): the document to persist

        Returns:
            int: the total documents persisted
        """

        svc = PersistDocuments(
            database=database,
            collection=collection,
            client=self._client)

        return svc.one(document)
