from __future__ import annotations

import importlib
import types
import typing
from dataclasses import Field, asdict

import bson

from ..base import BaseModel

T = typing.TypeVar('T')


def is_generic_type(_type: type) -> bool:
    return hasattr(_type, '__origin__')


def get_type_origin(_type: type) -> type:
    return getattr(_type, '__origin__')


def is_union_type(_type) -> bool:
    return isinstance(_type, types.UnionType)


def get_type_args(_type: types.UnionType | type) -> list[type]:
    return list(getattr(_type, '__args__'))


def unify_type(_type: None | type | list[type] | types.UnionType) -> type | list[type]:
    if _type is None:
        return type(None)

    if is_union_type(_type):
        return [unify_type(subtype) for subtype in get_type_args(_type)]

    if isinstance(_type, list):
        return [unify_type(subtype) for subtype in _type]

    if is_generic_type(_type):
        if get_type_origin(_type) == list:
            return _type
        raise ValueError('Unsupported generic type')

    if isinstance(_type, type):
        return _type

    raise ValueError('Unsupported type')


assert unify_type(None) == type(None)
assert unify_type(str) == str
assert unify_type([str, None]) == [str, type(None)]
assert unify_type(str | None) == [str, type(None)]


def get_model_fields(_type: type[BaseModel]) -> list[Field]:
    return list(getattr(_type, '__dataclass_fields__').values())


def eval_field_type(_field: Field, cls: type[BaseModel]) -> type | types.UnionType:
    module = importlib.import_module(cls.__module__)
    _globals = vars(module) | {'bson': bson, 'typing': typing}
    return eval(_field.type, _globals)


def cast_to_model(value: dict, to_type: type[BaseModel]):
    new_value = {}

    for _field in get_model_fields(to_type):
        if isinstance(_field.type, str):
            _field.type = eval_field_type(_field, cls=to_type)

        key = to_type.__aliases__.get(_field.name, _field.name)

        if key in value:
            new_value[_field.name] = _cast(value[key], _field.type)

    # noinspection PyArgumentList
    return to_type(**new_value)


def cast_to_type(value, to_type: type):
    if value is None:
        return None
    if issubclass(to_type, BaseModel):
        if not isinstance(value, dict):
            raise ValueError
        return cast_to_model(value, to_type)
    return to_type(value)


def _cast(value, to_type: type | list[type] | types.UnionType):
    to_type = unify_type(to_type)

    if to_type == dict:
        if isinstance(value, BaseModel):
            return asdict(value, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
        raise ValueError

    if isinstance(to_type, type):
        if is_generic_type(to_type):
            if get_type_origin(to_type) == list:
                subtypes = get_type_args(to_type)
                return [_cast(i, subtypes) for i in value]

        return cast_to_type(value, to_type)

    for subtype in to_type:
        try:
            return _cast(value, subtype)
        except (ValueError, TypeError):
            pass
    else:
        raise ValueError


def cast(value, to_type: type[T] | types.UnionType) -> T:
    try:
        return _cast(value, to_type)
    except ValueError:
        raise ValueError(f'Can\'t cast {repr(value)} to {to_type}')
