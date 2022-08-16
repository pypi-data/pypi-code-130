#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Find Documents by (nested) Field """


from pymongo import MongoClient
from pymongo import DESCENDING


from baseblock import Enforcer
from baseblock import Stopwatch
from baseblock import BaseObject


class FindDocumentsByQuery(BaseObject):
    """ Find Documents by (nested) Field """

    __slots__ = (
    )

    def __init__(self,
                 database: str,
                 collection: str,
                 client: MongoClient):
        """ Change Log

        Created:
            16-Aug-2022
            craigtrim@gmail.com

        Args:
            database (str): _description_
            collection (str): _description_
            client (MongoClient, optional): _description_. Defaults to None.
        """
        BaseObject.__init__(self, __name__)
        if self.isEnabledForDebug:
            Enforcer.is_str(database)
            Enforcer.is_str(collection)

        db = client[database]
        self._collection = db[collection]

        if self.isEnabledForDebug:
            self.logger.debug('\n'.join([
                "Initialized Service",
                f"\tDatabase: {database}",
                f"\tCollection: {collection}"]))

    def process(self,
                query: dict,
                sort_field: str = None) -> list:
        """ Find Results  by Query

        Args:
            query (dict): a dictionary query
            Sample Input:
                {'event.analysis.user_source': 'U02U27Q9W20'}

        Returns:
            list: 0..* results
        """
        sw = Stopwatch()

        if self.isEnabledForDebug:
            Enforcer.is_dict(query)

        def find_in_collection():
            finder = self._collection.find(query)
            if not sort_field:
                return finder
            return finder.sort(sort_field, DESCENDING)

        documents = list(find_in_collection())

        if self.isEnabledForDebug:
            self.logger.debug('\n'.join([
                "Find Documents By Query",
                f"\tTotal Time: {str(sw)}",
                f"\tTotal Results: {len(documents)}",
                f"\tQuery: {query}"]))

        return documents
