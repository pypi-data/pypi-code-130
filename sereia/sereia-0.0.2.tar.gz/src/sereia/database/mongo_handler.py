from pathlib import Path
import pickle
from pprint import pprint as pp

import pymongo

from sereia.config.config import DefaultConfiguration
from sereia.database.mongo_iter import MongoIter
from sereia.utils import ConfigHandler, DocumentTraverser


class MongoHandler:
    def __init__(self, database_name, database_client):
        self.config = ConfigHandler()
        self.database_name = database_name
        self.database_client = database_client

    def get_collections_and_attributes(self, mongo_client, predefined_attributes=None):
        database = mongo_client[self.database_name]

        collections_attributes = {}
        collections_structure = {}
        for collection in self.get_collections_names(mongo_client):
            collections_attributes[collection] = set([])
            collections_structure[collection] = {}

            projection_attributes = None

            if predefined_attributes:
                for item in predefined_attributes:
                    if item[0] == collection:
                        projection_attributes = item[1]

            for document in database[collection].find(
                projection=projection_attributes,
                batch_size=DefaultConfiguration.DATABASE_CURSOR_BATCH_SIZE,
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
            collections_attributes[collection])

        print(f'Storing {self.database_name} database structure...')
        Path(DefaultConfiguration.TEMP_FILES_PATH).mkdir(exist_ok=True)
        with open(
            '/'.join([DefaultConfiguration.TEMP_FILES_PATH, self.database_name + '.pickle']),
            mode = 'wb',
        ) as f:
            pickle.dump(
                collections_structure,
                f,
                protocol=pickle.HIGHEST_PROTOCOL
            )

        return collections_attributes

    def iterate_over_keywords(self, schema_index, predefined_attributes, database_client, **kwargs):
        schema_index_attributes = schema_index.tables_attributes(nested_structures=True)
        for attribute in predefined_attributes:
            if attribute not in schema_index_attributes:
                print('Attribute {} not located in Schema Index... Re-check and try again.'.format(attribute))
                exit(1)

        return MongoIter(predefined_attributes, self.database_name, self.database_client, **kwargs)

    def exist_results(self, query):
        client = pymongo.MongoClient(
            DefaultConfiguration.DATABASE_HOST,
            port=DefaultConfiguration.DATABASE_PORT,
            username=DefaultConfiguration.DATABASE_USER,
            password=DefaultConfiguration.DATABASE_PASSWORD
        )
        database = client[self.database_name]
        collection, mongo_query = query.build()

        count = database[collection].aggregate(mongo_query)

        for item in count:
            if item:
                count.close()
                return True

        return False
    
    def get_databases(self, mongo_client):
        databases = mongo_client.list_database_names()
        databases = [database for database in databases if database not in ['admin', 'local']]

        return databases

    def get_collections_names(self, mongo_client):
        print('database {}'.format(self.database_name))
        database = mongo_client[self.database_name]
        filter = {"name": {"$regex": r"^(?!system\.)"}}

        collection_names = database.list_collection_names(filter=filter)

        return collection_names
