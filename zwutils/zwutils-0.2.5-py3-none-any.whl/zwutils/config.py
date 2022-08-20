# -*- coding: utf-8 -*-
import os
import json
import codecs
from pathlib import Path

class Config():
    def __init__(self, fp=None, default=None):
        self.path = fp
        self.data = default or {}
        if self.path is not None and not os.path.isfile(self.path):
            self.save()
        self.load()

    def load(self):
        if self.path:
            with codecs.open(self.path, 'r', 'utf-8') as f:
                kv = json.load(f)
                for key, val in kv.items():
                    self.data[key] = val
        return self

    def save(self):
        if not Path(self.path).parent.exists():
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with codecs.open(self.path, 'w', 'utf-8') as f:
            json.dump(self.data, f, sort_keys=True, indent=4, separators=(',', ': '))
    
    def set(self, key, val):
        self.data[key] = val
    
    def get(self, key, default):
        return self.data[key] if key in self.data else default

    def __getattr__(self, key):
         # Support for attr-based lookup.
        try:
            return self.data[key]
        except KeyError as e:
            raise AttributeError(e)

    def __delattr__(self, key):
        try:
            del self.data[key]
        except KeyError as e:
            raise AttributeError(e)
    
    def __contains__(self, key):
        return key in self.data