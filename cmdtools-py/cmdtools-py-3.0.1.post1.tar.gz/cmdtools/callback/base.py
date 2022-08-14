from __future__ import annotations

import inspect
import typing
from typing import Any, Callable, Dict, Optional, Union

from cmdtools.callback.option import OptionModifier, Options
from cmdtools.converter.base import BasicTypes
from cmdtools.errors import NotEnoughArgumentError, ConversionError

if typing.TYPE_CHECKING:
    from cmdtools import Cmd

__all__ = [
    "Attributes",
    "Context",
    "ErrorContext",
    "Callback",
    "ErrorCallback",
    "callback_init",
    "add_option",
]


class Attributes:
    """Some sort of container to pass some objects
    that cannot be specified from the command argument.

    Parameters
    ----------
    attrs : dict
        A dictionary containing any objects.
    """

    def __init__(self, attrs: Dict[str, Any] = None):
        if attrs is None:
            self.attrs = {}
        else:
            self.attrs = attrs

    def __getattr__(self, name: str) -> Optional[str]:
        return self.attrs.get(name)


class BaseContext:
    """The base class for creating a context."""

    def __init__(self, command: Cmd, attrs: Union[Attributes, Dict[str, Any]] = None):
        self.command = command

        if isinstance(attrs, Attributes):
            self.attrs = attrs
        elif isinstance(attrs, dict):
            self.attrs = Attributes(attrs)
        else:
            self.attrs = Attributes()


class Context(BaseContext):
    """A context to pass to a Callback when
    the callback gets called by an executor.

    Parameters
    ----------
    command : Cmd
        The command object
    options : Options
        The specified options from the callback.
    attrs : Attributes
        The specified attributes from the callback.

    Raises
    ------
    ConversionError
        If converter fails to convert the value of an option.
    """

    def __init__(
        self,
        command: Cmd,
        options: Options = None,
        attrs: Union[Attributes, Dict[str, Any]] = None,
    ):
        if isinstance(options, Options):
            self.options = options
        elif isinstance(options, dict):
            self.options = Options(options)
        else:
            self.options = Options()

        super().__init__(command, attrs)

        for idx, option in enumerate(self.options.options):
            if idx < len(self.command.args):
                converter = self.command.converter(self.command.args[idx])

                if option.modifier is OptionModifier.ConsumeRest:
                    # Consume the rest of the arguments in the command
                    option.value = " ".join(self.command.args[idx:])
                else:
                    try:
                        # Converts the value of an option according to the type.
                        converted = converter.convert(option.type)
                    except (ValueError, TypeError):
                        raise ConversionError(
                            f"Could not convert {option.value!r} into {option.type}",
                            option.name,
                        )

                    # set the value to the converted value if successfully converted,
                    # otherwise, set it to the old value
                    if converted:
                        option.value = converted
                    else:
                        option.value = converter.value

            if option.value is None:
                raise NotEnoughArgumentError(
                    f"Not enough argument for option: {option.name}", option.name
                )

            self.options.options[idx] = option


class ErrorContext(BaseContext):
    """A context to pass to an error callback."""

    def __init__(self, command: Cmd, error: Exception, attrs: Attributes = None):
        self.error = error
        super().__init__(command, attrs)


class BaseCallback:
    """The base class for creating a callback."""

    def __init__(self, func: Callable):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @property
    def is_coroutine(self):
        """Checks if callback is a coroutine function."""
        return inspect.iscoroutinefunction(self.func)


class ErrorCallback(BaseCallback):
    """A callback used for handling errors or exceptions."""

    def make_context(self, command: Cmd, error: Exception, attrs: Attributes = None):
        """Create a new context based on a command object,
        and the error that occurs.

        Parameters
        ----------
        command : Cmd
            The command object.
        error : Exception
            The exception that gets raised.
        attrs : Attributes
            Attributes to pass to the callback context.

        Returns
        -------
        A context created from the command object and the error.
        """
        return ErrorContext(command, error, attrs)


class Callback(BaseCallback):
    """A function to call when related command gets executed.

    Parameters
    ----------
    func : Callable
        A function to call.
    """

    def __init__(self, func: Callable):
        self.options = Options()
        self.errcall = None
        super().__init__(func)

    def make_context(self, command: Cmd, attrs: Attributes = None) -> Context:
        """Create a new context based on a command object.

        Parameters
        ----------
        command : Cmd
            The command object.
        attrs : Attributes
            Attributes to pass to the callback context.

        Returns
        -------
        A context created from the command object.
        """
        return Context(command, self.options, attrs)

    def error(self, func: Callable) -> ErrorCallback:
        """Wraps a function to an ErrorCallback object,
        and set wrapped function as a callback for error
        handling.

        Parameters
        ----------
        func : Callable
            The function to wrap.

        Returns
        -------
        An ErrorCallback object.
        """
        self.errcall = ErrorCallback(func)
        return self.errcall


def callback_init(func: Callable) -> Callback:
    """Wraps a function to a Callback.

    Parameters
    ----------
    func : Callable
        The function to wrap.

    Returns
    -------
    A Callback object.
    """
    return Callback(func)


def add_option(
    name: str,
    *,
    default: Any = None,
    modifier: OptionModifier = OptionModifier.NoModifier,
    type: BasicTypes = str,
):
    """A callback wrapper for adding an option.

    Parameters
    ----------
    name : str
        The option name.
    default : str
        Default value if argument is not specified.
    modifier : OptionModifier
        The option modifier,
        some modifier used to modify the value.
    type : BasicType
        Convert the value to specified type.

    Raises
    ------
    TypeError
        If the wrapped object is not a callback object.
    """

    def decorator(obj):
        if isinstance(obj, Callback):
            obj.options.add(name, default, modifier, type=type)
        elif isinstance(obj, Callable):
            obj = Callback(obj)
            obj.options.add(name, default, modifier, type=type)
        else:
            raise TypeError(f"Cannot add option to object {obj!r}")

        return obj

    return decorator
