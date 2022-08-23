from collections import namedtuple
from json import load as json_load
from pathlib import Path
import pickle

class DictToSTupleFormatter(object):

    _NAME = 'STuple'

    def format(self, dictionary):
        sorted_keys = sorted(dictionary.keys())
        sorted_values = []
        
        for key in sorted_keys:
            sorted_values.append(dictionary[key])

        formatted_keys = [
            k.split('.')[1] if '.' in k else k for k in sorted_keys
        ]

        try:
            stuple = namedtuple(
                self._NAME,
                formatted_keys,
            )
        except ValueError as e:
            keys_set = set([])
            for key in formatted_keys:
                keys_set.add(key)
            stuple = namedtuple(
                self._NAME,
                keys_set,
            )
            sorted_values = []
            for key in keys_set:
                sorted_values.append(dictionary[key])

        generated_stuple = stuple(
            *sorted_values,
        )

        return generated_stuple

class AttributeTreeGenerator(dict):
    __slots__ = ['_dict', '_single_length_attribute_tree']

    def __init__(self):
        self._dict = {}
        self._single_length_attribute_tree = []
    
    def add_attribute(self, attribute, value):
        attribute_path = attribute.split('.')
        if len(attribute_path) == 1:
            self._single_length_attribute_tree.append(('', [(attribute, value,)]))
        else:
            leaf_attribute = attribute_path[-1]
            path = '.'.join(
                attribute_path[:-1],
            )

            if path not in self._dict:
                self._dict[path] = [
                    (leaf_attribute, value),
                ]
            else:
                self._dict[path].append((leaf_attribute, value,))

    def generate(self):
        attribute_trees = []
        for root in self._dict:
            tree = (
                root,
                self._dict[root],
            )
            attribute_trees.append(tree)
        
        for tree in self._single_length_attribute_tree:
            attribute_trees.append(tree)

        return attribute_trees

    def __repr__(self):
        return self._dict

def modify_retrieved_documents(retrieved_documents):
    modified_documents = []
    while len(retrieved_documents) > 0:
        document = retrieved_documents.pop()
        if '_id' in document:
            document['mongo_id'] = str(document['_id'])
        del document['_id']
        modified_documents.append(document)

    return modified_documents

def load_schema_graph_from_json(database):
    PATH = f'./schema_graphs/{database}_schema_graph.json'
    schema_graph_file_path_exists = Path(PATH).is_file()
    schema_graph = {}

    if schema_graph_file_path_exists:
        with open(PATH) as f:
            schema_graph = json_load(f)
        return schema_graph

    return Exception("Schema Graph file not found")

def load_datasets_ids_from_json():
    PATH = f'./collections_ids/datasets_collection_ids.json'
    datasets_ids_file_exists = Path(PATH).is_file()

    if datasets_ids_file_exists:
        with open(PATH) as f:
            return json_load(f)
    
    raise Exception("Datasets collection IDs file not found")

def load_database_structure_from_file(database_name):
    PATH = f'tmp/{database_name}.pickle'
    with open(PATH, 'rb') as f:
        database_structure = pickle.load(
            f,
        )
    
    return database_structure

if __name__ == '__main__':
    from pprint import pprint as pp

    tree = AttributeTreeGenerator()
    tree.add_attribute('teams.players.player', 'jon')
    tree.add_attribute('teams.players.player', 'jon')
    tree.add_attribute('teams.players.ast', 10)
    pp(tree.generate())

