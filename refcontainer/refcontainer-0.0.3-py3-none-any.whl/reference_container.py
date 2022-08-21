# std
from dataclasses import dataclass
from typeguard import check_type
# local
from .strong_generic import T, StrongGeneric, _set_type_constrainst


class ReadOnlyError(TypeError):
    pass


@dataclass
class Ref(StrongGeneric[T]):
    def __init__(self, value: T = ...):  # type: ignore
        self.__is_read_only = False
        try:
            self._type_constraints()
        except AttributeError:
            if value is Ellipsis:
                raise TypeError('Ref value type must be specified either via subscripting or a default value')
            _set_type_constrainst(self, type(value))
        if value is not Ellipsis:
            self.current = value

    @classmethod
    def readonly(cls, value: T):
        x = cls(value)
        x.engrave(value)
        return x

    @property
    def current(self):
        return self.__v

    @current.setter
    def current(self, value: T):
        if self.__is_read_only:
            raise ReadOnlyError
        self.__check_type(value)
        self.__v = value

    @current.deleter
    def current(self):
        if self.__is_read_only:
            raise ReadOnlyError
        try:
            del self.__v
        except AttributeError:
            pass

    def engrave(self, value: T):
        self.current = value
        self.__is_read_only = True

    def __check_type(self, value: T):
        check_type('value', value, self._type_constraints())
