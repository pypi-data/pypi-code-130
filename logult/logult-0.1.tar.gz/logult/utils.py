import requests
import json


def download_config(id):
    url = 'https://raw.githubusercontent.com/cuongngm/logult/why/config/{}'.format(id)
    r = requests.get(url)
    config = r.text
    return config


class Cfg(dict):
    def __init__(self, config_dict):
        super(Cfg, self).__init__(**config_dict)
        self.__dict__ = self

    @staticmethod
    def load_config_from_name():
        base_config = download_config('logger_config.json')
        base_config = json.loads(base_config)
        return Cfg(base_config)
