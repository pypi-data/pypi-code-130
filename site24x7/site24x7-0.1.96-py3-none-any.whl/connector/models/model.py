from abc import ABC, abstractmethod
from ...utils.util import validatePluginData, guessMetricByType

class ClientModel(ABC):
    '''
        date_created is a string in the format of MMM DDDD, YYYY
            example: Aug 18th, 2022
        match_list is a list of strings that are used to match the keys in the dict
            example: ['Fabletics', 'Yitty']
    '''
    def __init__(self, _dict=None, author=None, plugin_version=None, heartbeat_required=None, date_created=None, match_list=None):
        self.dict = {}
        self.author = author
        self.__setitem__('author', self.author)
        self.plugin_version = plugin_version
        self.__setitem__('plugin_version', self.plugin_version)
        self.heartbeat_required = heartbeat_required
        self.__setitem__('heartbeat_required', self.plugin_version)
        self.date_created = date_created
        self.__setitem__('date_created', self.date_created)
        if match_list:
            for key in _dict.keys():
                for i in match_list:
                    if i.lower() in key.lower():
                        self.__setitem__(key, _dict[key])
        else:
            self.dict.update(_dict)

    def __getitem__(self, key):
        return self.dict[key]
    def __setitem__(self, key, value):
        self.dict[key] = value
    def __delitem__(self, key):
        del self.dict[key]
    def __contains__(self, key):
        return key in self.dict
    def __len__(self):
        return len(self.dict)
    def __iter__(self):
        return iter(self.dict)
    def __legthCheck__(self, str:str):
        # string limit is 20 on site24x7 plugin dashboard
        if len(str) > 20:
            raise Exception("String length is greater than 20")

    def setAuthor(self, author:str):
        self.__legthCheck__(author)
        self.author = author
        self.__setitem__('author', self.author)

    def setPluginVersion(self, plugin_version:int):
        self.__legthCheck__(plugin_version)
        self.plugin_version = plugin_version
        self.__setitem__('plugin_version', self.plugin_version)

    def setHeartbeatRequired(self, heartbeat_required:bool):
        self.__legthCheck__(heartbeat_required)
        self.heartbeat_required = heartbeat_required
        self.__setitem__('heartbeat_required', self.heartbeat_required)
    
    def setDateCreated(self, date_created:str):
        self.__legthCheck__(date_created)
        self.date_created = date_created
        self.__setitem__('date_created', self.date_created)

    def validate(self):
        validatePluginData(self.dict)
    
    def set_metric_types(self):
        self.validate()
        metric_units = guessMetricByType({}, self.dict)
        self.__setitem__('units', metric_units)
