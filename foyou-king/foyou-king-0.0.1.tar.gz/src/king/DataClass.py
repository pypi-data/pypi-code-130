from dataclasses import dataclass, is_dataclass

from typing_extensions import get_type_hints, ClassVar, get_args, get_origin


@dataclass
class DataClass:
    _HINTS: ClassVar[dict] = {}

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def _get_hints(cls) -> dict:
        hints = cls._HINTS.get(cls)
        if hints:
            return hints
        hints = get_type_hints(cls)
        cls._HINTS[cls] = hints
        return hints

    @classmethod
    def fill_dataclass(cls, obj, debug=False):
        hints = cls._get_hints()
        params = {}
        for key, value in obj.items():
            if key in hints:
                params[key] = value
            elif debug:
                print(f'MISSING_ATTRS. {cls.__module__}.{cls.__name__}'
                      f'({key} : {type(value).__name__} = {repr(value)[:100]})')
        return cls(**params)

    @staticmethod
    def _null_list(cls, may_null):
        if may_null:
            if isinstance(may_null[0], dict):
                return [cls.fill_dataclass(item) for item in may_null]
            else:
                return may_null
        else:
            return []

    @staticmethod
    def _null_dict(cls, may_null):
        if may_null is None:
            return None
        if isinstance(may_null, dict):
            return cls.fill_dataclass(may_null)
        return may_null

    def __post_init__(self):
        """自动 post_init"""
        hints = self._get_hints()
        for attr_name, type_class in hints.items():
            origin = get_origin(type_class)
            if origin is None:
                if is_dataclass(type_class):
                    setattr(self, attr_name, DataClass._null_dict(type_class, getattr(self, attr_name)))
                    continue
            for hint_type in get_args(type_class):
                if is_dataclass(hint_type):
                    if origin is list:
                        setattr(self, attr_name, DataClass._null_list(hint_type, getattr(self, attr_name)))
                    break
