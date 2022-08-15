# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import json
import pandas as pd
from suanpan import g
from suanpan.log import logger
from suanpan.storage import storage
from suanpan.utils.tools import safeMkdirsForFile


class Arg:

    def __init__(self, key, alias=None, default=None):
        self.key = key
        self.alias = alias
        self.default = default

    def getValue(self, func, value):
        return func(value) if value is not None else self.default

    def context(self, func, value, action):
        value = self.getValue(func, value)
        self.log(action, value)
        return {
            self.key: value,
            self.alias: value
        } if self.alias else {
            self.key: value
        }

    def logKeyAlias(self):
        return self.key if self.alias is None else f"{self.key}({self.alias})"

    def log(self, action, value):
        logger.debug(f"Argument: {self.logKeyAlias()} {action}ed: {value}")


class String(Arg):

    def load(self, value):
        return self.context(str, value, "load")

    def dump(self, value, **kwds):
        return self.context(str, value, "dump")


class Json(Arg):

    def load(self, value):
        return self.context(json.loads, value, "load")

    def dump(self, value, **kwds):
        return self.context(json.dumps, value, "dump")


class Int(Arg):

    def load(self, value):
        return self.context(int, value, "load")

    def dump(self, value, **kwds):
        return self.context(int, value, "dump")


class Float(Arg):

    def load(self, value):
        return self.context(float, value, "load")

    def dump(self, value, **kwds):
        return self.context(float, value, "dump")


class Csv(Arg):

    def read_csv(self, value):
        safeMkdirsForFile(storage.getPath(g.tempStore, value, "data.csv"))
        storage.download(storage.getPath(value, "data.csv"),
                         storage.getPath(g.tempStore, value, "data.csv"))
        return pd.read_csv(storage.getPath(g.tempStore, value, "data.csv"),
                           index_col=0)

    def save_csv(self, result):
        path = result["path"]
        value = result["value"]
        safeMkdirsForFile(storage.getPath(g.tempStore, path, "data.csv"))
        value.to_csv(storage.getPath(g.tempStore, path, "data.csv"))
        storage.upload(storage.getPath(path, "data.csv"), storage.getPath(g.tempStore, path, "data.csv"))
        return path

    def load(self, value):
        return self.context(self.read_csv, value, "load")

    def dump(self, value, requestId=None, **kwds):
        result = {
            "path":
            storage.getPath("studio", g.userId, "tmp", g.appId, requestId,
                            g.nodeId, self.key.replace("outputData", "out")),
            "value":
            value
        }
        return self.context(self.save_csv, result, "dump")
