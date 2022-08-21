from pathlib import Path
import pickle
from pprint import pprint as pp

import pymongo

from sereia.database.mongo_iter import MongoIter
from sereia.utils import ConfigHandler, DocumentTraverser


class MongoHandler:
    def __init__(self, database_name, database_credentials, config_handler, **kwargs):
        self.database_name = database_name
        self.database_credentials = database_credentials
        self.database_client = pymongo.MongoClient(
            database_credentials,
        )

        self.database_batch_cursor_size = kwargs.get('database_batch_cursor_size', 10000)

    def set_database_name(self, database_name):
        self.database_name = database_name

    def execute(self, base_collection, query):
        database = self.database_client[
            self.database_name
        ]

        mongo_result = database[base_collection].aggregate(
            query,
            allowDiskUse=True,
        )

        return mongo_result

    def get_collections_and_attributes(self, indexable_attributes=None):
        database = self.database_client[self.database_name]

        collections_attributes = {}
        collections_structure = {}
        for collection in self.get_collections_names():
            collections_attributes[collection] = set([])
            collections_structure[collection] = {}

            projection_attributes = None

            if indexable_attributes:
                for item in indexable_attributes:
                    if item[0] == collection:
                        projection_attributes = item[1]

            for document in database[collection].find(
                projection=projection_attributes,
                batch_size=self.database_batch_cursor_size,
            ):

                traverser = DocumentTraverser()
                traverser.traverse(document)
                document_attributes = traverser.get_document_attributes().keys()
                for attribute in document_attributes:

                    if attribute != '_id':
                        collections_attributes[collection].add(
                            attribute,
                        )

                attributes_with_types = traverser.get_document_attributes()

                for attribute in attributes_with_types:
                    if attributes_with_types[attribute] != type(None):
                        collections_structure[collection][attribute] = attributes_with_types[attribute]

            collections_attributes[collection] = list(
                collections_attributes[collection]
            )

        print(f'Storing {self.database_name} database structure...')
        Path('tmp/').mkdir(exist_ok=True)
        with open(
            '/'.join(['tmp/', self.database_name + '.pickle']),
            mode = 'wb',
        ) as f:
            pickle.dump(
                collections_structure,
                f,
                protocol=pickle.HIGHEST_PROTOCOL
            )

        return collections_attributes

    def iterate_over_keywords(self, schema_index, indexable_attributes, **kwargs):
        schema_index_attributes = schema_index.tables_attributes(self.database_name, nested_structures=True)
        if indexable_attributes:
            for attribute in indexable_attributes:
                if attribute not in schema_index_attributes:
                    print('Attribute {} not located in Schema Index... Re-check and try again.'.format(attribute))
                    exit(1)

        return MongoIter(
            indexable_attributes,
            self.database_name,
            self.database_client,
            self.database_batch_cursor_size,
            **kwargs
        )

    def exist_results(self, query):
        database = self.database_client[self.database_name]
        collection, mongo_query = query.build()

        count = database[collection].aggregate(mongo_query)

        for item in count:
            if item:
                count.close()
                return True

        return False
    
    def get_databases(self):
        databases = self.database_client.list_database_names()
        databases = [database for database in databases if database not in ['admin', 'local']]

        return databases

    def get_collections_names(self):
        database = self.database_client[self.database_name]
        filter = {"name": {"$regex": r"^(?!system\.)"}}

        collection_names = database.list_collection_names(filter=filter)

        return collection_names
