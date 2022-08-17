import abc
import enum
from typing import Dict, Any, List

from json import JSONEncoder
from .typing import JSONType

__all__ = ["AdvancedJSONEncoder", "IResolver", "ResolverPriority", "ResolveError"]


class ResolverPriority(enum.IntEnum):
    LOW_BOUND = 1000
    LOWEST = 1000
    LOW = 750
    MEDIUM = 500
    HIGH = 250
    HIGHEST = 0
    HIGH_BOUND = 0

    @classmethod
    def is_valid_priority(cls, priority: int) -> bool:
        return cls.LOW_BOUND >= priority >= cls.HIGH_BOUND


class IResolver(abc.ABC):
    @abc.abstractmethod
    def get_priority(self) -> int:
        """
        lower number higher priority
        """

    @abc.abstractmethod
    def initialize(self) -> bool:
        """
        :return: False if initialization failed
        """

    @abc.abstractmethod
    def resolve(self, o, context: Dict[str, Any]) -> JSONType:
        """
        :raises ResolveError when cannot resolve the object.
                 If you aren't resolves the object, you MUST raise this exception.
        """


class ResolveError(Exception):
    pass


class AdvancedJSONEncoder(JSONEncoder):
    context: Dict[str, Any]
    _uninitialized_resolvers: Dict[str, IResolver]
    _resolvers: List[IResolver]
    _resolver_name_map: Dict[str, IResolver]

    def __init__(
            self, *,
            skipkeys=False,
            ensure_ascii=True,
            check_circular=True,
            allow_nan=True,
            sort_keys=False,
            indent=None,
            separators=None,
            default=None,
            **kwargs
    ):
        super().__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                         allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators,
                         default=default)
        self.context = kwargs
        self._uninitialized_resolvers = {}
        self._resolver_name_map = {}
        self._resolvers = []

    def default(self, o):
        self.initialize_resolvers()
        for r in self._resolvers:
            try:
                return r.resolve(o, self.context)
            except ResolveError:
                pass
        super().default(o)

    def add_resolver(self, name: str, resolver: IResolver) -> None:
        priority = resolver.get_priority()
        if not ResolverPriority.is_valid_priority(priority):
            raise ValueError(f"Invalid resolver priority: {priority}")
        self._uninitialized_resolvers[name] = resolver

    def get_resolver(self, name: str) -> IResolver:
        self.initialize_resolvers()
        return self._resolver_name_map[name]

    def remove_resolver(self, name: str) -> None:
        self.initialize_resolvers()
        r = self._resolver_name_map.pop(name)
        self._resolvers.remove(r)

    def initialize_resolvers(self) -> None:
        if self._uninitialized_resolvers:
            for name, r in self._uninitialized_resolvers.items():
                if r.initialize():
                    if name in self._resolver_name_map:
                        self.remove_resolver(name)
                    self._resolver_name_map[name] = r
                    self._resolvers.append(r)
            self._resolvers.sort(key=lambda x: x.get_priority())
            self._uninitialized_resolvers.clear()
