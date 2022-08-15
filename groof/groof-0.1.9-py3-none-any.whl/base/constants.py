from __future__ import annotations


class ConstantsMeta(type):

    def __getattribute__(cls: type[Constants], item):
        value = super().__getattribute__(item)

        if value is ...:
            if cls.__with_class_name__:
                return f'{cls.__name__}.{item}'
            return item

        return value


class Constants(metaclass=ConstantsMeta):
    __with_class_name__ = False
