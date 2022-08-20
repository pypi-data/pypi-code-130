import pymongo

from sereia.config.config import DefaultConfiguration


class MongoQueryExecutor(object):

    def __init__(self):
        self.client = pymongo.MongoClient(
            DefaultConfiguration.DATABASE_HOST,
            port=DefaultConfiguration.DATABASE_PORT,
            username=DefaultConfiguration.DATABASE_USER,
            password=DefaultConfiguration.DATABASE_PASSWORD
        )

    def execute(self, base_collection, query):
        database = self.client[
            DefaultConfiguration.DATABASE
        ]

        mongo_result = database[base_collection].aggregate(
            query,
            allowDiskUse=True,
        )

        return mongo_result
