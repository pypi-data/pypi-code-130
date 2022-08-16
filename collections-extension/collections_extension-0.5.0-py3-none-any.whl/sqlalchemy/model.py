from contextlib import suppress
from importlib import import_module
from inspect import getmembers
from operator import itemgetter
from types import ModuleType

from ..native import Map

__all__ = [

]


with suppress(ImportError):
    from sqlalchemy.ext.declarative import DeclarativeMeta

    class SqlalchemyModelMap(Map[str, DeclarativeMeta]):
        """Sqlalchemy objects map."""
        __slots__ = ()

        @classmethod
        def from_module(
            cls,
            module: ModuleType,
        ) -> 'SqlalchemyModelMap':
            """Create model map from module."""
            return cls({
                cls.__tablename__: cls for cls in map(
                    itemgetter(1),
                    getmembers(
                        module,
                        lambda item: isinstance(
                            item, DeclarativeMeta,
                        ) and getattr(
                            item, '__tablename__', False,
                        ),
                    ),
                )
            })

        @classmethod
        def from_module_name(
            cls,
            module_name: str,
        ) -> 'SqlalchemyModelMap':
            """Create model map from module name."""
            module = import_module(module_name)
            return cls.from_module(module)


    __all__.append(SqlalchemyModelMap.__name__)
