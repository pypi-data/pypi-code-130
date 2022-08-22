from copy import deepcopy
import shelve
import pickle


class SchemaIndex():
    def __init__(self):
        self._dict = {}

    def __iter__(self):
        yield from self._dict.keys()

    def __getitem__(self,word):
        return self._dict[word]

    def __setitem__(self,key,value):
        self._dict[key] = value

    def __repr__(self):
        return repr(self._dict)

    def __str__(self):
        return str(self._dict)

    def keys(self):
        yield from self.__iter__()

    def items(self):
        for key in self.__iter__():
            yield key, self.__getitem__(key)

    def values(self):
        for key in self:
            yield self[key]

    def create_entries(self,table_attributes,metrics):
        if type(table_attributes) == list:
            for table,attributes in table_attributes:
                self._dict.setdefault(table,{})
                for attribute in attributes:
                    self._dict[table].setdefault(attribute, deepcopy(metrics) )
        elif type(table_attributes) == dict:
            for table,attributes in table_attributes.items():
                self._dict.setdefault(table,{})
                for attribute in attributes:
                    self._dict[table].setdefault(attribute, deepcopy(metrics) )

    def tables_attributes(self, database_name, nested_structures=False):
        collection_structure_path = ''.join([
                'tmp/',
                database_name + '.pickle'
            ]
        )
        
        with open(collection_structure_path, 'rb') as f:
            collection_structure = pickle.load(
                f,
            )
        
        tables_attributes_set = set([])
        for table in self:
            for attribute in self[table]:
                if nested_structures:
                    tables_attributes_set.add((table, attribute))
                else:
                    if not collection_structure[table][attribute] in [type(dict()), type(list())]:
                        tables_attributes_set.add((table, attribute))

        return tables_attributes_set

    def get_num_total_attributes(self):
        return sum([len(attribute) for attribute in self.values()])

    def persist_to_file(self, file_directory, filename):
        filepath = file_directory + filename
        with shelve.open(filepath) as storage:
            for key,value in self._dict.items():
                storage[key]=value

    def load_from_file(self, filename):
        with shelve.open(filename,flag='r') as storage:
            for key,value in storage.items():
                self[key]=value
