import json
import logging
import os


class Cache:
    _LOGGER = logging.getLogger()
    _LOGGER.setLevel(logging.INFO)

    def __init__(self, name, cache_base_path=None):
        if cache_base_path is None:
            cache_base_path = '/tmp'
        self._cache_path = os.path.join(cache_base_path, f"{name}.json")
        self._LOGGER.info(f"Creating cache at {self._cache_path}")
        try:
            with open(self._cache_path) as cache_file:
                self.cache = json.load(cache_file)
        except IOError:
            self._LOGGER.info("No cache available. Creating empty one.")
            self.cache = {}
            os.makedirs(cache_base_path, exist_ok=True)

    @property
    def cache_path(self):
        return self._cache_path

    def get_all(self):
        return self.cache

    def set_all(self, keys_with_values):
        for key in keys_with_values:
            self.set(key, keys_with_values[key])

    def get(self, key):
        return self.cache.get(key, None)

    def set(self, key, value):
        self.cache[key] = value
        with open(self._cache_path, 'w') as cache_file:
            json.dump(self.cache, cache_file)

    def delete_all(self):
        self.cache = {}
        with open(self._cache_path, 'w') as cache_file:
            json.dump(self.cache, cache_file)
