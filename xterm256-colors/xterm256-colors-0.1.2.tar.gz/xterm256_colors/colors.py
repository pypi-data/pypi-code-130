from __future__ import annotations

import colorsys
import functools
import math
from typing import Type, cast

from ._compat import LabColor, convert_color, requires_colormath, sRGBColor
from .constants import CMDNUM_BACKGROUND, CSI, CMDNUM_FOREGROUND, RESET_ALL
from .types import NOTSET

__all__ = [
    'XtermColor',
    'XtermCodes',
    'Fore256',
    'Back256',
]


def code_to_chars(code: int, is_background: bool = False):
    cmdnum = CMDNUM_BACKGROUND if is_background else CMDNUM_FOREGROUND
    return CSI + cmdnum + ';5;' + str(code) + 'm'


class _XtermColorSwatch:
    __slots__ = ('color',)
    color: XtermColor

    def __init__(self, color: 'XtermColor'):
        self.color = color

    def __str__(self) -> str:
        return self()

    def __repr__(self) -> str:
        return str(self)

    def __format__(self, format_spec) -> str:
        return format(str(self), format_spec)

    def __call__(self, n: int = 3, c: str | None = None):
        if c is None:
            c = ' ' if self.color.is_background else '█'
        return self.color(c * n)


class XtermColor(str):
    code: int
    rgb: int
    name: str
    is_background: bool

    def __new__(cls, code: int, rgb: int, name: str, is_background: bool):
        chars = code_to_chars(code, is_background=is_background)
        color = str.__new__(cls, chars)
        color.code = code
        color.rgb = rgb
        color.name = name
        color.is_background = is_background
        return color

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__}('
            f'{self.code:03d}, 0x{self.rgb:06x}, {self.name!r}, is_background={self.is_background}'
            f')>'
        )

    def __call__(self, s: str | Type[NOTSET] = NOTSET, /) -> str:
        """Return the string surrounded by this color and a style reset"""
        if s is NOTSET:
            return str(self)
        else:
            return f'{self}{s}{RESET_ALL}'

    def reset(self) -> str:
        """Print the reset-all-styles escape sequence"""
        return RESET_ALL

    @functools.cached_property
    def swatch(self) -> _XtermColorSwatch:
        return _XtermColorSwatch(self)

    @functools.cached_property
    def r(self) -> int:
        return (self.rgb >> 24) & 0xFF

    @functools.cached_property
    def g(self) -> int:
        return (self.rgb >> 16) & 0xFF

    @functools.cached_property
    def b(self) -> int:
        return self.rgb & 0xFF

    @functools.cached_property
    def red(self) -> float:
        return self.r / 255.0

    @functools.cached_property
    def green(self) -> float:
        return self.g / 255.0

    @functools.cached_property
    def blue(self) -> float:
        return self.b / 255.0

    @functools.cached_property
    def hsv(self) -> tuple[float, float, float]:
        return colorsys.rgb_to_hsv(self.red, self.green, self.blue)

    @functools.cached_property
    def is_greyscale(self) -> bool:
        hue, saturation, value = self.hsv
        return saturation == 0.0

    @functools.cached_property
    def perceived_brightness(self) -> float:
        """Perceived brightness, according to the HSP colour model

        See https://alienryderflex.com/hsp.html
        """
        return math.sqrt(0.299 * self.red ** 2 + 0.587 * self.green ** 2 + 0.114 * self.blue ** 2)

    @functools.cached_property
    def is_bright(self) -> bool:
        return self.perceived_brightness >= 0.5

    @functools.cached_property
    def is_dark(self) -> bool:
        return self.perceived_brightness < 0.5

    @functools.cached_property  # type: ignore[misc]
    @requires_colormath
    def as_srgb_color(self) -> sRGBColor:
        return sRGBColor(self.red, self.green, self.blue)

    @functools.cached_property  # type: ignore[misc]
    @requires_colormath
    def as_lab_color(self) -> LabColor:
        return convert_color(self.as_srgb_color, LabColor)


# A collection of visually distinguishable colors, for use with colorizing identifiers
DEFAULT_DIFFERENTIATED_COLOR_NAMES = (
    'BLUE',
    'CADETBLUE',
    'CHARTREUSE1',
    'CORNFLOWERBLUE',
    'CYAN1',
    'DARKGOLDENROD',
    'DARKORANGE',
    'DEEPPINK1',
    'GOLD1',
    'DARKKHAKI',
    'HONEYDEW2',
    'MEDIUMVIOLETRED',
    'PURPLE',
    'WHEAT1',
    'YELLOW2',
    'ROSYBROWN',
    'MAROON',
    'LIGHTCYAN3',
    'HOTPINK',
    'GREY82',
    'LIGHTCORAL',
    'LIGHTSEAGREEN',
    'MEDIUMSPRINGGREEN',
    'OLIVE',
    'DODGERBLUE2',
    'ORANGERED1',
    'PALETURQUOISE1',
    'THISTLE3',
    'DARKTURQUOISE',
    'GREEN',
    'LIGHTGOLDENROD1',
    'LIGHTSALMON1',
    'PINK1',
    'NAVAJOWHITE1',
    'LIGHTSLATEBLUE',
    'LIGHTCYAN1',
    'GOLD3',
    'INDIANRED',
    'PURPLE',
    'SALMON1',
)


