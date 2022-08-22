from __future__ import annotations
from abc import ABC, abstractmethod
import types
from .abstract import AArchitect
from typing import Any

func_types = (
    types.FunctionType,
    types.BuiltinMethodType,
    types.BuiltinFunctionType,
    types.MethodType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType,
    types.MethodWrapperType,
    types.WrapperDescriptorType,
    types.GetSetDescriptorType,
    types.MemberDescriptorType,
)

class CoreArchitect(AArchitect):
    def parse(self, var: Any, parse_as: str = "object", *, metadata: dict | None = None):
        if parse_as == "object":
            return self.parse_object(var, metadata=metadata)
        elif parse_as == "attr":
            return self.parse_attr(var, metadata=metadata)
        elif self.next is not None:
            return self.next.parse(var, parse_as, metadata=metadata)
        return None

    def parse_object(self, var: Any, *, metadata: dict | None = None):
        if self.e is None:
            return None

        id_ = id(var)

        # Check if already parsed
        if id_ in self.e.maze.objects:
            return {"id": id_, "mode": "object"}

        obj: dict = {}
        self.e.maze.objects[id_] = obj

        try:
            obj["name"] = var.__name__
        except:
            pass
        
        try:
            obj["qualname"] = var.__qualname__
        except:
            pass

        try:
            obj["module"] = var.__module__
        except:
            pass
        
        try:
            obj["class"] = id(var.__class__)
            self.e.parse(var.__class__, "object")
        except:
            pass

        try:
            obj["mro"] = []
            for i in var.__mro__:
                obj["mro"].append(id(i))
                self.e.parse(i, "object")
        except:
            del obj["mro"]

        try:
            obj["bases"] = []
            for i in list(var.__bases__):
                obj["bases"].append(id(i))
                self.e.parse(i, "object")
        except:
            del obj["bases"]

        try:
            d = var.__dict__
            obj["dict"] = {}
            for i in d:
                res = self.e.parse(d[i], "attr", metadata={"object": var, "attr": i})
                if res is not None:
                    obj["dict"][i] = res
        except:
            pass

        return {"id": id_, "mode": "object"}

    def parse_attr(self, var: Any, *, metadata: dict | None = None):
        id_ = id(var)
        if self.e is None or self.e.maze is None:
            return

        maze = self.e.maze
        try:
            if type(var) in func_types:
                return {"mode": "func", "type": type(var).__name__, "id": id_}
            elif type(var) == str:
                maze.strings[id_] = var
                return {"mode": "str", "type": "str", "id": id_}
            elif type(var) in (int, float):
                return {"mode": "dir", "type": type(var).__name__, "val": var}
            elif var is None:
                return {"mode": "dir", "type": "NoneType", "val": "None"}
            elif type(var) == bool:
                return {"mode": "dir", "type": "bool", "val": str(var)}
            elif type(var) in (list, set, frozenset, tuple):
                if id_ not in maze.lists:
                    maze.lists[id_] = {"type": type(var).__name__, "items": []}
                    for i in var:
                        maze.lists[id_]["items"].append(self.e.parse(i, "attr"))
                return {"mode": "list", "type": type(var).__name__, "id": id_, "len": len(var)}
            elif type(var) == dict:
                if id_ not in maze.dicts:
                    maze.dicts[id_] = {"type": type(var).__name__, "items": []}
                    for (i, j) in var.items():
                        maze.dicts[id_]["items"].append( (
                            self.e.parse(i, "attr"),
                            self.e.parse(j, "attr"),
                        ) )
                return {"mode": "dict", "type": type(var).__name__, "id": id_, "len": len(var)}
            else:
                return self.parse_object(var)
        except:
            import traceback
            traceback.print_exc()
            return None
