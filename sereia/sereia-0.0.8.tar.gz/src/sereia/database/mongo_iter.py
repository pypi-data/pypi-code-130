from pathlib import Path
import pickle

import pymongo

from sereia.utils import (
    ConfigHandler,
    DocumentTraverser,
    Tokenizer,
)


class MongoIter:
    def __init__(self, database_table_columns, database_name, database_client,
                 database_cursor_batch_size=10000, **kwargs):
        self.database_name = database_name
        self.database_client = database_client
        self.database_table_columns = database_table_columns
        self.table_hash = self._get_indexable_schema_elements()
        self.limit_per_collection = kwargs.get('limit_per_table', 0)
        self.tokenizer = kwargs.get('tokenizer', Tokenizer())
        self.database_cursor_batch_size = database_cursor_batch_size

    def _schema_element_validator(self,table,column):
        return True

    def _get_indexable_schema_elements(self):

        table_hash = {}
        for table, column in self.database_table_columns:
            table_hash.setdefault(table, []).append(column)

        return table_hash

    def __iter__(self):
        collection_count = 0
        for collection, attributes in self.table_hash.items():
            collection_count += 1

            indexable_attributes = [
                 attr for attr in attributes if self._schema_element_validator(collection, attr)]

            if len(indexable_attributes) == 0:
                continue

            print(f"{collection_count} of {len(self.table_hash.keys())} collections indexed")

            database = self.database_client[self.database_name]
            collection_document_count = database[collection].count_documents({})
            document_count = 0

            traverser = DocumentTraverser()

            for document in database[collection].find(
                projection=attributes,
                batch_size=self.database_cursor_batch_size,
                show_record_id=True,
            ):

                document_record_id = document['$recordId']
                del document['$recordId']

                document_count += 1

                if (document_count % self.database_cursor_batch_size) == 0:
                    print(f"Indexed {document_count} of {collection_document_count} for collection {collection}")

                traverser.traverse(document)
                indexable_content = traverser.get_indexable_content()

                for column, content in indexable_content:
                    content = str(content)

                    tokens = self.tokenizer.tokenize(content)

                    for token in tokens:
                        yield collection, document_record_id, column, token

                traverser.cleanup()
