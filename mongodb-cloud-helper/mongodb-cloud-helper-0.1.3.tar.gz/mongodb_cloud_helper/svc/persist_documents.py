#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Persist Documents into MongoDB """


from pprint import pprint

from pymongo import MongoClient
from pymongo.errors import BulkWriteError

from baseblock import Enforcer
from baseblock import BaseObject


class PersistDocuments(BaseObject):
    """ Persist Documents into MongoDB """

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

    def _validate(self,
                  document: dict) -> None:

        if type(document) != dict:
            self.logger.error('\n'.join([
                "Invalid Persistence Request",
                f"\tInput Document must be dictionaries"]))
            raise ValueError

        if 'membership' not in document:
            self.logger.error('\n'.join([
                "Invalid Persistence Request",
                f"\tInput Document must have pre-assigned Membership ID"]))
            raise ValueError

    def one(self,
            document: dict) -> int:
        self._validate(document)
        return self._collection.insert_one(document).inserted_id

    def many(self,
             documents: list) -> str:

        [self._validate(x) for x in documents]

        try:
            self._collection.insert_many(documents)
        except BulkWriteError as e:
            self.logger.error('\n'.join([
                "Failed to Persist Documents",
                f"\tTotal Failed Documents: {len(documents)}"]))

        return None
