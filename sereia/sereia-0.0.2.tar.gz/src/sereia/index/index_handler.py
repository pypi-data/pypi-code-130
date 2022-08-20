import gc
from glob import glob
import shelve
from contextlib import ExitStack
import json
from pprint import pprint as pp
from math import log
from time import time

from sereia.config.config import DefaultConfiguration
from sereia.utils import (
    calculate_tf,
    calculate_inverse_frequency,
    calculate_iaf,
    ConfigHandler,
    load_schema_graph_from_json,
    memory_size,
)

from sereia.index.value_index import ValueIndex
from sereia.index.schema_index import SchemaIndex
from sereia.index.schema_graph import SchemaGraph
from sereia.index.babel_hash import BabelHash
import sys


class IndexHandler:

    def __init__(self, database_handler, database_client, **kwargs):
        self.config = kwargs.get('config',ConfigHandler())
        self.value_index = ValueIndex()
        self.schema_index = SchemaIndex()
        self.schema_graph = SchemaGraph()
        self.database_client = database_client
        self.database_handler = database_handler
        self.partial_index_count=0

    def create_indexes(self):
        if not self.config.create_index:
            print(f'Index Creation is disabled.')
            return

        self.create_schema_graph()
        self.create_partial_schema_index()
        self.create_partial_value_indexes()
        self.merge_partial_value_indexes_and_process_max_frequency()
        self.process_norms()

    def create_schema_graph(self):
        fk_constraints = load_schema_graph_from_json(DefaultConfiguration.DATABASE)
        self.database_handler.get_collections_names(
            self.database_client,
        )

        for constraint,values in fk_constraints.items():
            self.schema_graph.add_fk_constraint(constraint,*values)

        if not len(self.schema_graph):
            self.schema_graph.add_root(
                self.database_handler.get_collections_names(
                    self.database_client,
                )[0],
            )

        self.schema_graph.persist_to_file(
            self.config.dataset_directory,
            self.config.schema_graph_filepath,
        )

    def create_partial_schema_index(self):
        tables_attributes = None

        tables_attributes = self.database_handler.get_collections_and_attributes(
            self.database_client,
        )

        metrics = {'max_frequency':0, 'norm':[0,0,0,0]}
        self.schema_index.create_entries(tables_attributes,metrics)

    def create_partial_value_indexes(self,**kwargs):
        unit = kwargs.get('unit', 2**30)
        max_memory_allowed = DefaultConfiguration.HOST_MAX_RAM_LIMIT
        max_memory_allowed *= unit
        gb = 1 * unit

        attributes_filepath = self.config.attributes_filepath
        with open(attributes_filepath,'r') as indexable_attributes_file:     
            predefined_attributes = [
                (item['table'],attribute)
                for item in json.load(indexable_attributes_file)
                for attribute in item['attributes']
            ]

        def part_index():
            self.partial_index_count += 1
            partial_index_filename = f'{self.config.value_index_filepath}.part{self.partial_index_count:02d}'
            # print(f'Storing value_index.part{self.partial_index_count} in {partial_index_filename}')
            self.value_index.persist_to_file(self.config.dataset_directory, partial_index_filename)
            self.value_index = ValueIndex()
            # print('Storing file because of space')
            gc.collect()
            # print('Resuming indexing process...')

        for table, ctid, attribute, word in self.database_handler.iterate_over_keywords(
                self.schema_index,
                predefined_attributes,
                self.database_client
            ):
            self.value_index.add_mapping(word,table,attribute,ctid)
            
            if memory_size() >= max_memory_allowed:
                print(f'Memory usage exceeded the maximum memory allowed (above {max_memory_allowed/gb:.2f}GB).')
                part_index()

        part_index()

    def merge_partial_value_indexes_and_process_max_frequency(self):
        num_total_attributes=self.schema_index.get_num_total_attributes()
        babel = BabelHash.babel

        value_index_path = self.config.dataset_directory + self.config.value_index_filepath
        filenames=glob(f'{value_index_path}.part*')
        filenames = [file.replace('.db', '') for file in filenames]

        with ExitStack() as stack:
            partial_value_indexes = [stack.enter_context(shelve.open(fname,flag='r')) for fname in filenames]
            final_value_index = stack.enter_context(shelve.open(f'{value_index_path}'))

            for partial_value_index in partial_value_indexes:
                babel.update(partial_value_index['__babel__'])
            final_value_index['__babel__'] = babel

            for i in range( len(partial_value_indexes)):
                # print(f'i {i} {filenames[i]}')
                for word in partial_value_indexes[i]:
                    # print(word)

                    if word in final_value_index or word == '__babel__':
                    #     print('Word in final hash')
                        continue

                    value_list = [ partial_value_indexes[i][word] ]

                    for j in range(i+1,len(partial_value_indexes)):
                        # print(f'  j {j} {filenames[j]}')
                        if word in partial_value_indexes[j]:
                            value_list.append(partial_value_indexes[j][word])

                    merged_babel_hash = BabelHash()
                    if len(value_list)>1:
                        for ( _ ,part_babel_hash) in value_list:
                            for table in part_babel_hash:
                                merged_babel_hash.setdefault(table,BabelHash())
                                for attribute in part_babel_hash[table]:
                                    merged_babel_hash[table].setdefault( attribute , [] )
                                    merged_babel_hash[table][attribute]+= part_babel_hash[table][attribute]
                    else:
                        _ ,merged_babel_hash = value_list[0]

                    for table in merged_babel_hash:
                        for attribute in merged_babel_hash[table]:
                            frequency = len(merged_babel_hash[table][attribute])
                            max_frequency = self.schema_index[table][attribute]['max_frequency']
                            if frequency > max_frequency:
                               self.schema_index[table][attribute]['max_frequency'] = frequency


                    num_attributes_with_this_word = sum([len(merged_babel_hash[table]) for table in merged_babel_hash])

                    inverse_frequency = calculate_inverse_frequency(num_total_attributes,num_attributes_with_this_word)
                    merged_value = (inverse_frequency,merged_babel_hash)
                    final_value_index[word]=merged_value

    def process_norms(self):
        value_index_path = self.config.dataset_directory + self.config.value_index_filepath
        with shelve.open(f'{value_index_path}') as full_index:
            for word in full_index:
                if word == '__babel__':
                    continue

                inverse_frequency, babel_hash = full_index[word]
                for table in babel_hash:
                    for attribute in babel_hash[table]:
                        frequency = len(babel_hash[table][attribute])
                        max_frequency = self.schema_index[table][attribute]['max_frequency']
                        
                        for weight_scheme in range(4):
                            tf  = calculate_tf(weight_scheme,frequency,max_frequency)
                            iaf = calculate_iaf(weight_scheme,inverse_frequency)
                            self.schema_index[table][attribute]['norm'][weight_scheme] += (tf*iaf)**2

        for table in self.schema_index:
            for attribute in self.schema_index[table]:
                for weight_scheme in range(4):
                    self.schema_index[table][attribute]['norm'][weight_scheme] **= 0.5

        self.schema_index.persist_to_file(
            self.config.dataset_directory,
            self.config.schema_index_filepath,
        )

    def load_indexes(self,**kwargs):
        schema_graph_path = self.config.dataset_directory + self.config.schema_graph_filepath
        value_index_path = self.config.dataset_directory + self.config.value_index_filepath
        schema_index_path = self.config.dataset_directory + self.config.schema_index_filepath

        self.schema_graph.load_from_file(schema_graph_path)
        self.value_index.load_from_file(value_index_path, **kwargs)
        self.schema_index.load_from_file(schema_index_path)