XTERM_256_COLOR_MAP = dict(

    # NOTE: these language= comments enable color swatch gutter icons in IDEA-based IDEs.
    #       Unfortunately, they only affect directly proceeding lines, so we must repeat ourselves.

    # language=css prefix=*{color: suffix=;}
    BLACK                = (0,   '#000000'),  # language=css prefix=*{color: suffix=;}
    MAROON               = (1,   '#800000'),  # language=css prefix=*{color: suffix=;}
    GREEN                = (2,   '#008000'),  # language=css prefix=*{color: suffix=;}
    OLIVE                = (3,   '#808000'),  # language=css prefix=*{color: suffix=;}
    NAVY                 = (4,   '#000080'),  # language=css prefix=*{color: suffix=;}
    PURPLE               = (5,   '#800080'),  # language=css prefix=*{color: suffix=;}
    TEAL                 = (6,   '#008080'),  # language=css prefix=*{color: suffix=;}
    SILVER               = (7,   '#c0c0c0'),  # language=css prefix=*{color: suffix=;}
    GREY                 = (8,   '#808080'),  # language=css prefix=*{color: suffix=;}
    RED                  = (9,   '#ff0000'),  # language=css prefix=*{color: suffix=;}
    LIME                 = (10,  '#00ff00'),  # language=css prefix=*{color: suffix=;}
    YELLOW               = (11,  '#ffff00'),  # language=css prefix=*{color: suffix=;}
    BLUE                 = (12,  '#0000ff'),  # language=css prefix=*{color: suffix=;}
    FUCHSIA              = (13,  '#ff00ff'),  # language=css prefix=*{color: suffix=;}
    AQUA                 = (14,  '#00ffff'),  # language=css prefix=*{color: suffix=;}
    WHITE                = (15,  '#ffffff'),  # language=css prefix=*{color: suffix=;}
    GREY0                = (16,  '#000000'),  # language=css prefix=*{color: suffix=;}
    NAVYBLUE             = (17,  '#00005f'),  # language=css prefix=*{color: suffix=;}
    DARKBLUE             = (18,  '#000087'),  # language=css prefix=*{color: suffix=;}
    BLUE3                = (19,  '#0000af'),  # language=css prefix=*{color: suffix=;}
    BLUE3_1              = (20,  '#0000d7'),  # language=css prefix=*{color: suffix=;}
    BLUE1                = (21,  '#0000ff'),  # language=css prefix=*{color: suffix=;}
    DARKGREEN            = (22,  '#005f00'),  # language=css prefix=*{color: suffix=;}
    DEEPSKYBLUE4         = (23,  '#005f5f'),  # language=css prefix=*{color: suffix=;}
    DEEPSKYBLUE4_1       = (24,  '#005f87'),  # language=css prefix=*{color: suffix=;}
    DEEPSKYBLUE4_2       = (25,  '#005faf'),  # language=css prefix=*{color: suffix=;}
    DODGERBLUE3          = (26,  '#005fd7'),  # language=css prefix=*{color: suffix=;}
    DODGERBLUE2          = (27,  '#005fff'),  # language=css prefix=*{color: suffix=;}
    GREEN4               = (28,  '#008700'),  # language=css prefix=*{color: suffix=;}
    SPRINGGREEN4         = (29,  '#00875f'),  # language=css prefix=*{color: suffix=;}
    TURQUOISE4           = (30,  '#008787'),  # language=css prefix=*{color: suffix=;}
    DEEPSKYBLUE3         = (31,  '#0087af'),  # language=css prefix=*{color: suffix=;}
    DEEPSKYBLUE3_1       = (32,  '#0087d7'),  # language=css prefix=*{color: suffix=;}
    DODGERBLUE1          = (33,  '#0087ff'),  # language=css prefix=*{color: suffix=;}
    GREEN3               = (34,  '#00af00'),  # language=css prefix=*{color: suffix=;}
    SPRINGGREEN3         = (35,  '#00af5f'),  # language=css prefix=*{color: suffix=;}
    DARKCYAN             = (36,  '#00af87'),  # language=css prefix=*{color: suffix=;}
    LIGHTSEAGREEN        = (37,  '#00afaf'),  # language=css prefix=*{color: suffix=;}
    DEEPSKYBLUE2         = (38,  '#00afd7'),  # language=css prefix=*{color: suffix=;}
    DEEPSKYBLUE1         = (39,  '#00afff'),  # language=css prefix=*{color: suffix=;}
    GREEN3_1             = (40,  '#00d700'),  # language=css prefix=*{color: suffix=;}
    SPRINGGREEN3_1       = (41,  '#00d75f'),  # language=css prefix=*{color: suffix=;}
    SPRINGGREEN2         = (42,  '#00d787'),  # language=css prefix=*{color: suffix=;}
    CYAN3                = (43,  '#00d7af'),  # language=css prefix=*{color: suffix=;}
    DARKTURQUOISE        = (44,  '#00d7d7'),  # language=css prefix=*{color: suffix=;}
    TURQUOISE2           = (45,  '#00d7ff'),  # language=css prefix=*{color: suffix=;}
    GREEN1               = (46,  '#00ff00'),  # language=css prefix=*{color: suffix=;}
    SPRINGGREEN2_1       = (47,  '#00ff5f'),  # language=css prefix=*{color: suffix=;}
    SPRINGGREEN1         = (48,  '#00ff87'),  # language=css prefix=*{color: suffix=;}
    MEDIUMSPRINGGREEN    = (49,  '#00ffaf'),  # language=css prefix=*{color: suffix=;}
    CYAN2                = (50,  '#00ffd7'),  # language=css prefix=*{color: suffix=;}
    CYAN1                = (51,  '#00ffff'),  # language=css prefix=*{color: suffix=;}
    DARKRED              = (52,  '#5f0000'),  # language=css prefix=*{color: suffix=;}
    DEEPPINK4            = (53,  '#5f005f'),  # language=css prefix=*{color: suffix=;}
    PURPLE4              = (54,  '#5f0087'),  # language=css prefix=*{color: suffix=;}
    PURPLE4_1            = (55,  '#5f00af'),  # language=css prefix=*{color: suffix=;}
    PURPLE3              = (56,  '#5f00d7'),  # language=css prefix=*{color: suffix=;}
    BLUEVIOLET           = (57,  '#5f00ff'),  # language=css prefix=*{color: suffix=;}
    ORANGE4              = (58,  '#5f5f00'),  # language=css prefix=*{color: suffix=;}
    GREY37               = (59,  '#5f5f5f'),  # language=css prefix=*{color: suffix=;}
    MEDIUMPURPLE4        = (60,  '#5f5f87'),  # language=css prefix=*{color: suffix=;}
    SLATEBLUE3           = (61,  '#5f5faf'),  # language=css prefix=*{color: suffix=;}
    SLATEBLUE3_1         = (62,  '#5f5fd7'),  # language=css prefix=*{color: suffix=;}
    ROYALBLUE1           = (63,  '#5f5fff'),  # language=css prefix=*{color: suffix=;}
    CHARTREUSE4          = (64,  '#5f8700'),  # language=css prefix=*{color: suffix=;}
    DARKSEAGREEN4        = (65,  '#5f875f'),  # language=css prefix=*{color: suffix=;}
    PALETURQUOISE4       = (66,  '#5f8787'),  # language=css prefix=*{color: suffix=;}
    STEELBLUE            = (67,  '#5f87af'),  # language=css prefix=*{color: suffix=;}
    STEELBLUE3           = (68,  '#5f87d7'),  # language=css prefix=*{color: suffix=;}
    CORNFLOWERBLUE       = (69,  '#5f87ff'),  # language=css prefix=*{color: suffix=;}
    CHARTREUSE3          = (70,  '#5faf00'),  # language=css prefix=*{color: suffix=;}
    DARKSEAGREEN4_1      = (71,  '#5faf5f'),  # language=css prefix=*{color: suffix=;}
    CADETBLUE            = (72,  '#5faf87'),  # language=css prefix=*{color: suffix=;}
    CADETBLUE_1          = (73,  '#5fafaf'),  # language=css prefix=*{color: suffix=;}
    SKYBLUE3             = (74,  '#5fafd7'),  # language=css prefix=*{color: suffix=;}
    STEELBLUE1           = (75,  '#5fafff'),  # language=css prefix=*{color: suffix=;}
    CHARTREUSE3_1        = (76,  '#5fd700'),  # language=css prefix=*{color: suffix=;}
    PALEGREEN3           = (77,  '#5fd75f'),  # language=css prefix=*{color: suffix=;}
    SEAGREEN3            = (78,  '#5fd787'),  # language=css prefix=*{color: suffix=;}
    AQUAMARINE3          = (79,  '#5fd7af'),  # language=css prefix=*{color: suffix=;}
    MEDIUMTURQUOISE      = (80,  '#5fd7d7'),  # language=css prefix=*{color: suffix=;}
    STEELBLUE1_1         = (81,  '#5fd7ff'),  # language=css prefix=*{color: suffix=;}
    CHARTREUSE2          = (82,  '#5fff00'),  # language=css prefix=*{color: suffix=;}
    SEAGREEN2            = (83,  '#5fff5f'),  # language=css prefix=*{color: suffix=;}
    SEAGREEN1            = (84,  '#5fff87'),  # language=css prefix=*{color: suffix=;}
    SEAGREEN1_1          = (85,  '#5fffaf'),  # language=css prefix=*{color: suffix=;}
    AQUAMARINE1          = (86,  '#5fffd7'),  # language=css prefix=*{color: suffix=;}
    DARKSLATEGRAY2       = (87,  '#5fffff'),  # language=css prefix=*{color: suffix=;}
    DARKRED_1            = (88,  '#870000'),  # language=css prefix=*{color: suffix=;}
    DEEPPINK4_1          = (89,  '#87005f'),  # language=css prefix=*{color: suffix=;}
    DARKMAGENTA          = (90,  '#870087'),  # language=css prefix=*{color: suffix=;}
    DARKMAGENTA_1        = (91,  '#8700af'),  # language=css prefix=*{color: suffix=;}
    DARKVIOLET           = (92,  '#8700d7'),  # language=css prefix=*{color: suffix=;}
    PURPLE_1             = (93,  '#8700ff'),  # language=css prefix=*{color: suffix=;}
    ORANGE4_1            = (94,  '#875f00'),  # language=css prefix=*{color: suffix=;}
    LIGHTPINK4           = (95,  '#875f5f'),  # language=css prefix=*{color: suffix=;}
    PLUM4                = (96,  '#875f87'),  # language=css prefix=*{color: suffix=;}
    MEDIUMPURPLE3        = (97,  '#875faf'),  # language=css prefix=*{color: suffix=;}
    MEDIUMPURPLE3_1      = (98,  '#875fd7'),  # language=css prefix=*{color: suffix=;}
    SLATEBLUE1           = (99,  '#875fff'),  # language=css prefix=*{color: suffix=;}
    YELLOW4              = (100, '#878700'),  # language=css prefix=*{color: suffix=;}
    WHEAT4               = (101, '#87875f'),  # language=css prefix=*{color: suffix=;}
    GREY53               = (102, '#878787'),  # language=css prefix=*{color: suffix=;}
    LIGHTSLATEGREY       = (103, '#8787af'),  # language=css prefix=*{color: suffix=;}
    MEDIUMPURPLE         = (104, '#8787d7'),  # language=css prefix=*{color: suffix=;}
    LIGHTSLATEBLUE       = (105, '#8787ff'),  # language=css prefix=*{color: suffix=;}
    YELLOW4_1            = (106, '#87af00'),  # language=css prefix=*{color: suffix=;}
    DARKOLIVEGREEN3      = (107, '#87af5f'),  # language=css prefix=*{color: suffix=;}
    DARKSEAGREEN         = (108, '#87af87'),  # language=css prefix=*{color: suffix=;}
    LIGHTSKYBLUE3        = (109, '#87afaf'),  # language=css prefix=*{color: suffix=;}
    LIGHTSKYBLUE3_1      = (110, '#87afd7'),  # language=css prefix=*{color: suffix=;}
    SKYBLUE2             = (111, '#87afff'),  # language=css prefix=*{color: suffix=;}
    CHARTREUSE2_1        = (112, '#87d700'),  # language=css prefix=*{color: suffix=;}
    DARKOLIVEGREEN3_1    = (113, '#87d75f'),  # language=css prefix=*{color: suffix=;}
    PALEGREEN3_1         = (114, '#87d787'),  # language=css prefix=*{color: suffix=;}
    DARKSEAGREEN3        = (115, '#87d7af'),  # language=css prefix=*{color: suffix=;}
    DARKSLATEGRAY3       = (116, '#87d7d7'),  # language=css prefix=*{color: suffix=;}
    SKYBLUE1             = (117, '#87d7ff'),  # language=css prefix=*{color: suffix=;}
    CHARTREUSE1          = (118, '#87ff00'),  # language=css prefix=*{color: suffix=;}
    LIGHTGREEN           = (119, '#87ff5f'),  # language=css prefix=*{color: suffix=;}
    LIGHTGREEN_1         = (120, '#87ff87'),  # language=css prefix=*{color: suffix=;}
    PALEGREEN1           = (121, '#87ffaf'),  # language=css prefix=*{color: suffix=;}
    AQUAMARINE1_1        = (122, '#87ffd7'),  # language=css prefix=*{color: suffix=;}
    DARKSLATEGRAY1       = (123, '#87ffff'),  # language=css prefix=*{color: suffix=;}
    RED3                 = (124, '#af0000'),  # language=css prefix=*{color: suffix=;}
    DEEPPINK4_2          = (125, '#af005f'),  # language=css prefix=*{color: suffix=;}
    MEDIUMVIOLETRED      = (126, '#af0087'),  # language=css prefix=*{color: suffix=;}
    MAGENTA3             = (127, '#af00af'),  # language=css prefix=*{color: suffix=;}
    DARKVIOLET_1         = (128, '#af00d7'),  # language=css prefix=*{color: suffix=;}
    PURPLE_2             = (129, '#af00ff'),  # language=css prefix=*{color: suffix=;}
    DARKORANGE3          = (130, '#af5f00'),  # language=css prefix=*{color: suffix=;}
    INDIANRED            = (131, '#af5f5f'),  # language=css prefix=*{color: suffix=;}
    HOTPINK3             = (132, '#af5f87'),  # language=css prefix=*{color: suffix=;}
    MEDIUMORCHID3        = (133, '#af5faf'),  # language=css prefix=*{color: suffix=;}
    MEDIUMORCHID         = (134, '#af5fd7'),  # language=css prefix=*{color: suffix=;}
    MEDIUMPURPLE2        = (135, '#af5fff'),  # language=css prefix=*{color: suffix=;}
    DARKGOLDENROD        = (136, '#af8700'),  # language=css prefix=*{color: suffix=;}
    LIGHTSALMON3         = (137, '#af875f'),  # language=css prefix=*{color: suffix=;}
    ROSYBROWN            = (138, '#af8787'),  # language=css prefix=*{color: suffix=;}
    GREY63               = (139, '#af87af'),  # language=css prefix=*{color: suffix=;}
    MEDIUMPURPLE2_1      = (140, '#af87d7'),  # language=css prefix=*{color: suffix=;}
    MEDIUMPURPLE1        = (141, '#af87ff'),  # language=css prefix=*{color: suffix=;}
    GOLD3                = (142, '#afaf00'),  # language=css prefix=*{color: suffix=;}
    DARKKHAKI            = (143, '#afaf5f'),  # language=css prefix=*{color: suffix=;}
    NAVAJOWHITE3         = (144, '#afaf87'),  # language=css prefix=*{color: suffix=;}
    GREY69               = (145, '#afafaf'),  # language=css prefix=*{color: suffix=;}
    LIGHTSTEELBLUE3      = (146, '#afafd7'),  # language=css prefix=*{color: suffix=;}
    LIGHTSTEELBLUE       = (147, '#afafff'),  # language=css prefix=*{color: suffix=;}
    YELLOW3              = (148, '#afd700'),  # language=css prefix=*{color: suffix=;}
    DARKOLIVEGREEN3_2    = (149, '#afd75f'),  # language=css prefix=*{color: suffix=;}
    DARKSEAGREEN3_1      = (150, '#afd787'),  # language=css prefix=*{color: suffix=;}
    DARKSEAGREEN2        = (151, '#afd7af'),  # language=css prefix=*{color: suffix=;}
    LIGHTCYAN3           = (152, '#afd7d7'),  # language=css prefix=*{color: suffix=;}
    LIGHTSKYBLUE1        = (153, '#afd7ff'),  # language=css prefix=*{color: suffix=;}
    GREENYELLOW          = (154, '#afff00'),  # language=css prefix=*{color: suffix=;}
    DARKOLIVEGREEN2      = (155, '#afff5f'),  # language=css prefix=*{color: suffix=;}
    PALEGREEN1_1         = (156, '#afff87'),  # language=css prefix=*{color: suffix=;}
    DARKSEAGREEN2_1      = (157, '#afffaf'),  # language=css prefix=*{color: suffix=;}
    DARKSEAGREEN1        = (158, '#afffd7'),  # language=css prefix=*{color: suffix=;}
    PALETURQUOISE1       = (159, '#afffff'),  # language=css prefix=*{color: suffix=;}
    RED3_1               = (160, '#d70000'),  # language=css prefix=*{color: suffix=;}
    DEEPPINK3            = (161, '#d7005f'),  # language=css prefix=*{color: suffix=;}
    DEEPPINK3_1          = (162, '#d70087'),  # language=css prefix=*{color: suffix=;}
    MAGENTA3_1           = (163, '#d700af'),  # language=css prefix=*{color: suffix=;}
    MAGENTA3_2           = (164, '#d700d7'),  # language=css prefix=*{color: suffix=;}
    MAGENTA2             = (165, '#d700ff'),  # language=css prefix=*{color: suffix=;}
    DARKORANGE3_1        = (166, '#d75f00'),  # language=css prefix=*{color: suffix=;}
    INDIANRED_1          = (167, '#d75f5f'),  # language=css prefix=*{color: suffix=;}
    HOTPINK3_1           = (168, '#d75f87'),  # language=css prefix=*{color: suffix=;}
    HOTPINK2             = (169, '#d75faf'),  # language=css prefix=*{color: suffix=;}
    ORCHID               = (170, '#d75fd7'),  # language=css prefix=*{color: suffix=;}
    MEDIUMORCHID1        = (171, '#d75fff'),  # language=css prefix=*{color: suffix=;}
    ORANGE3              = (172, '#d78700'),  # language=css prefix=*{color: suffix=;}
    LIGHTSALMON3_1       = (173, '#d7875f'),  # language=css prefix=*{color: suffix=;}
    LIGHTPINK3           = (174, '#d78787'),  # language=css prefix=*{color: suffix=;}
    PINK3                = (175, '#d787af'),  # language=css prefix=*{color: suffix=;}
    PLUM3                = (176, '#d787d7'),  # language=css prefix=*{color: suffix=;}
    VIOLET               = (177, '#d787ff'),  # language=css prefix=*{color: suffix=;}
    GOLD3_1              = (178, '#d7af00'),  # language=css prefix=*{color: suffix=;}
    LIGHTGOLDENROD3      = (179, '#d7af5f'),  # language=css prefix=*{color: suffix=;}
    TAN                  = (180, '#d7af87'),  # language=css prefix=*{color: suffix=;}
    MISTYROSE3           = (181, '#d7afaf'),  # language=css prefix=*{color: suffix=;}
    THISTLE3             = (182, '#d7afd7'),  # language=css prefix=*{color: suffix=;}
    PLUM2                = (183, '#d7afff'),  # language=css prefix=*{color: suffix=;}
    YELLOW3_1            = (184, '#d7d700'),  # language=css prefix=*{color: suffix=;}
    KHAKI3               = (185, '#d7d75f'),  # language=css prefix=*{color: suffix=;}
    LIGHTGOLDENROD2      = (186, '#d7d787'),  # language=css prefix=*{color: suffix=;}
    LIGHTYELLOW3         = (187, '#d7d7af'),  # language=css prefix=*{color: suffix=;}
    GREY84               = (188, '#d7d7d7'),  # language=css prefix=*{color: suffix=;}
    LIGHTSTEELBLUE1      = (189, '#d7d7ff'),  # language=css prefix=*{color: suffix=;}
    YELLOW2              = (190, '#d7ff00'),  # language=css prefix=*{color: suffix=;}
    DARKOLIVEGREEN1      = (191, '#d7ff5f'),  # language=css prefix=*{color: suffix=;}
    DARKOLIVEGREEN1_1    = (192, '#d7ff87'),  # language=css prefix=*{color: suffix=;}
    DARKSEAGREEN1_1      = (193, '#d7ffaf'),  # language=css prefix=*{color: suffix=;}
    HONEYDEW2            = (194, '#d7ffd7'),  # language=css prefix=*{color: suffix=;}
    LIGHTCYAN1           = (195, '#d7ffff'),  # language=css prefix=*{color: suffix=;}
    RED1                 = (196, '#ff0000'),  # language=css prefix=*{color: suffix=;}
    DEEPPINK2            = (197, '#ff005f'),  # language=css prefix=*{color: suffix=;}
    DEEPPINK1            = (198, '#ff0087'),  # language=css prefix=*{color: suffix=;}
    DEEPPINK1_1          = (199, '#ff00af'),  # language=css prefix=*{color: suffix=;}
    MAGENTA2_1           = (200, '#ff00d7'),  # language=css prefix=*{color: suffix=;}
    MAGENTA1             = (201, '#ff00ff'),  # language=css prefix=*{color: suffix=;}
    ORANGERED1           = (202, '#ff5f00'),  # language=css prefix=*{color: suffix=;}
    INDIANRED1           = (203, '#ff5f5f'),  # language=css prefix=*{color: suffix=;}
    INDIANRED1_1         = (204, '#ff5f87'),  # language=css prefix=*{color: suffix=;}
    HOTPINK              = (205, '#ff5faf'),  # language=css prefix=*{color: suffix=;}
    HOTPINK_1            = (206, '#ff5fd7'),  # language=css prefix=*{color: suffix=;}
    MEDIUMORCHID1_1      = (207, '#ff5fff'),  # language=css prefix=*{color: suffix=;}
    DARKORANGE           = (208, '#ff8700'),  # language=css prefix=*{color: suffix=;}
    SALMON1              = (209, '#ff875f'),  # language=css prefix=*{color: suffix=;}
    LIGHTCORAL           = (210, '#ff8787'),  # language=css prefix=*{color: suffix=;}
    PALEVIOLETRED1       = (211, '#ff87af'),  # language=css prefix=*{color: suffix=;}
    ORCHID2              = (212, '#ff87d7'),  # language=css prefix=*{color: suffix=;}
    ORCHID1              = (213, '#ff87ff'),  # language=css prefix=*{color: suffix=;}
    ORANGE1              = (214, '#ffaf00'),  # language=css prefix=*{color: suffix=;}
    SANDYBROWN           = (215, '#ffaf5f'),  # language=css prefix=*{color: suffix=;}
    LIGHTSALMON1         = (216, '#ffaf87'),  # language=css prefix=*{color: suffix=;}
    LIGHTPINK1           = (217, '#ffafaf'),  # language=css prefix=*{color: suffix=;}
    PINK1                = (218, '#ffafd7'),  # language=css prefix=*{color: suffix=;}
    PLUM1                = (219, '#ffafff'),  # language=css prefix=*{color: suffix=;}
    GOLD1                = (220, '#ffd700'),  # language=css prefix=*{color: suffix=;}
    LIGHTGOLDENROD2_1    = (221, '#ffd75f'),  # language=css prefix=*{color: suffix=;}
    LIGHTGOLDENROD2_2    = (222, '#ffd787'),  # language=css prefix=*{color: suffix=;}
    NAVAJOWHITE1         = (223, '#ffd7af'),  # language=css prefix=*{color: suffix=;}
    MISTYROSE1           = (224, '#ffd7d7'),  # language=css prefix=*{color: suffix=;}
    THISTLE1             = (225, '#ffd7ff'),  # language=css prefix=*{color: suffix=;}
    YELLOW1              = (226, '#ffff00'),  # language=css prefix=*{color: suffix=;}
    LIGHTGOLDENROD1      = (227, '#ffff5f'),  # language=css prefix=*{color: suffix=;}
    KHAKI1               = (228, '#ffff87'),  # language=css prefix=*{color: suffix=;}
    WHEAT1               = (229, '#ffffaf'),  # language=css prefix=*{color: suffix=;}
    CORNSILK1            = (230, '#ffffd7'),  # language=css prefix=*{color: suffix=;}
    GREY100              = (231, '#ffffff'),  # language=css prefix=*{color: suffix=;}
    GREY3                = (232, '#080808'),  # language=css prefix=*{color: suffix=;}
    GREY7                = (233, '#121212'),  # language=css prefix=*{color: suffix=;}
    GREY11               = (234, '#1c1c1c'),  # language=css prefix=*{color: suffix=;}
    GREY15               = (235, '#262626'),  # language=css prefix=*{color: suffix=;}
    GREY19               = (236, '#303030'),  # language=css prefix=*{color: suffix=;}
    GREY23               = (237, '#3a3a3a'),  # language=css prefix=*{color: suffix=;}
    GREY27               = (238, '#444444'),  # language=css prefix=*{color: suffix=;}
    GREY30               = (239, '#4e4e4e'),  # language=css prefix=*{color: suffix=;}
    GREY35               = (240, '#585858'),  # language=css prefix=*{color: suffix=;}
    GREY39               = (241, '#626262'),  # language=css prefix=*{color: suffix=;}
    GREY42               = (242, '#6c6c6c'),  # language=css prefix=*{color: suffix=;}
    GREY46               = (243, '#767676'),  # language=css prefix=*{color: suffix=;}
    GREY50               = (244, '#808080'),  # language=css prefix=*{color: suffix=;}
    GREY54               = (245, '#8a8a8a'),  # language=css prefix=*{color: suffix=;}
    GREY58               = (246, '#949494'),  # language=css prefix=*{color: suffix=;}
    GREY62               = (247, '#9e9e9e'),  # language=css prefix=*{color: suffix=;}
    GREY66               = (248, '#a8a8a8'),  # language=css prefix=*{color: suffix=;}
    GREY70               = (249, '#b2b2b2'),  # language=css prefix=*{color: suffix=;}
    GREY74               = (250, '#bcbcbc'),  # language=css prefix=*{color: suffix=;}
    GREY78               = (251, '#c6c6c6'),  # language=css prefix=*{color: suffix=;}
    GREY82               = (252, '#d0d0d0'),  # language=css prefix=*{color: suffix=;}
    GREY85               = (253, '#dadada'),  # language=css prefix=*{color: suffix=;}
    GREY89               = (254, '#e4e4e4'),  # language=css prefix=*{color: suffix=;}
    GREY93               = (255, '#eeeeee'),
)


