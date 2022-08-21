import json
import logging
import re
from glob import glob
from pprint import pprint as pp


debug_mapping = { \
	'DEBUG' : logging.DEBUG,\
	'INFO': logging.INFO, \
	'ERROR': logging.ERROR, \
	'WARNING': logging.WARNING, \
	'CRITICAL': logging.CRITICAL \
}

class ConfigHandler:
    __instance = None

    config_folder_directory = None
    connection = {}
    logging_mode = None
    create_index = None
    results_directory = None
    plots_directory = None
    queryset_config_filepath = None
    dataset_config_filepath = None
    queryset_filepath = None
    queryset_name = None
    attributes_filepath = None
    schema_index_filepath = None
    value_index_filepath = None
    schema_graph_filepath = None

    def __init__(self, config_directory, reset=False, **kwargs):

        if ConfigHandler.__instance is None or reset:
            config_folder_directory = config_directory
            general_config_file = f'{config_folder_directory}config.json'

            config = self.load_config(general_config_file)
            config['logging_mode'] = debug_mapping[config['logging_mode']]

            if 'queryset_config_filepath' in kwargs:
                config['queryset_config_filepath'] = kwargs['queryset_config_filepath']

            queryset_config = self.load_config(config['queryset_config_filepath'])

            if 'dataset_config_filepath' in kwargs:
                queryset_config['dataset_config_filepath'] = kwargs['dataset_config_filepath']         

            dataset_config = self.load_config(queryset_config['dataset_config_filepath'])

            config['connection']['database'] = dataset_config['database']
            del dataset_config['database']

            ConfigHandler.__instance = config
            ConfigHandler.__instance.update(queryset_config)
            ConfigHandler.__instance.update(dataset_config)
        
        # from pprint import pprint as pp
        # pp(ConfigHandler.__instance)

        self.__dict__ = ConfigHandler.__instance

    def update_paths(self, config, prefix_directory):
        re_path = re.compile(".+(_filepath|_directory)")
        for key in config:
            #keys that contains path info and are not None
            if config[key] and re_path.match(key):
                config[key] = config[key]
                # config[key]=prefix_directory+config[key]

    def load_config(self, filepath):
        with open(filepath, 'r') as f:
            config = json.load(f)
        return config

    def set_logging_level(self, ĺevel):
        self.logging_mode = debug_mapping[ĺevel]
        ConfigHandler.__instance['logging_mode'] = self.logging_mode

    def get_dataset_configs(self):
        subfolder = './datasets_config/'
        results = []
        for filepath in glob(f'{self.config_folder_directory}{subfolder}*.json'):
            with open(filepath,'r') as f:
                results.append( (json.load(f)['database'], filepath) )
        return results

    def get_queryset_configs(self,dataset_config_filepath=None):
        subfolder = './querysets_config/'
        results = []
        for filepath in glob(f'{self.config_folder_directory}{subfolder}*.json'):
            with open(filepath,'r') as f:
                data = json.load(f)
                if dataset_config_filepath in (None,data['dataset_config_filepath']):
                    results.append( (data['queryset_name'], filepath) )
        return results
