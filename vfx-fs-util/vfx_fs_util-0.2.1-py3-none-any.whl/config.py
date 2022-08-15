import os
import json


__FILE_DIR = os.path.dirname(__file__)
__FORMAT_CONFIG = os.path.join(__FILE_DIR, 'config.json')


CONFIG = {}
ITERATION_KEY = 'iteration_formats'
COMPRESSED_FILEPATH_TYPES_KEY = 'compressed_filepath_types'


if os.path.exists(__FORMAT_CONFIG):
    with open(__FORMAT_CONFIG) as f:
        try:
            CONFIG = json.loads(f.read())
        except:
            pass


ITERATION_FORMATTING = CONFIG.get(ITERATION_KEY, {})
COMPRESSED_FILEPATH_TYPES = CONFIG.get(COMPRESSED_FILEPATH_TYPES_KEY, {})
