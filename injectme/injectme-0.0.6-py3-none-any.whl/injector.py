import logging
from typing import Optional

from .errors import (
    DependencyNotFound,
    InjectionFailure,
    InjectionNotSupported,
)
from .registry import DependenciesRegistry

logger = logging.getLogger(__name__)


class Injector:
    """
    Class responsible for the injection of dependencies.
    """

    def __init__(self, registry: Optional[DependenciesRegistry] = None):
        """
        Initialize the Injector.

        :param registry: dependencies registry
            to be used with this ``Injector`` instance. If not sepcified,
            an instance of registry will be created automatically.
        """
        if registry is None:
            registry = DependenciesRegistry()

        self._registry = registry

    @property
    def registry(self) -> DependenciesRegistry:
        """
        Dependencies registry associated with this ``Injector``.

        :return: instance of registry.
        """
        return self._registry

    def __call__(self, cls: type) -> type:
        """
        Mark class to be the target of injection performed with this instance
        of ``Injector``.

        :param cls: class to be marked for injection.
        :raises InjectionFailure: raised if any of the required dependencies
            can't be found in the registry associated with this ``Injector``.
        :return: class passed as a param.
        """
        logger.debug("marking %s as target for %s", cls, self)
        if not isinstance(cls, type):
            raise InjectionNotSupported(cls)

        injector = self

        def __init_deps__(self):
            annotations = cls.__dict__.get("__annotations__", {})
            registry = injector.registry

            logger.debug(
                "injecting into %s by %s using %s", self, injector, registry
            )

            try:
                for name, dependency in annotations.items():
                    instance = registry.get(dependency)
                    setattr(self, name, instance)
            except DependencyNotFound as err:
                raise InjectionFailure(cls) from err

        def injectme_init(self, *args, **kwargs):
            cls.__init_deps__(self)
            cls.__original_init__(self, *args, **kwargs)

        cls.__original_init__ = cls.__init__
        cls.__init_deps__ = __init_deps__
        cls.__init__ = injectme_init

        return cls
