import logging

from .errors import (
    DependencyAlreadyRegistered,
    DependencyNotFound,
    InjectionFailure,
    InjectionNotSupported,
    InjectmeException,
)
from .injector import Injector
from .registry import DependenciesRegistry
from .simple_api import (
    clear_dependencies,
    inject,
    register,
    register_factory,
)


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__all__ = [
    "DependencyAlreadyRegistered",
    "DependencyNotFound",
    "InjectionFailure",
    "InjectionNotSupported",
    "InjectmeException",
    "Injector",
    "DependenciesRegistry",
    "clear_dependencies",
    "inject",
    "register",
    "register_factory",
]

__version__ = "0.0.6"
