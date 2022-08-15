from typing import Any


class InjectmeException(Exception):
    """
    Base class for all injectme's exceptions.
    """


class DependencyNotFound(InjectmeException):
    """
    Requested dependency has not been found in the registry.
    """

    def __init__(self, dependency: type):
        super().__init__(
            f"Dependency {dependency} has not been found in the registry"
        )


class DependencyAlreadyRegistered(InjectmeException):
    """
    Dependency has already been registered in selected registry.
    """

    def __init__(self, dependency: type):
        super().__init__(f"Dependency {dependency} already registered")


class InjectionNotSupported(InjectmeException):
    """
    Decorated target is not valid for injection.
    """

    def __init__(self, target: Any):
        super().__init__(f"Unsopported injection target {target}")


class InjectionFailure(InjectmeException):
    """
    Failed to inject the dependency.
    """

    def __init__(self, cls: type):
        super().__init__(f"Failed to inject dependencies into {cls}")
