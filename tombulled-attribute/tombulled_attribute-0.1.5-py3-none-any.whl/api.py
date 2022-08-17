from typing import Any, Callable, Optional

DEFAULT: object = object()


class Attribute:
    name: str
    __default: Any = None
    __default_factory: Optional[Callable] = None

    def __init__(
        self,
        name: str,
        *,
        default: Any = None,
        default_factory: Optional[Callable] = None,
    ) -> None:
        if default is not None and default_factory is not None:
            raise ValueError("cannot specify both default and default_factory")

        self.name = name
        self.__default = default
        self.__default_factory = default_factory

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r}, default={self.default!r})"

    def __str__(self) -> str:
        return self.name

    @property
    def default(self) -> Any:
        if self.__default_factory is not None:
            return self.__default_factory()

        return self.__default

    def __getitem__(self, obj: Any, /) -> Any:
        return getattr(obj, self.name)

    def get(self, obj: Any, default: Any = DEFAULT) -> Any:
        return getattr(
            obj, self.name, default if default is not DEFAULT else self.default
        )

    def delete(self, obj: Any) -> None:
        delattr(obj, self.name)

    def has(self, obj: Any) -> bool:
        return hasattr(obj, self.name)

    def set(self, obj: Any, val: Any = DEFAULT) -> None:
        setattr(obj, self.name, val if val is not DEFAULT else self.default)

    def setdefault(self, obj: Any, default: Any = DEFAULT) -> Any:
        if self.has(obj):
            return self.get(obj)

        self.set(obj, default if default is not DEFAULT else self.default)

        return self.get(obj)
