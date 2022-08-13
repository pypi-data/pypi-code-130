"""Module with base dataclass with validations."""

import collections
import copy
import dataclasses
import sys
import typing

from aiojsonapi import exception


class TypedList(collections.UserList):
    """List with validation that every item have same type."""

    def __init__(self, items_type, iterable=()):
        self.items_type = items_type
        for item_n, item in enumerate(copy.copy(iterable)):
            if isinstance(item, int) and issubclass(self.items_type, int):
                iterable[item_n] = self.items_type(item)
            elif not isinstance(item, self.items_type):
                raise ValueError(f"Wrong item type {type(item)}.")
        super().__init__(iterable)

    def append(self, item) -> None:
        if not isinstance(item, self.items_type):
            raise ValueError("Wrong item type.")
        return super().append(item)

    def insert(self, i: int, item) -> None:
        if not isinstance(item, self.items_type):
            raise ValueError("Wrong item type.")
        return super().insert(i, item)

    def __add__(self, other):
        if isinstance(other, (TypedList, self.items_type)):
            return super().__add__(other)
        raise ValueError("Wrong item type.")


@dataclasses.dataclass
class BaseDataclass:
    """Base dataclass for requests validations. Subclassed on JSON template creation."""

    @property
    def _fields(self):
        return {field.name: field for field in dataclasses.fields(self)}

    def _get_field(self, field_name):
        return self._fields[field_name]

    @staticmethod
    def _ensure_special_container(field, field_value):
        if not isinstance(field_value, (list, set, TypedList)):
            raise ValueError(f"Wrong value type for {field.name}.")
        items_type = field.type.__args__[0]
        if issubclass(items_type, typing.List):
            field_value = TypedList(items_type, field_value)
        else:
            for item_n, item in enumerate(field_value.copy()):
                if isinstance(item, items_type):
                    field_value[item_n] = item
                else:
                    field_value[item_n] = items_type(item)
        return field_value

    @staticmethod
    def _ensure_special_dict(field, field_value):
        if not isinstance(field_value, dict):
            raise ValueError(f"Wrong value type for {field.name}.")
        k_type, v_type = field.type.__args__
        new_dict = {}
        for key, value in field_value.items():
            new_dict[k_type(key)] = v_type(value)
        return new_dict

    @classmethod
    def ensure_field_value(cls, field, field_value):  # pylint: disable=too-many-return-statements
        """Ensures that value matches provided typehint."""

        if field.default is None and field_value is None:
            return None
        if (
            isinstance(field.type, type)
            and issubclass(field.type, BaseDataclass)
            and isinstance(field_value, dict)
        ):
            return field.type(**field_value)
        if isinstance(field.type, typing._GenericAlias):  # pylint: disable=protected-access
            if typing.get_origin(field.type) in [list, set, frozenset]:
                return cls._ensure_special_container(field, field_value)
            if typing.get_origin(field.type) is dict:
                return cls._ensure_special_dict(field, field_value)
            if typing.get_origin(field.type) is typing.Union:
                if not isinstance(field_value, typing.get_args(field.type)):
                    raise ValueError(f"Wrong value type for {field.name}.")
                return field_value
        if isinstance(field_value, field.type):
            return field_value
        try:
            return field.type(field_value)
        except TypeError:
            raise exception.WrongDataType(field.name) from None

    def __post_init__(self):
        for (
            field_name,
            field,
        ) in self.__class__.__dataclass_fields__.items():  # pylint: disable=no-member
            setattr(
                self,
                field_name,
                self.ensure_field_value(field, getattr(self, field_name)),
            )

    def __setattr__(self, key, value):
        if key in self._fields:
            field = self._get_field(key)
            return super().__setattr__(key, self.ensure_field_value(field, value))
        raise AttributeError()

    def to_dict(self):
        """Returns dictionary representation of dataclass."""

        def convert_object(value):
            if isinstance(value, dict):
                return custom_data_types_dict_factory(value.items())
            if isinstance(value, (list, set, frozenset, tuple)):
                result = []
                for item in value:
                    result.append(convert_object(item))
                return type(value)(result)
            return value

        def custom_data_types_dict_factory(key_value_tuple):
            result = {}
            for key, value in key_value_tuple:
                if key.startswith("__"):
                    continue
                result[key] = convert_object(value)
            return result

        return dataclasses.asdict(self, dict_factory=custom_data_types_dict_factory)

    @classmethod
    def update_forward_refs(cls, **localns):
        """Updates references from locals."""

        globalns = sys.modules[cls.__module__].__dict__.copy()
        globalns.setdefault(cls.__name__, cls)
        for field in cls.__dataclass_fields__.values():  # pylint: disable=no-member
            cls._update_field_forward_refs(field, globalns=globalns, localns=localns)

    @staticmethod
    def _update_field_forward_refs(
        field: "ModelField", globalns: typing.Any, localns: typing.Any
    ) -> None:
        """
        Try to update ForwardRefs on fields based on this ModelField, globalns and localns.
        """

        if field.type.__class__ == typing.ForwardRef:
            eval_type = field.type._eval_type  # pylint: disable=protected-access
            field.type = eval_type(globalns, localns) or None
            field.prepare()
        elif field.type.__class__ == str:
            field.type = eval(field.type, globalns, localns)  # pylint: disable=eval-used

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def cut_unknown(cls, data: dict):
        """Removes unknown keys from JSON data."""

        result = {}
        fields = {field.name: field for field in dataclasses.fields(cls)}
        for key, value in data.items():
            if key in fields and isinstance(fields[key], BaseDataclass):
                result[key] = fields[key].cut_unknown(value)
            elif key in fields:
                result[key] = value
        return result
