from .models.model import ClientModel
import json

# create a base class for the cache client
class CacheClient(ClientModel):
    '''cache client is a client model that is used to store data in a cache file'''
    def __init__(self, cacheFileFullPath, *args, force=False, **kwargs):
        self.cacheFileFullPath = cacheFileFullPath
        try:
            self.dict = self.__loads()
        except FileNotFoundError as err:
            if not force:
                raise Exception("Cache file not found") from err
            else:
                self.save({})
                self.dict = self.__loads()
        super().__init__(self.dict, *args, **kwargs)

    def __loads(self):
        return json.loads(open(self.cacheFileFullPath, encoding='utf8').read())

    def save(self, data:dict):
        open(self.cacheFileFullPath, 'w', encoding='utf8').write(
            self.dumps(data)
        )

    def dumps(self, data:dict, indent=4, sort_keys=False):
        return json.dumps(data, indent=indent, sort_keys=sort_keys)

    def set(self, key:str, value:str):
        self.dict[key] = value
        self.save(self.dict)
