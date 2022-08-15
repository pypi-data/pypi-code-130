from dataclasses import dataclass

from .storage import Storage


@dataclass
class ContextDict:
    storage: Storage

    def __getitem__(self, item: str):
        return self.storage.data[item]

    def __setitem__(self, key: str, value):
        self.storage.data[key] = value
        self.storage.save()

    def __delitem__(self, key: str):
        del self.storage.data[key]
        self.storage.save()

    def __contains__(self, key: str):
        return key in self.storage.data

    def get(self, item: str, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def setdefault(self, key: str, default):
        self.storage.data.setdefault(key, default)
        self.storage.save()

    def clear(self):
        self.storage.data.clear()
        self.storage.save()
