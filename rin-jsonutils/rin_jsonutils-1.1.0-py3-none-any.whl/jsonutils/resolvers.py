import numbers
from datetime import datetime
from typing import Dict, Any, Mapping, Callable, Union

from .advanced_json_encoder import IResolver, ResolveError, ResolverPriority
from .typing import JSONType, JSONSerializable

__all__ = ["JSONSerializableResolver", "NumberResolver", "IterableResolver", "DateTimeResolver", "NumpyResolver"]


class _Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class JSONSerializableResolver(IResolver, _Singleton):

    def get_priority(self) -> int:
        return ResolverPriority.HIGH

    def initialize(self) -> bool:
        return True

    def resolve(self, o, context: Dict[str, Any]) -> JSONType:
        if isinstance(o, JSONSerializable):
            return o.__json__(context)
        raise ResolveError()


class NumberResolver(IResolver, _Singleton):
    def get_priority(self) -> int:
        return ResolverPriority.MEDIUM

    def initialize(self) -> bool:
        return True

    def resolve(self, o, context: Dict[str, Any]) -> JSONType:
        if isinstance(o, numbers.Integral):
            return int(o)
        if isinstance(o, numbers.Real):
            return float(o)
        raise ResolveError()


class IterableResolver(IResolver, _Singleton):
    def get_priority(self) -> int:
        return ResolverPriority.MEDIUM

    def initialize(self) -> bool:
        return True

    def resolve(self, o, context: Dict[str, Any]) -> JSONType:
        if isinstance(o, Mapping):
            return dict(o)
        try:
            return list(o)
        except TypeError:
            pass
        raise ResolveError()


class DateTimeResolver(IResolver):
    def __init__(self, datetime_format: Union[str, Callable[[datetime], str]] = None):
        self.datetime_format = datetime_format

    def get_priority(self) -> int:
        return ResolverPriority.MEDIUM

    def initialize(self) -> bool:
        return True

    def resolve(self, o, context: Dict[str, Any]) -> JSONType:
        if isinstance(o, datetime):
            datetime_format = context.get("datetime.format", self.datetime_format)
            if datetime_format is None:
                return o.isoformat()
            if isinstance(datetime_format, str):
                return o.strftime(datetime_format)
            if isinstance(datetime_format, Callable):
                return datetime_format(o)
        raise ResolveError()


class NumpyResolver(IResolver, _Singleton):

    def get_priority(self) -> int:
        return ResolverPriority.HIGH

    def initialize(self) -> bool:
        try:
            import numpy as np
            return True
        except ImportError:
            return False

    def resolve(self, o, context: Dict[str, Any]) -> JSONType:
        import numpy as np
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise ResolveError()
