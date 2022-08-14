from typing import Optional
from cmdtools.converter.base import BaseConverter, BasicTypes

__all__ = [
    "IntConverter",
    "FloatConverter",
    "BoolConverter",
    "StringConverter",
    "Converter",
]


class IntConverter(BaseConverter):
    """BasicType to int converter

    Parameters
    ----------
    value : BasicTypes
        The value to convert
    """

    def get_int(self) -> Optional[int]:
        result = None

        if isinstance(self.value, str):
            result = int(self.value, base=0)
        elif isinstance(self.value, int):
            result = self.value
        elif isinstance(self.value, (bool, float)):
            result = int(self.value)

        return result


class FloatConverter(BaseConverter):
    """BasicType to float converter

    Parameters
    ----------
    value : BasicTypes
        The value to convert
    """

    def get_float(self) -> Optional[float]:
        result = None

        if isinstance(self.value, str):
            result = float(self.value)
        elif isinstance(self.value, (int, bool)):
            result = float(self.value)
        elif isinstance(self.value, float):
            result = self.value

        return result


class BoolConverter(BaseConverter):
    """BasicType to bool converter

    Parameters
    ----------
    value : BasicTypes
        The value to convert
    """

    def get_bool(self) -> Optional[float]:
        result = None

        if isinstance(self.value, str):
            if self.value:
                if self.value.lower() in ("no", "off", "false", "0"):
                    result = False
                elif self.value.lower() in ("yes", "on", "true", "1"):
                    result = True
                else:
                    result = bool(self.value)
            else:
                result = False
        elif isinstance(self.value, (int, float)):
            result = bool(self.value)
        elif isinstance(self.value, bool):
            result = self.value

        return result


class StringConverter(BaseConverter):
    """BasicType to string converter

    Parameters
    ----------
    value : BasicTypes
        The value to convert
    """

    def get_str(self) -> str:
        return str(self.value)


class Converter(
    IntConverter,
    FloatConverter,
    BoolConverter,
    StringConverter,
):
    """BasicType converter.

    Parameters
    ----------
    value : BasicTypes
        The value to convert
    """

    def __init__(self, value: BasicTypes):
        super().__init__(value)

    def convert(self, type: BasicTypes = str):
        """Converts BasicType to a specific type

        Parameters
        ----------
        type : BasicTypes
            The type that the value should be converted to
        """
        if type is int:
            return self.get_int()
        elif type is float:
            return self.get_float()
        elif type is bool:
            return self.get_bool()
        elif type is str:
            return self.get_str()
        else:
            return self.value
