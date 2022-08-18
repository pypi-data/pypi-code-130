"""
---
(c) 2022 David SPORN
---
This is part of Electronic Symbol Generator for CAD.

Electronic Symbol Generator for CAD is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

Electronic Symbol Generator for CAD is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.

See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Electronic Symbol Generator for CAD.
If not, see <https://www.gnu.org/licenses/>. 
---
"""

from typing import List
from enum import Enum


class StyleOfField(Enum):
    NORMAL = "NN"
    ITALIC = "IN"
    BOLD = "NB"
    BOLD_ITALIC = "IB"


def toBeginSymbolSet(name: str) -> List[str]:
    return [
        "EESchema-LIBRARY Version 2.4",
        "#encoding utf-8",
        "#",
        "#",
        f"# Symbol set of : {name}",
        "#",
    ]


def toEndSymbolSet() -> List[str]:
    return ["#", "#End Library"]


def toBeginSymbol(name: str, count: int = 1) -> List[str]:
    """
    Start a symbol description with the given name an unit count (MUST be >= 1).
    """
    validCount = max(1, count)
    return [f"DEF {name} U 0 50 Y Y {validCount} L N"]


def toAliases(aliases: List[str]) -> List[str]:
    return [f"ALIAS {' '.join(aliases).upper()}"]


def toEndSymbol() -> List[str]:
    return ["ENDDEF"]


def toBeginDraw() -> List[str]:
    return ["DRAW"]


def toEndDraw() -> List[str]:
    return ["ENDDRAW"]


def toFieldVisible(
    index: int, name: str, x: int, y: int, style: StyleOfField
) -> List[str]:
    return [f'F{index} "{name}" {x} {y} 50 H V L T{style.value}']


def toFieldInvisible(
    index: int, name: str, x: int, y: int, style: StyleOfField
) -> List[str]:
    return [f'F{index} "{name}" {x} {y} 50 H I L T{style.value}']


def toContour(x1: int, y1: int, x2: int, y2: int, unit: int = 0) -> List[str]:
    return [f"S {x1} {y1} {x2} {y2} {unit} 0 10 N"]


def toSurface(x1: int, y1: int, x2: int, y2: int, unit: int = 0) -> List[str]:
    return [f"S {x1} {y1} {x2} {y2} {unit} 0 10 f"]


def toText(message: str, x: int, y: int, unit: int = 0) -> List[str]:
    return [f'T 0 {x} {y} 50 1 {unit} 0 "{message}" Normal 0 L T']
