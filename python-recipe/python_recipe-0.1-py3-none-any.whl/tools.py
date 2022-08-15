import logging
from typing import Any, Callable, Iterable

from recipe.on_error import OnError
from recipe.recipe_core import execute_sequence_of_functions
from recipe.types_ import RecipeResult
from recipe.util import call_or_return_value, is_empty, is_mutable


def do(func: Callable, *func_args, **func_kwargs):
    """
    Generates a function that will call the given function *func* with provided
    arguments *func_args* and *func_kwargs*.
    """

    def _do(
        _value: Any,
        _sequence_name: str,
        _logger: logging.Logger,
        _on_error: OnError,
        **kwargs,
    ):
        return func(_value, *func_args, **(func_kwargs | kwargs))

    _do.__real_name__ = func.__qualname__
    return _do


def do_and_take_index(func: Callable, *func_args, _index: int, **func_kwargs):
    """Similar to *do*. The difference is in the result of the function *func*,
    which in this case must return an iterable. On successful execution, the
    result of the function will be the element at index *_index* of the
    iterable.

    .. note:: Index must be passed as a keyword argument.

    """

    def _do(
        _value: Any,
        _sequence_name: str,
        _logger: logging.Logger,
        _on_error: OnError,
        **kwargs,
    ):
        return func(_value, *func_args, **(func_kwargs | kwargs))[_index]

    _do.__real_name__ = func.__qualname__
    return _do


def while_(
    *functions: Callable,
    _block_name: str = None,
    _condition: bool | Callable[[Any], bool] = True,
):
    """Executes the block of functions *functions* as long as the condition
    evaluates to True.

    *functions* must be tool functions found in this module or any other
    function that respect the same signature.

    The condition evaluates as follows:

        - Computed value by *functions* must differ from the previous loop iteration.
        - Computed value by *functions* must not be empty, when applies (__len__ defined).
        - *_condition* must evaluate to True.

    Using *_block_name* you can name the block of functions for logging purposes.

    """
    _block_name: str = _block_name or "while"

    def _while_(
        _value: Any,
        _sequence_name: str,
        _logger: logging.Logger,
        _on_error: OnError,
        **kwargs,
    ):
        modified: str = ""

        while (
            modified != _value and not is_empty(_value) and call_or_return_value(_condition, _value)
        ):

            result: RecipeResult = execute_sequence_of_functions(
                f"{_sequence_name}::{_block_name}",
                functions,
                initial_value=_value,
                logger=_logger,
                on_error=_on_error,
                value_is_mutable=is_mutable(_value),
            )
            modified = _value

            _value = result.actual_value
            logging.debug("*** endloop ***")

        return _value

    return _while_


def if_(
    condition: bool | Callable[[Any], bool],
    *,
    _on_true: Iterable[Callable],
    _on_false: Iterable[Callable] = None,
    _block_name: str = None,
):
    """Conditionally executes a given block of functions depending on the
    result of *condition*.

    *condition* receives as first argument the inner value.

    """
    _block_name = _block_name or "if"

    def _if_(
        _value: Any,
        _sequence_name: str,
        _logger: logging.Logger,
        _on_error: OnError,
        **kwargs,
    ):
        if call_or_return_value(condition, _value):
            return execute_sequence_of_functions(
                f"{_sequence_name}::{_block_name}-true",
                _on_true,
                initial_value=_value,
                logger=_logger,
                on_error=_on_error,
                value_is_mutable=is_mutable(_value),
            ).actual_value

        if _on_false:
            return execute_sequence_of_functions(
                f"{_sequence_name}::{_block_name}-false",
                _on_false,
                initial_value=_value,
                logger=_logger,
                on_error=_on_error,
                value_is_mutable=is_mutable(_value),
            ).actual_value

        return _value

    return _if_
