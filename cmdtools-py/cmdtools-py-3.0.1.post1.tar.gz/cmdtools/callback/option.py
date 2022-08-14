import dataclasses
import enum
from typing import Any, List, Optional
from cmdtools.converter.base import BasicTypes

__all__ = [
    "OptionModifier",
]


class OptionModifier(enum.Enum):
    """An option modifier.

    NoModifier
        doesn't do anything to the option value.
    ConsumeRest
        Consume the rest of the arguments in the command
    """

    NoModifier = "no_modifier"
    ConsumeRest = "consume_rest"


@dataclasses.dataclass
class Option:
    """An option dataclass.

    Parameters
    ----------
    name : str
        The name of the option.
    value : str
        The value of the option.
    modifier : OptionModifier
        The option modifier,
        some modifier used to modify the value.
    type : BasicType
        Convert the value to specified type.
    """

    name: str
    value: str
    modifier: OptionModifier = OptionModifier.NoModifier
    type: BasicTypes = str


class Options:
    """An option container class.

    Parameters
    ----------
    options : List[Option]
        List of options to store.
    """

    def __init__(self, options: List[Option] = None):
        if options is None:
            self.options = []
        else:
            self.options = options

    def __getattr__(self, name: str) -> Optional[str]:
        option = self.get(name)

        if option:
            return option.value

    def get(self, name: str) -> Option:
        """Gets an option by name.

        Parameters
        ----------
        name : str
            The name of the option.
        """
        for option in self.options:
            if option.name == name:
                return option

    def has_option(self, name: str) -> Optional[int]:
        """Check if the container has an option.

        Parameters
        ----------
        name : str
            The name of the option.
        """
        if self.get(name):
            return True

        return False

    def add(
        self,
        name: str,
        default: Any = None,
        modifier: OptionModifier = OptionModifier.NoModifier,
        append: bool = False,
        type: BasicTypes = str,
    ):
        """Store or add an option to container.

        Parameters
        ----------
        name : str
            The option name.
        default : str
            Default value if argument is not specified.
        modifier : OptionModifier
            The option modifier,
            some modifier used to modify the value.
        append : bool
            If true use append method to store an option,
            else use insert from the first index (0).
        type : BasicType
            Convert the value to specified type.
        """
        option = self.has_option(name)

        if not option:
            option_args = []
            option_args.append(name)
            option_args.append(default)
            option_args.append(modifier)
            option_args.append(type)

            if not append:
                self.options.insert(0, Option(*option_args))
            else:
                self.options.append(Option(*option_args))
