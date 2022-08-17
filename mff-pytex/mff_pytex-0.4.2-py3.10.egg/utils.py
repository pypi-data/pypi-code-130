"""Basic utils for work with LaTeX documents."""


from typing import Optional, Any
import sys
from os import path


class File:
    """Abstract class for generating files.
    """
    file_type: str
    file_path: str
    file_name: str

    def __init__(self, file_name: str) -> None:
        """Initialize File

        Args:
            file_name (str): Name of file which will be created.
        """

        self.file_name = file_name
        self.file_path = f"{get_dir()}/{file_name}.{self.file_type}"


def get_func_name() -> str:
    """Utility that returns name of function.

    Returns:
        str: Name of function.
    """
    return sys._getframe(1).f_code.co_name


def get_dir() -> str:
    """Returns directory where main file has been executed.

    Returns:
        str: Directory name where is main file
    """
    return str(path.dirname(str(sys.modules['__main__'].__file__)))


def get_path() -> str:
    """Returns path to main file.

    Returns:
        str: Path to main file
    """
    return str(path.abspath(str(sys.modules['__main__'].__file__)))


def command(comm: str, main: Optional[str] = None, *params) -> str:
    """Template for creating commands.

    If main is None, than return '\\command'.
    If main is not none, but any optional parameter given, than return '\\command{main}'
    If main and optional parameters given, than return '\\command[param1, param2, ...]{main}'

    Args:
        comm (str): Name of command
        main (str| None, optional): Main parameter of command, defaults to None.
        *params (str): Optional parameters of command

    Returns:
        str: string of given command by given parameters.
    """
    if main is None:
        return f"\\{comm}"
    elif params:
        return f"\\{comm}[{', '.join(params)}]{{{main}}}"
    else:
        return f"\\{comm}{{{main}}}"


def doublecommand(comm: str, main: str, second: Optional[str] = None, opt: bool = False) -> str:
    """Template for creating doublecommands.

    Commands lokks like this \\comm{main} {second}

    Args:
        comm (str): Name of command
        main (str): First parameter
        second (str | None, optional): Second parameter
        opt (bool, optional): Set if the second parameter is optional. Defaults None

    Returns:
        str: string of given command by given parameters.
    """
    if second is None:
        return f"\\{comm}{{{main}}}"
    elif opt:
        return f"\\{comm}{{{main}}} [{second}]"
    else:
        return f"\\{comm}{{{main}}} {{{second}}}"


class Writing:
    _text = ""

    def __str__(self) -> str:
        return self._text

    def _writeline(self, text: str) -> None:
        """Write single line to the TeX file.

        Args:
            text (str): Line of text intended for insert to content.
        """
        self._text += f"{text}\n"

    def write(self, *lines: Optional[str]) -> None:
        """Write multiple lines to the TeX file.

        Args:
            *lines (str): Lines of text intended for insert to content.
        """
        for line in lines:
            if line is not None:
                self._writeline(line)

    def add(self, environment: Any) -> None:
        """Writes environment to the TeX file.

        Args:
            environment (Any): Figure to use.
        """
        self.write(str(environment))

    def math(self, formula: str) -> None:
        """Add math formula to the TeX file.

        Args:
            formula (str): Used formula
        """
        self.write(f"\\[{formula}\\]")


class Environment(Writing):
    """Basic environment structure.

    Attributes:
        en_type (str): Type of environment
        _text (str): Content of environment,
    """

    def __init__(self, en_type: str, *params: str) -> None:
        """Initialize Environment.

        Args:
            en_type (str): Type of environment
            *params (str): Optional parameters for environment
        """
        self.en_type = en_type
        if params:
            self.write(command('begin', self.en_type, *params))
        else:
            self.write(command('begin', self.en_type))

    def __str__(self) -> str:
        """Returns content string encapsuled by environment.

        Returns:
            str: Content
        """
        return self._text + command('end', self.en_type) + '\n'
