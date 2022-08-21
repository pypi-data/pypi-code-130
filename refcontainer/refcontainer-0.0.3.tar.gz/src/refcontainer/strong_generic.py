# type: ignore
from typing import Any, Generic, Type, TypeVar


T = TypeVar('T')
def _set_type_constrainst(self: Any, params: Type[T]):
    def f(*a, **kw):
        return params
    self._type_constraints = f


class StrongGeneric(Generic[T]):
    def __class_getitem__(cls, params: Type[T]):
        if params is T:
            return cls
        class SubCls(cls):
            pass
        _set_type_constrainst(SubCls, params)
        return SubCls

    @staticmethod
    def _type_constraints() -> Type[T]:
        raise AttributeError
