from __future__ import annotations

from typing import Callable, Any, AnyStr

from .datalogger_map import DataLoggerMap


class Field(str):
    def __new__(cls, field_name: str, *args_func: object, func: Callable = None, default: object = None):
        """
        Define a Field to be used for logging data.

        Args:
            field_name: The name of the field.
            args_func: Optional arguments to pass to func.
        """

        obj = super().__new__(cls, field_name)
        obj.field_name = field_name
        obj.func = func
        obj.default = default

        if not args_func:
            args_func = tuple()
        obj.args_func = args_func
        return obj


class FieldMap(DataLoggerMap):
    @property
    def key_type(self):
        return Field

    def add(self, f: Field, v: Any):
        assert f not in self, f"Field {f} is already present in the field-map (it is mapped to {self.get(f)})"
        self.update({f: v})

    def copy(self) -> FieldMap[AnyStr, Any]:
        r = FieldMap(super(FieldMap, self).copy())
        return r
