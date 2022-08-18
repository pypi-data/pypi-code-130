from abc import ABC, abstractmethod
import json

# create a base class for the cache client
class CacheClient(ABC):
    def __init__(self, cacheFileFullPath, force=False):
        self.cacheFileFullPath = cacheFileFullPath
        try:
            self.dict = self.__loads()
        except Exception as e:
            if not force:
                print(e)
                raise Exception("Cache file not found")
            else:
                self.save({})
    
    def __loads(self):
        return json.loads(open(self.cacheFileFullPath).read())

    def save(self, data:dict):
        open(self.cacheFileFullPath, 'w').write(
            self.dumps(data)
        )
    
    def dumps(self, data:dict, indent=4, sort_keys=False):
        return json.dumps(data, indent=4, sort_keys=False)

    def set(self, key, value):
        self.dict[key] = value
        self.save(self.dict)