import datetime
from collections import namedtuple

Call = namedtuple("Call", ["result", "datetime"])


class CallsCache:
    def __init__(self, timeout=3):
        self.calls = {}
        self.timeout = timeout

    def add_call(self, key, value):
        self.calls[key] = Call(result=value, datetime=datetime.datetime.now())

    def search_call(self, key):
        result = self.calls.get(key)
        if result:
            time_now = datetime.datetime.now()
            if (time_now - result.datetime).seconds > self.timeout:
                self.remove_call(key)
                return
            return result.result
        else:
            return

    def remove_call(self, key):
        self.calls.pop(key)

    def clear_cache(self):
        self.calls = {}
