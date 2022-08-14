import inspect
from typing import Any, Callable, Dict, List, Optional, Union

from cmdtools import Cmd, Executor, NotFoundError
from cmdtools.callback import Attributes, Callback, ErrorCallback
from cmdtools.callback.option import OptionModifier
from cmdtools.converter.base import BasicTypes

__all__ = ["Command", "Group"]


class BaseCommand:
    """Base class of command struct or class."""

    _callback: Optional[Callback]

    def __init__(self, name: str):
        self.name = name
        self._callback = None

    @property
    def callback(self) -> Optional[Callback]:
        """returns the callback of the command struct or class if set."""
        if not isinstance(self._callback, Callback):
            func: Callable = getattr(self, self.name, None)
            errfunc: Callable = getattr(self, "error_" + self.name, None)

            if inspect.ismethod(func):
                self._callback = Callback(func)
                if errfunc:
                    self._callback.errcall = ErrorCallback(errfunc)
                return self._callback
        else:
            return self._callback

    def add_option(
        self,
        name: str,
        *,
        default: Any = None,
        modifier: OptionModifier = OptionModifier.NoModifier,
        type: BasicTypes = str,
    ):
        """Adds an option to callback.

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
        """
        self.callback.options.add(name, default, modifier, append=True, type=type)


class Command(BaseCommand):
    """A command struct or class.

    Parameters
    ----------
    name : str
        The name of the command.
    aliases : List[str]
        The aliases of the command.
    """

    def __init__(self, name: str, aliases: List[str] = None):
        if aliases is None:
            aliases = []
        self._aliases = aliases
        super().__init__(name)

    @property
    def aliases(self) -> List[str]:
        """gets the command aliases if set."""
        if self._aliases:
            return self._aliases

        return getattr(self, "__aliases__", [])


class Container:
    """Command struct or class container class.

    Parameters
    ----------
    commands : List[Command]
        List of command struct or class to store.
    """

    def __init__(self, commands: List[Command] = None):
        if not commands:
            commands = []

        self.commands = commands

    def get_names(self, aliases: bool = False) -> List[str]:
        """gets all command names stored in the container.

        Parameters
        ----------
        aliases : bool
            Includes the commands aliases.
        """
        names = [cmd.name for cmd in self.commands]

        if aliases:
            names.extend([cmd.aliases for cmd in self.commands])

        return names

    def has_command(self, name: str) -> bool:
        """Checks if the container has a command.

        Parameters
        ----------
        name : str
            The command name.
        """
        return name in self.get_names()

    async def run(
        self, command: Cmd, *, attrs: Union[Attributes, Dict[str, Any]] = None
    ):
        """Executes a command in container by the command object.

        Parameters
        ----------
        command : Cmd
            The command object.
        attrs : dict or Attributes
            Attributes to pass to the callback context.

        Raises
        ------
        NotFoundError
            If the specified command is not found in the container.
        """
        if attrs is None:
            attrs = {}

        for cmd in self.commands:
            if cmd.name == command.name or command.name in cmd.aliases:
                executor = Executor(command, cmd.callback, attrs=attrs)

                if cmd.callback.is_coroutine:
                    return await executor.exec_coro()

                return executor.exec()

        raise NotFoundError(f"Command not found: {command.name}", command.name)


class GroupWrapper(Command):
    """A callback wrapper for functions.

    Parameters
    ----------
    name : str
        The command name.
    aliases : List[str]
        The command aliases.
    """

    def __init__(self, name: str, aliases: List[str] = None):
        super().__init__(name, aliases)

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

    @property
    def error_callback(self) -> Optional[ErrorCallback]:
        return self.callback.errcall


class Group(Container):
    """A group based container class.

    Parameters
    ----------
    name : str
        The group name
    commands : List[Command]
        List of command struct or class
        to store to the container.
    """

    def __init__(self, name: str, commands: List[Command] = None):
        self.name = name
        super().__init__(commands)

    def command(self, name: str = None, *, aliases: List[str] = None):
        """stores a command struct or class to the container.

        Parameters
        ----------
        name : str
            The name of the command
        aliases : List[str]
            The command aliases.
        """
        if aliases is None:
            aliases = []

        def decorator(obj):
            nonlocal name

            if inspect.isclass(obj) and Command in inspect.getmro(obj):
                self.commands.append(obj())
            else:
                if not name:
                    if isinstance(obj, Callback):
                        name = obj.func.__name__
                    elif isinstance(obj, Callable):
                        name = obj.__name__

                wrapper = GroupWrapper(name, aliases)
                if isinstance(obj, Callback):
                    wrapper._callback = obj
                else:
                    wrapper._callback = Callback(obj)
                self.commands.append(wrapper)

                return wrapper
            return obj

        return decorator
