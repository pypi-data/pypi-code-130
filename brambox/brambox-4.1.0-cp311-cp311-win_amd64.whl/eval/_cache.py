#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Caching class for eval package
#

__all__ = ['Cache']


class Cache:
    def __init__(self, *fields):
        self.fields = set(fields)
        self.values = {}

    def __contains__(self, name):
        if name not in self.fields:
            raise ValueError(f'Uncached value: {name}')
        return name in self.values

    def __getitem__(self, name):
        if name not in self.fields:
            raise ValueError(f'Uncached value: {name}')
        return self.values.get(name, None)

    def __setitem__(self, name, value):
        if name not in self.fields:
            raise ValueError(f'Uncached value: {name}')
        self.values[name] = value

    def __len__(self):
        return len(self.values)

    def reset(self):
        self.values = {}
