import logging
from copy import copy
from typing import Any, Callable, Iterable

from recipe.on_error import OnError, handle_error
from recipe.types_ import NULL, RecipeResult
from recipe.util import is_empty, is_mutable


class _FakeCache:
    def get(self, key, default=None):
        return default

    def __setitem__(self, key, value):
        pass


class _Cache(dict):
    def get(self, key: Any, default=None):
        return super().get(str(key), default)

    def __setitem__(self, key, value):
        super().__setitem__(str(key), value)


class Recipe:  # pylint: disable=too-few-public-methods
    """
    Central class to generate recipes.
    """

    __slots__ = ("functions", "name", "on_error_behavior", "_cache")

    def __init__(
        self,
        name: str,
        *functions: Callable,
        cachable: bool = True,
        on_error_behavior: OnError = OnError.LOG,
    ):
        self.name: str = name
        self.functions: tuple[Callable, ...] = functions
        self.on_error_behavior: OnError = on_error_behavior
        self._cache: _Cache | _FakeCache = _Cache() if cachable else _FakeCache()

    def __call__(self, initial_value: Any, logger: logging.Logger = None) -> RecipeResult:
        logger = logger if logger is not None else logging.getLogger()

        if (item := self._cache.get(initial_value, NULL)) != NULL:
            logger.debug('Recipe "%s" -> Found %s in cache', self.name, initial_value)
            return item

        if not initial_value:
            logger.debug('Recipe "%s" -> Nothing provided', self.name)
            return RecipeResult()

        result: RecipeResult = execute_sequence_of_functions(
            self.name,
            self.functions,
            initial_value=initial_value,
            logger=logger,
            on_error=self.on_error_behavior,
            value_is_mutable=is_mutable(initial_value),
        )
        self._cache[initial_value] = result
        logger.debug(
            'Recipe "%s" -> Successfully applied recipy (from "%s" to "%s" (Last = "%s"))',
            self.name,
            initial_value,
            result.actual_value,
            result.last_value,
        )
        return result


def get_tool_function_name(func: Callable) -> str:
    return func.__real_name__ if hasattr(func, "__real_name__") else func.__name__


def execute_sequence_of_functions(
    sequence_name: str,
    tool_functions: Iterable[Callable[[Any, str, logging.Logger, OnError, dict], Any]],
    *,
    initial_value: Any,
    logger: logging.Logger,
    on_error: OnError,
    value_is_mutable: bool = False,
) -> RecipeResult:
    processed: Any = copy(initial_value) if value_is_mutable else initial_value
    last: Any = None
    logger.debug(
        'Recipe "%s" -> Initial Value%s: "%s"',
        sequence_name,
        " (MUT) " if value_is_mutable else "",
        initial_value,
    )

    for func in tool_functions:
        if not is_empty(processed):
            last = processed

        try:
            processed = func(
                _value=copy(processed) if value_is_mutable else processed,
                _sequence_name=sequence_name,
                _logger=logger,
                _on_error=on_error,
            )
            logger.debug(
                'Recipe "%s" -> %s: "%s"',
                sequence_name,
                func.__real_name__ if hasattr(func, "__real_name__") else func.__name__,
                processed,
            )
        except Exception as error:  # pylint: disable=broad-except
            handle_error(
                error,
                on_error,
                logger=logger,
                message=f"Recipe {sequence_name} -> "
                f'An error occurred while applying "{get_tool_function_name(func)}" '
                        f'on value "{processed}"',
            )
            return RecipeResult(actual_value=processed, last_value=last, error=error)

    return RecipeResult(actual_value=processed, last_value=last)
