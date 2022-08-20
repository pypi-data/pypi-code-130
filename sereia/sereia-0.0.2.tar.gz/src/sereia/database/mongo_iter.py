from pathlib import Path
import pickle

import pymongo

from sereia.config.config import DefaultConfiguration
from sereia.utils import (
    ConfigHandler,
    DocumentTraverser,
    Tokenizer,
)


class MongoIter:
    def __init__(self, database_table_columns, database_name, database_client, **kwargs):
        self.config = ConfigHandler()
        self.database_name = database_name
        self.database_client = database_client
        self.database_table_columns = database_table_columns
        self.table_hash = self._get_indexable_schema_elements()
        self.limit_per_collection = kwargs.get('limit_per_table', 0)
        self.tokenizer = kwargs.get('tokenizer', Tokenizer())

    def _schema_element_validator(self,table,column):
        return True

    def _get_indexable_schema_elements(self):

        table_hash = {}
        for table, column in self.database_table_columns:
            table_hash.setdefault(table, []).append(column)

        return table_hash

    def __iter__(self):
        collection_count = 0
        for collection,columns in self.table_hash.items():
            collection_count += 1

            indexable_columns = [
                col for col in columns if self._schema_element_validator(collection, col)]
            print('Indexable columns: {}'.format(indexable_columns))

            if len(indexable_columns)==0:
                continue

            print(f"{collection_count} of {len(self.table_hash.keys())} collections indexed")
            
            database = self.database_client[self.database_name]
            collection_document_count = database[collection].count_documents({})
            document_count = 0

            traverser = DocumentTraverser()

            for document in database[collection].find(
                projection=columns,
                batch_size=DefaultConfiguration.DATABASE_CURSOR_BATCH_SIZE,
                show_record_id=True,
            ):

                document_record_id = document['$recordId']
                del document['$recordId']

                document_count += 1

                if (document_count % DefaultConfiguration.DATABASE_INDEX_CHECKPOINT_VALUE) == 0:
                    print(f"Indexed {document_count} of {collection_document_count} for collection {collection}")


                traverser.traverse(document)
                indexable_content = traverser.get_indexable_content()

                for column, content in indexable_content:

                    # This was used when we define the indexable content in the config file
                    # We also must be aware of how we define this for nested document
                    # if column not in document:
                    #     continue

                    # TODO: the behaviour below is not valid anymore, it only worked on Yelp
                    # if type(column) == list:
                    #     content = ' '.join(document[column])
                    # else:
                    content = str(content)

                    tokens = self.tokenizer.tokenize(content)

                    for token in tokens:
                        yield collection, document_record_id, column, token

                traverser.cleanup()

                if (document_count % DefaultConfiguration.DATABASE_CURSOR_BATCH_SIZE) == 0:
                    print(
                        f"Indexed {document_count} of {collection_document_count} for collection {collection}")
