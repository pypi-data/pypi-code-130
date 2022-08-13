from objectextensions import Extension

from typing import Callable, Generator, Any

from ...state import State
from .constants import Keys, ErrorMessages


class Listeners(Extension):
    """
    Provides an easy way to attach observer methods that will be called immediately after set() and/or get()
    """

    @staticmethod
    def can_extend(target_cls):
        return issubclass(target_cls, State)

    @staticmethod
    def extend(target_cls):
        Extension._wrap(target_cls, "__init__", Listeners.__wrap_init)

        Extension._set(target_cls, "add_listener", Listeners.__add_listener)
        Extension._set(target_cls, "remove_listener", Listeners.__remove_listener)

        Extension._wrap(target_cls, Keys.METHOD_GET, Listeners.__generate_listeners_caller(Keys.METHOD_GET))
        Extension._wrap(target_cls, Keys.METHOD_SET, Listeners.__generate_listeners_caller(Keys.METHOD_SET))

    def __wrap_init(self, *args, **kwargs):
        yield
        Extension._set(self, "_listeners", {
            Keys.METHOD_GET: set(),
            Keys.METHOD_SET: set()
        })

    def __add_listener(self, method: str, listener: Callable[[dict], None]) -> None:
        """
        Adds the provided listener to a set of callbacks for the specified method.
        These callbacks will receive copies of the method return value and its arguments
        in the form `result, self, *args, **kwargs`
        """

        if method not in [Keys.METHOD_GET, Keys.METHOD_SET]:
            ErrorMessages.invalid_method(method)

        self._listeners[method].add(listener)

    def __remove_listener(self, method: str, listener: Callable[[dict], None]) -> None:
        """
        Removes the provided listener from the set of callbacks for the specified method
        """

        if method not in [Keys.METHOD_GET, Keys.METHOD_SET]:
            ErrorMessages.invalid_method(method)

        if listener in self._listeners[method]:
            self._listeners[method].remove(listener)

    @staticmethod
    def __generate_listeners_caller(method: str) -> Callable[..., Generator[None, Any, None]]:
        """
        Used internally as a generic way to get listener handlers that can wrap each relevant method
        """

        def call_listeners(self, *args, **kwargs):
            result = yield

            for listener in self._listeners[method]:
                listener(result, self, *args, **kwargs)

        return call_listeners
