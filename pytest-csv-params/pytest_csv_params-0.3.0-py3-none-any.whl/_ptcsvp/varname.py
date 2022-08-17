"""
Test if a variable name is valid
"""

import builtins
import keyword
import re
from string import ascii_letters, digits

from pytest_csv_params.exception import CsvHeaderNameInvalid

VALID_CHARS = ascii_letters + digits
VARIABLE_NAME = re.compile(r"^[a-zA-Z_][A-Za-z0-9_]{0,1023}$")


def is_valid_name(name: str) -> bool:
    """
    Checks if the variable name is valid
    """
    if (
        keyword.iskeyword(name)
        or (hasattr(keyword, "issoftkeyword") and getattr(keyword, "issoftkeyword")(name))
        or getattr(builtins, name, None) is not None
    ):
        return False
    return VARIABLE_NAME.match(name) is not None


def make_name_valid(name: str, replacement_char: str = "_") -> str:
    """
    Make a name valid
    """

    fixed_name = name

    for index, character in enumerate(name):
        if character in VALID_CHARS:
            continue
        fixed_name = f"{fixed_name[:index]}{replacement_char}{fixed_name[index+1:]}"
    if fixed_name[0] not in ascii_letters:
        fixed_name = f"{replacement_char}{fixed_name[1:]}"
    if not is_valid_name(fixed_name):
        raise CsvHeaderNameInvalid(f"'{fixed_name}' is not a valid variable name")
    return fixed_name
