from typing import Any, Callable

from .injector import Injector

_injector = Injector()


def _get_injector() -> Injector:
    return _injector


def _get_registry():
    return _get_injector().registry


def inject(cls: type) -> None:
    """
    Mark class as a target for the injection.

    :param cls: Target for injection.
    :raise injectme.InjectionNotSupported: If the cls argument is not an
        instance of ``type``.
    """
    injector = _get_injector()
    return injector(cls)


def register(dependency: type, instance: Any) -> None:
    """
    Register dependency instance to be used during injection phase.

    :param dependency: class of dependency to be registered
    :param instance: instance of dependency to be registered
    :raise injectme.DependencyAlreadyRegistered: If the dependency has already
        been registered.
    """
    registry = _get_registry()
    registry.register_instance(dependency, instance)


def register_factory(dependency: type, factory: Callable[[], Any]) -> None:
    """
    Register dependency factory to be used during injection phase.

    :param dependency: class of dependency to be registered
    :param factory: factory of dependency to be registered
    :raise injectme.DependencyAlreadyRegistered: If the dependency has already
        been registered.
    """
    registry = _get_registry()
    registry.register_factory(dependency, factory)


def clear_dependencies() -> None:
    """
    Clear all of the dependencies registered with :func:`injectme.register` or
    :func:`injectme.register_factory` prior to calling this function.
    """
    registry = _get_registry()
    registry.clear()
