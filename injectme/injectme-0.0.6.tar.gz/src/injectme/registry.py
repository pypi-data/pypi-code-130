import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from .errors import DependencyNotFound, DependencyAlreadyRegistered

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    INSTANCE = 1
    FACTORY = 2


@dataclass
class RegistryEntry:
    dependency_type: DependencyType
    dependency_value: Any

    @classmethod
    def factory(cls, factory) -> "RegistryEntry":
        return cls(
            dependency_type=DependencyType.FACTORY,
            dependency_value=factory,
        )

    @classmethod
    def instance(cls, instance) -> "RegistryEntry":
        return cls(
            dependency_type=DependencyType.INSTANCE,
            dependency_value=instance,
        )


class DependenciesRegistry:
    """
    Class used as a registry of instances and factories which can be used
    for injection.
    """

    def __init__(self):
        self._dependencies = {}

    def get(self, dependency: type) -> Any:
        """
        Get object registered as an instance of dependency or call callable
        registered as a factory of dependency.

        :param dependency: dependency for which a registered instance will be
            returned.
        :raises DependencyNotFound: raised if the dependency passed as argument
            has not been registered prior to making this call.
        :return: instance of dependency.
        """
        logger.debug("looking for %s in %s", dependency, self)
        entry = self._dependencies.get(dependency)
        if entry is None:
            raise DependencyNotFound(dependency)

        if entry.dependency_type == DependencyType.FACTORY:
            return entry.dependency_value()

        return entry.dependency_value

    def register_instance(self, dependency: type, instance: Any) -> None:
        """
        Register passed object as an instance of dependency.

        :param dependency: dependency for which an instance should be
            registered.
        :param instance: an object which should be registered as an instance of
            dependency.
        :raises DependencyAlreadyRegistered: raised if dependency has been
            already registered.
        """
        logger.debug(
            "registering %s as %s dependency in %s",
            instance,
            dependency,
            self,
        )
        self._ensure_not_registered(dependency)
        entry = RegistryEntry.instance(instance)
        self._dependencies[dependency] = entry

    def register_factory(
        self, dependency: type, factory: Callable[[], Any]
    ) -> None:
        """
        Register passed callable as a factory of dependency instances.

        :param dependency: dependency for which an instance should be
            registered.
        :param factory: a callable which should be registered as a factory of
            dependency instances
        :raises DependencyAlreadyRegistered: raised if dependency has been
            already registered.
        """
        logger.debug(
            "registering %s as %s dependency in %s",
            factory,
            dependency,
            self,
        )
        self._ensure_not_registered(dependency)
        entry = RegistryEntry.factory(factory)
        self._dependencies[dependency] = entry

    def clear(self) -> None:
        """
        Remove all of the registered dependencies.
        """
        logger.debug("clearing %s registry", self)
        self._dependencies = {}

    def _ensure_not_registered(self, dependency):
        if dependency in self._dependencies:
            raise DependencyAlreadyRegistered(dependency)
