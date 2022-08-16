import re

import pandas as pd


@pd.api.extensions.register_dataframe_accessor("aa")
class AttributeAccessor:
    _RENAME_REGEX = re.compile(r"[^A-Za-z0-9 ]+", re.IGNORECASE)

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._generate_accessor_properties(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        # No validation for now
        pass

    def _generate_accessor_properties(self, panda_obj):
        def _rename(name) -> str:
            return AttributeAccessor._RENAME_REGEX.sub("", name)

        # Find space free name, without conflict
        col_names = [_rename(name) for name in list(panda_obj.columns)]
        assert len(set(col_names)) == len(col_names)

        # Generate properties
        def _fget(self, obj, col_name):
            return obj[col_name]

        def _fset(self, obj, col_name, value):
            obj[col_name] = value

        def _fdel(self, obj, col_name):
            del obj[col_name]

        [setattr(self, name, property(_fget, _fset, _fdel)) for name in col_names]
