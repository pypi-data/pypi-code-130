from enum import Enum
from color_gradient_generator.errors import IncorrectProvidedColor
class ColorFormat(Enum):
    """
    Represents the format of the color :

    `DEC` stands for "decimal",

    `HEX` stands for "hexadecimal",

    `RGB` stands for... well... RGB.
    """
    DEC = 0
    HEX = 1
    RGB = 2

types = {
    "int": "DEC",
    "str": "HEX",
    "tuple": "RGB"
}

class Color:
    """
    Represents a color, in either decimal, hexadecimal, or RGB format.
    """
    def __init__(self, value: int | str | tuple):
        _format = ColorFormat[types[value.__class__.__name__]]
        if _format == ColorFormat.DEC and value not in range(16777216):
                raise IncorrectProvidedColor("Please provide a correct DEC format (integer between 0 and 16777215).")
        if _format == ColorFormat.HEX:
            try:
                if len(value) == 3: value = "".join(f"{i}{i}" for i in [value[i:i+1] for i in range(0, 3, 1)])
                int(value, 16)
            except ValueError:
                raise IncorrectProvidedColor("Please provide a correct HEX format (string composed of 3 or 6 characters, from 0 to 9 and from a to f, without any hexadecimal prefix).")
        if _format == ColorFormat.RGB:
            for i in value:
                if i not in range(256) or len(value) != 3:
                    raise IncorrectProvidedColor("Please provide a correct RGB format (tuple composed of 3 integers between 0 and 255).")

        self._format = _format
        self.value = value
    
    def __dec__(self) -> int:
        """
        The decimal value of the :class:`Color`.
        """
        if self.value.__class__ == str:
            return int(self.value, 16)
        elif self.value.__class__ == tuple:
            return (self.value[0] << 16) + (self.value[1] << 8) + self.value[2]
        else:
            return self.value
    
    def __hex__(self, prefix: str = "") -> str:
        """
        The hexadecimal value of the :class:`Color`.
        """
        if self.value.__class__ == int:
            return f"{prefix}{self.value:0>6x}"
        elif self.value.__class__ == tuple:
            return "{}%02x%02x%02x".format(prefix) % self.value
        else:
            return f"{prefix}{self.value}"
    
    def __rgb__(self) -> tuple[int]:
        """
        The RGB value of the :class:`Color`.
        """
        if self.value.__class__ == str:
            return tuple(int(self.value[i:i+2], 16) for i in (0, 2, 4))
        elif self.value.__class__ == int:
            return (self.value & 255, (self.value << 8) & 255, (self.value << 16) & 255)
        else:
            return self.value