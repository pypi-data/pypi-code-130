from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Union

from cmdtools import utils
from cmdtools.callback import Attributes, Callback
from cmdtools.converter.converter import Converter

__all__ = ["Cmd", "Executor", "execute"]


class Cmd:
    """A base class for creating a command object.

    Parameters
    ----------
    text : str
        Command text to parse. ex: `'/ping 8.8.8.8'`
    prefix : str
        The prefix of the command
    converter
        Converter for arguments.

    Examples
    --------
    Creating a basic command object::

        from cmdtools import Cmd

        x = Cmd("/test")

        if x.name == "test":
            print("test ok!")


    """

    def __init__(
        self, text: str, prefix: str = "/", *, converter: Converter = Converter
    ):
        self.text = text
        self.prefix = utils.string.PrefixChecker(text, prefix)
        self.converter = converter

    @property
    def _args(self) -> Optional[List[str]]:
        if self.prefix.strip_prefix is not None:
            return utils.string.splitargs(self.prefix.strip_prefix)

        return []

    @property
    def args(self) -> Optional[List[str]]:
        """List of arguments in the command"""
        if len(self._args) > 1:
            return self._args[1:]

        return []

    @property
    def name(self) -> Optional[str]:
        """The name of the command"""
        if len(self._args) >= 1:
            return self._args[0]


class Executor:
    """A class for creating custom command executor

    Parameters
    ----------
    command
        The command object to execute.
    callback
        The callback that will be called when command is executed.
    attrs
        Attributes to pass to the callback context.

    Examples
    --------
    Executing a command with a custom executor::

        from cmdtools import Cmd, Executor
        from cmdtools.callback import callback_init

        cmd = Cmd("/somecmd")

        @callback_init
        def some_callback(ctx):
            print("Wicked insane!")

        x = Executor(cmd, some_callback)
        x.exec()


    Raises
    ------
    TypeError
        If callback is not a `Callback` instance or,
        if callback is coroutine but the error callback is not, or vice versa.
    """

    def __init__(
        self,
        command: Cmd,
        callback: Callback,
        *,
        attrs: Union[Attributes, Dict[str, Any]] = None,
    ):
        self.command = command
        if not isinstance(attrs, Attributes):
            if isinstance(attrs, dict):
                self.attrs = Attributes(attrs)
            else:
                self.attrs = Attributes()
        else:
            self.attrs = attrs

        if not isinstance(callback, Callback):
            raise TypeError(f"{callback!r} is not a Callback type!")
        self.callback = callback

        if self.callback.errcall:
            if self.callback.is_coroutine:
                if not self.callback.errcall.is_coroutine:
                    raise TypeError(
                        "Error callback should be a coroutine function if callback is coroutine"
                    )
            elif self.callback.errcall.is_coroutine:
                if not self.callback.is_coroutine:
                    raise TypeError(
                        "Error callback cannot be a coroutine function if callback is not a coroutine function"
                    )

    def exec(self) -> Optional[Any]:
        """Executes the command passed in constructor

        Returns
        -------
        Anything retured in the callback.

        Raises
        ------
        Exception
            Any exception raised during execution
            if error callback is not set.
        """
        result = None
        old_options = copy.deepcopy(self.callback.options.options)

        try:
            context = self.callback.make_context(self.command, self.attrs)
            result = self.callback(context)
        except Exception as exception:
            if self.callback.errcall:
                error_context = self.callback.errcall.make_context(
                    self.command, exception, self.attrs
                )
                result = self.callback.errcall(error_context)
            else:
                raise exception

        self.callback.options.options = old_options
        return result

    async def exec_coro(self) -> Optional[Any]:
        """Executes the command passed in constructor
        if the callback is coroutine.

        Returns
        -------
        Anything returned in the callback.

        Raises
        ------
        Exception
            Any exception raised during execution
            if error callback is not set.
        """
        result = None
        old_options = copy.deepcopy(self.callback.options.options)

        try:
            context = self.callback.make_context(self.command, self.attrs)
            result = await self.callback(context)
        except Exception as exception:
            if self.callback.errcall:
                error_context = self.callback.errcall.make_context(
                    self.command, exception, self.attrs
                )
                result = await self.callback.errcall(error_context)
            else:
                raise exception

        self.callback.options.options = old_options
        return result


async def execute(
    command: Cmd,
    callback: Callback,
    *,
    attrs: Union[Attributes, Dict[str, Any]] = None,
):
    """A simple executor using `Executor` class

    Parameters
    ----------
    command
        The command object to execute.
    callback
        The callback that will be called when command is executed.
    attrs
        Attributes to pass to the callback context.

    Returns
    -------
    Anything retured in the callback.

    Raises
    ------
    Exception
        Any exception raised during execution
        if error callback is not set.
    TypeError
        If callback is not a `Callback` instance or,
        if callback is coroutine but the error callback is not, or vice versa.
    """
    executor = Executor(command, callback, attrs=attrs)

    if callback.is_coroutine:
        return await executor.exec_coro()

    return executor.exec()