# TODO(zk): convert to Enum class

class XtermCodes:
    all_colors: dict[str, XtermColor]
    bright_colors: dict[str, XtermColor]
    dark_colors: dict[str, XtermColor]
    by_code: dict[int, XtermColor]
    differentiated_colors: tuple[XtermColor, ...]

    def __init__(self):
        self.all_colors = {}
        self.bright_colors = {}
        self.dark_colors = {}
        self.by_code = {}

        for name, (code, rgb_hex_str) in XTERM_256_COLOR_MAP.items():
            rgb = int(rgb_hex_str[1:], 16)
            color = self._init_color(code, rgb, name)
            setattr(self, name, color)

            self.by_code[code] = color
            self.all_colors[name] = color
            if color.is_bright:
                self.bright_colors[name] = color
            else:
                self.dark_colors[name] = color

        self.differentiated_colors = tuple(
            cast(XtermColor, getattr(self, name))
            for name in DEFAULT_DIFFERENTIATED_COLOR_NAMES
        )

    def _init_color(self, code, rgb, name) -> XtermColor:
        raise NotImplementedError

    def __getitem__(self, item) -> XtermColor:
        if isinstance(item, str):
            return self.all_colors[item]
        else:
            return self.by_code[item]

    def __len__(self):
        return len(self.all_colors)

    BLACK: XtermColor
    MAROON: XtermColor
    GREEN: XtermColor
    OLIVE: XtermColor
    NAVY: XtermColor
    PURPLE: XtermColor
    TEAL: XtermColor
    SILVER: XtermColor
    GREY: XtermColor
    RED: XtermColor
    LIME: XtermColor
    YELLOW: XtermColor
    BLUE: XtermColor
    FUCHSIA: XtermColor
    AQUA: XtermColor
    WHITE: XtermColor
    GREY0: XtermColor
    NAVYBLUE: XtermColor
    DARKBLUE: XtermColor
    BLUE3: XtermColor
    BLUE3_1: XtermColor
    BLUE1: XtermColor
    DARKGREEN: XtermColor
    DEEPSKYBLUE4: XtermColor
    DEEPSKYBLUE4_1: XtermColor
    DEEPSKYBLUE4_2: XtermColor
    DODGERBLUE3: XtermColor
    DODGERBLUE2: XtermColor
    GREEN4: XtermColor
    SPRINGGREEN4: XtermColor
    TURQUOISE4: XtermColor
    DEEPSKYBLUE3: XtermColor
    DEEPSKYBLUE3_1: XtermColor
    DODGERBLUE1: XtermColor
    GREEN3: XtermColor
    SPRINGGREEN3: XtermColor
    DARKCYAN: XtermColor
    LIGHTSEAGREEN: XtermColor
    DEEPSKYBLUE2: XtermColor
    DEEPSKYBLUE1: XtermColor
    GREEN3_1: XtermColor
    SPRINGGREEN3_1: XtermColor
    SPRINGGREEN2: XtermColor
    CYAN3: XtermColor
    DARKTURQUOISE: XtermColor
    TURQUOISE2: XtermColor
    GREEN1: XtermColor
    SPRINGGREEN2_1: XtermColor
    SPRINGGREEN1: XtermColor
    MEDIUMSPRINGGREEN: XtermColor
    CYAN2: XtermColor
    CYAN1: XtermColor
    DARKRED: XtermColor
    DEEPPINK4: XtermColor
    PURPLE4: XtermColor
    PURPLE4_1: XtermColor
    PURPLE3: XtermColor
    BLUEVIOLET: XtermColor
    ORANGE4: XtermColor
    GREY37: XtermColor
    MEDIUMPURPLE4: XtermColor
    SLATEBLUE3: XtermColor
    SLATEBLUE3_1: XtermColor
    ROYALBLUE1: XtermColor
    CHARTREUSE4: XtermColor
    DARKSEAGREEN4: XtermColor
    PALETURQUOISE4: XtermColor
    STEELBLUE: XtermColor
    STEELBLUE3: XtermColor
    CORNFLOWERBLUE: XtermColor
    CHARTREUSE3: XtermColor
    DARKSEAGREEN4_1: XtermColor
    CADETBLUE: XtermColor
    CADETBLUE_1: XtermColor
    SKYBLUE3: XtermColor
    STEELBLUE1: XtermColor
    CHARTREUSE3_1: XtermColor
    PALEGREEN3: XtermColor
    SEAGREEN3: XtermColor
    AQUAMARINE3: XtermColor
    MEDIUMTURQUOISE: XtermColor
    STEELBLUE1_1: XtermColor
    CHARTREUSE2: XtermColor
    SEAGREEN2: XtermColor
    SEAGREEN1: XtermColor
    SEAGREEN1_1: XtermColor
    AQUAMARINE1: XtermColor
    DARKSLATEGRAY2: XtermColor
    DARKRED_1: XtermColor
    DEEPPINK4_1: XtermColor
    DARKMAGENTA: XtermColor
    DARKMAGENTA_1: XtermColor
    DARKVIOLET: XtermColor
    PURPLE_1: XtermColor
    ORANGE4_1: XtermColor
    LIGHTPINK4: XtermColor
    PLUM4: XtermColor
    MEDIUMPURPLE3: XtermColor
    MEDIUMPURPLE3_1: XtermColor
    SLATEBLUE1: XtermColor
    YELLOW4: XtermColor
    WHEAT4: XtermColor
    GREY53: XtermColor
    LIGHTSLATEGREY: XtermColor
    MEDIUMPURPLE: XtermColor
    LIGHTSLATEBLUE: XtermColor
    YELLOW4_1: XtermColor
    DARKOLIVEGREEN3: XtermColor
    DARKSEAGREEN: XtermColor
    LIGHTSKYBLUE3: XtermColor
    LIGHTSKYBLUE3_1: XtermColor
    SKYBLUE2: XtermColor
    CHARTREUSE2_1: XtermColor
    DARKOLIVEGREEN3_1: XtermColor
    PALEGREEN3_1: XtermColor
    DARKSEAGREEN3: XtermColor
    DARKSLATEGRAY3: XtermColor
    SKYBLUE1: XtermColor
    CHARTREUSE1: XtermColor
    LIGHTGREEN: XtermColor
    LIGHTGREEN_1: XtermColor
    PALEGREEN1: XtermColor
    AQUAMARINE1_1: XtermColor
    DARKSLATEGRAY1: XtermColor
    RED3: XtermColor
    DEEPPINK4_2: XtermColor
    MEDIUMVIOLETRED: XtermColor
    MAGENTA3: XtermColor
    DARKVIOLET_1: XtermColor
    PURPLE_2: XtermColor
    DARKORANGE3: XtermColor
    INDIANRED: XtermColor
    HOTPINK3: XtermColor
    MEDIUMORCHID3: XtermColor
    MEDIUMORCHID: XtermColor
    MEDIUMPURPLE2: XtermColor
    DARKGOLDENROD: XtermColor
    LIGHTSALMON3: XtermColor
    ROSYBROWN: XtermColor
    GREY63: XtermColor
    MEDIUMPURPLE2_1: XtermColor
    MEDIUMPURPLE1: XtermColor
    GOLD3: XtermColor
    DARKKHAKI: XtermColor
    NAVAJOWHITE3: XtermColor
    GREY69: XtermColor
    LIGHTSTEELBLUE3: XtermColor
    LIGHTSTEELBLUE: XtermColor
    YELLOW3: XtermColor
    DARKOLIVEGREEN3_2: XtermColor
    DARKSEAGREEN3_1: XtermColor
    DARKSEAGREEN2: XtermColor
    LIGHTCYAN3: XtermColor
    LIGHTSKYBLUE1: XtermColor
    GREENYELLOW: XtermColor
    DARKOLIVEGREEN2: XtermColor
    PALEGREEN1_1: XtermColor
    DARKSEAGREEN2_1: XtermColor
    DARKSEAGREEN1: XtermColor
    PALETURQUOISE1: XtermColor
    RED3_1: XtermColor
    DEEPPINK3: XtermColor
    DEEPPINK3_1: XtermColor
    MAGENTA3_1: XtermColor
    MAGENTA3_2: XtermColor
    MAGENTA2: XtermColor
    DARKORANGE3_1: XtermColor
    INDIANRED_1: XtermColor
    HOTPINK3_1: XtermColor
    HOTPINK2: XtermColor
    ORCHID: XtermColor
    MEDIUMORCHID1: XtermColor
    ORANGE3: XtermColor
    LIGHTSALMON3_1: XtermColor
    LIGHTPINK3: XtermColor
    PINK3: XtermColor
    PLUM3: XtermColor
    VIOLET: XtermColor
    GOLD3_1: XtermColor
    LIGHTGOLDENROD3: XtermColor
    TAN: XtermColor
    MISTYROSE3: XtermColor
    THISTLE3: XtermColor
    PLUM2: XtermColor
    YELLOW3_1: XtermColor
    KHAKI3: XtermColor
    LIGHTGOLDENROD2: XtermColor
    LIGHTYELLOW3: XtermColor
    GREY84: XtermColor
    LIGHTSTEELBLUE1: XtermColor
    YELLOW2: XtermColor
    DARKOLIVEGREEN1: XtermColor
    DARKOLIVEGREEN1_1: XtermColor
    DARKSEAGREEN1_1: XtermColor
    HONEYDEW2: XtermColor
    LIGHTCYAN1: XtermColor
    RED1: XtermColor
    DEEPPINK2: XtermColor
    DEEPPINK1: XtermColor
    DEEPPINK1_1: XtermColor
    MAGENTA2_1: XtermColor
    MAGENTA1: XtermColor
    ORANGERED1: XtermColor
    INDIANRED1: XtermColor
    INDIANRED1_1: XtermColor
    HOTPINK: XtermColor
    HOTPINK_1: XtermColor
    MEDIUMORCHID1_1: XtermColor
    DARKORANGE: XtermColor
    SALMON1: XtermColor
    LIGHTCORAL: XtermColor
    PALEVIOLETRED1: XtermColor
    ORCHID2: XtermColor
    ORCHID1: XtermColor
    ORANGE1: XtermColor
    SANDYBROWN: XtermColor
    LIGHTSALMON1: XtermColor
    LIGHTPINK1: XtermColor
    PINK1: XtermColor
    PLUM1: XtermColor
    GOLD1: XtermColor
    LIGHTGOLDENROD2_1: XtermColor
    LIGHTGOLDENROD2_2: XtermColor
    NAVAJOWHITE1: XtermColor
    MISTYROSE1: XtermColor
    THISTLE1: XtermColor
    YELLOW1: XtermColor
    LIGHTGOLDENROD1: XtermColor
    KHAKI1: XtermColor
    WHEAT1: XtermColor
    CORNSILK1: XtermColor
    GREY100: XtermColor
    GREY3: XtermColor
    GREY7: XtermColor
    GREY11: XtermColor
    GREY15: XtermColor
    GREY19: XtermColor
    GREY23: XtermColor
    GREY27: XtermColor
    GREY30: XtermColor
    GREY35: XtermColor
    GREY39: XtermColor
    GREY42: XtermColor
    GREY46: XtermColor
    GREY50: XtermColor
    GREY54: XtermColor
    GREY58: XtermColor
    GREY62: XtermColor
    GREY66: XtermColor
    GREY70: XtermColor
    GREY74: XtermColor
    GREY78: XtermColor
    GREY82: XtermColor
    GREY85: XtermColor
    GREY89: XtermColor
    GREY93: XtermColor


class XtermFore(XtermCodes):
    def _init_color(self, code, rgb, name) -> XtermColor:
        return XtermColor(code, rgb, name, is_background=False)


class XtermBack(XtermFore):
    def _init_color(self, code, rgb, name) -> XtermColor:
        return XtermColor(code, rgb, name, is_background=True)


Fore256 = XtermFore()
Back256 = XtermBack()
