#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Find Documents in MongoDB """


from pymongo import MongoClient


from baseblock import Enforcer
from baseblock import Stopwatch
from baseblock import BaseObject


class FindDocuments(BaseObject):
    """ Find Documents in MongoDB """

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

    def find(self) -> list:
        sw = Stopwatch()

        results = list(self._collection.find())

        if self.isEnabledForDebug:
            self.logger.debug('\n'.join([
                "Retrieved Results",
                f"\tTotal Results: {len(results)}",
                f"\tTotal Time: {str(sw)}"]))

        return results
