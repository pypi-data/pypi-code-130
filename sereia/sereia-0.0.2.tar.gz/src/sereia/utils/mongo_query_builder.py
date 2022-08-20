import pickle
from pprint import pprint as pp

from sereia.config.config import DefaultConfiguration

class MongoQueryBuilder:

    PROJECT_STEP_FIELD = '$project'
    MATCH_STEP_FIELD = '$match'
    LOOKUP_STEP_FIELD = '$lookup'
    ADD_FIELDS_STEP_FIELD = '$addFields'
    FILTER_STEP_FIELD = '$filter'
    COUNT_STEP_FIELD = '$count'
    UNWIND_STEP_FIELD = '$unwind'
    SET_STEP_FIELD = '$set'
    EXPRESSION_FIELD = '$expr'
    GROUP_STEP_FIELD = '$group'
    FIRST_FIELD = '$first'

    def __init__(self, database_name):
        self.query_steps = []
        self._last_added_step = None
        self._starting_collection = None
        self._last_collection_lookup = None
        self.database_name = database_name
        # self.collection_name = DefaultConfiguration.COLLECTION_NAME
        self.collection_structure = self._load_collection_structure(
            self.database_name,
        )
        self._top_level_attributes = self._extract_top_level_attributes()

    def set_starting_collection(self, collection):
        self._starting_collection = collection

    def get_starting_collection(self, collection):
        return self._starting_collection

    def _load_collection_structure(self, collection):
        collection_structure_path = ''.join([
                DefaultConfiguration.TEMP_FILES_PATH,
                collection + '.pickle',
            ]
        )
        
        with open(collection_structure_path, 'rb') as f:
            collection_structure = pickle.load(
                f,
            )
        
        return collection_structure
    
    def _extract_top_level_attributes(self):
        top_level_attributes = []
        for attribute in self.collection_structure:
            if '.' not in attribute:
                top_level_attributes.append(
                    attribute,
                )

    def project(self, fields):
        project_fields = {}
        if type(fields) == list:
            for field in fields:
                project_fields[field] = 1
        
        project_clause = {
            self.PROJECT_STEP_FIELD: project_fields,
        }

        self.query_steps.append(project_clause)

    def _squash_project(self, fields):
        for field in fields:
            self.query_steps[-1][field] = 1

    def _regex_match(self, field_name, field_value, from_filter=None):
        if from_filter:
            input_name = field_name
        else:
            input_name = ''.join(['$', field_name])
        return {
            '$regexMatch': {
                'input': input_name,
                'regex': field_value,
                'options': 'i'
            }
        }

    def _group(self, collection):
        
        group_step = {
            self.GROUP_STEP_FIELD: {
                '_id': self._to_mongo_attribute_name('_id'),
            },
        }

        for path in self.collection_structure[collection]:
            if '.' not in path:
                group_step[
                    self.GROUP_STEP_FIELD
                ][
                    path
                ] = {
                    self.FIRST_FIELD: self._to_mongo_attribute_name(path)
                }
        
        self.query_steps.append(group_step)

    def _get_aliased_path(self, field_name, aliased_dict):
        aliased_path = field_name
        for aliased_field, aliased_field_name in aliased_dict.items():
            aliased_path = aliased_path.replace(
                aliased_field,
                aliased_field_name,
            )
        
        return aliased_path

    def _append_attribute_to_path(self, path, attribute):
        if attribute:
            return '.'.join(
                [
                    path,
                    attribute
                ]
            )
        return attribute
    
    def _get_attribute_type(self, collection, attribute):
        return self.collection_structure[
            collection
        ][attribute]

    def new_match_v3(self, collection, attribute_matches):
        alias_dict = {}

        for attribute_path, matches in attribute_matches:
            path = attribute_path.split('.')
            last_attribute = None
            unwind_stage = []

            for attribute in path:

                if not attribute:
                    continue

                if last_attribute:
                    attribute = self._append_attribute_to_path(
                        last_attribute, 
                        attribute,
                    )

                attribute_type = self._get_attribute_type(
                    collection, 
                    attribute,
                )

                if attribute_type == list:
                    if not unwind_stage and \
                    not self._check_for_list_in_parent_attributes(
                        collection, 
                        attribute, 
                        path, 
                        alias_dict
                    ):
                        field_name, set_stage = self._copy_field(
                            attribute,
                        )

                        unwind_stage.append(
                            set_stage,
                        )

                        alias_dict[attribute] = field_name

                    aliased_attribute = self._get_aliased_path(
                        attribute, 
                        alias_dict,
                    )

                    unwind_stage.append(
                        self.unwind(
                            aliased_attribute,
                        )
                    )
         
                last_attribute = attribute

            for attribute, value in matches:
                if last_attribute:
                    attribute = self._append_attribute_to_path(
                        last_attribute,
                        attribute,
                    )

                attribute_type = self._get_attribute_type(
                    collection, 
                    attribute,
                )

                aliased_attribute = self._get_aliased_path(
                    attribute, 
                    alias_dict,
                )

                if collection != self._starting_collection:
                    aliased_attribute = self._append_attribute_to_path(
                        collection,
                        aliased_attribute,
                    )

                if attribute_type == str:
                    # print('Found froze: {}'.format(value))
                    if isinstance(value, frozenset):
                        self.query_steps.extend(
                            unwind_stage,
                        )
                        for term in value:
                            self._generate_string_match_stage(
                                aliased_attribute, 
                                term,
                                collection=collection,
                            )
                    else:
                        self._generate_string_match_stage(
                            aliased_attribute,
                            value,
                            collection=collection,
                            unwind_stage=unwind_stage,
                        )
                elif attribute_type in [int, float]:
                    self._generate_numeric_match_stage(
                        aliased_attribute, 
                        value,
                        collection=collection,
                        unwind_stage=unwind_stage,
                    )
                elif attribute_type == list:
                    field_name, set_stage = self._copy_field(
                        attribute,
                    )

                    unwind_stage.append(
                        set_stage,
                    )

                    self.query_steps.extend(
                        unwind_stage,
                    )

                    alias_dict[attribute] = field_name

                    aliased_attribute = self._get_aliased_path(
                        attribute, 
                        alias_dict,
                    )

                    self._generate_string_match_stage(
                        aliased_attribute, 
                        value,
                        collection=collection,
                        unwind_stage=[self.unwind(
                            aliased_attribute,
                        )])

    def _check_for_list_in_parent_attributes(self, collection, attribute, parent_attributes, alias_dict):
        for parent_attribute in parent_attributes:
            if parent_attribute == attribute:
                break
        
            if self._get_attribute_type(
                collection, 
                parent_attribute,
            ):
                return True
            
        return False

    def _generate_string_match_stage(self, attribute, value, collection=None, unwind_stage=None):
        if unwind_stage:
            self.query_steps.extend(
                unwind_stage,
            )

        self._match_string(
            attribute,
            value,
        )

        if unwind_stage:
            if not collection:
                raise TypeError('Missing parameter: collection')

            self._group(
                collection,
            )

    def _generate_numeric_match_stage(self, attribute, value, collection=None, unwind_stage=None):
        if unwind_stage:
            self.query_steps.extend(
                unwind_stage,
            )

        self._match_number(
            attribute,
            value,
        )

        if unwind_stage:
            if not collection:
                raise TypeError('Missing parameter: collection')

            self._group(
                collection,
            )

    def _match_string(self, field_name, field_value):
        self.query_steps.append(
            {
                self.MATCH_STEP_FIELD: {
                    self.EXPRESSION_FIELD: self._regex_match(
                        field_name,
                        field_value,
                    )
                }
            }
        )
    
    def _match_number(self, field_name, field_value):
        new_field_value = None
        if '.' in field_value:
            new_field_value = float(field_value)
        else:
            new_field_value = int(field_value)
        self.query_steps.append(
            {
                self.MATCH_STEP_FIELD: {
                    self.EXPRESSION_FIELD: {
                        '$eq': [
                            ''.join(self._to_mongo_attribute_name(field_name)),
                            new_field_value,
                        ]
                    }
                }
            }
        )

    def _to_mongo_attribute_name(self, field_name):
        return '$' + field_name

    def _copy_field(self, field_name):
        dup_field_name = field_name + '_dup'
        return (dup_field_name, {
            self.SET_STEP_FIELD: {
                dup_field_name: self._to_mongo_attribute_name(field_name)
            }
        })

    def unwind(self, field_name, insert=False):
        if insert:
            self.query_steps.append(
                {
                    self.UNWIND_STEP_FIELD: self._to_mongo_attribute_name(field_name)
                }
            )

        return {
            self.UNWIND_STEP_FIELD: self._to_mongo_attribute_name(field_name)
        }

    def lookup(self, local_field, foreign_field,
               foreign_collection, alias):

        lookup_clause = {
            self.LOOKUP_STEP_FIELD: {
                'from': foreign_collection,
                'foreignField': foreign_field,
                'localField': local_field,
                'as': alias
            }
        }

        self.query_steps.append(lookup_clause)
        self._last_added_step = self.LOOKUP_STEP_FIELD
        self._last_collection_lookup = foreign_collection

    def count_documents(self):
        count_clause = {
            self.COUNT_STEP_FIELD: 'count'
        }
        self.query_steps.append(count_clause)

    def build(self):
        return (self._starting_collection, self.query_steps)
