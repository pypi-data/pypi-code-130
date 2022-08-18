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

from electronic_package_descriptor import PinDescription, TypeOfPin


class SideOfComponent(Enum):
    """
    The 4 sides of a components will be designated like when looking at a map from above.
    """

    NORTH = "n"  # ^
    EAST = "e"  # -->
    SOUTH = "s"  # v
    WEST = "w"  # <--


# pin type to kicad electrical type
elecTypeByValueOfTypeOfPin = {
    "PWR": "W",
    "GND": "W",
    "DNC": "N",
    "I": "I",
    "ICLK": "I",
    "O": "O",
    "OCLK": "O",
    "O3": "T",
    "OCOL": "C",
    "OEMT": "E",
    "OPSV": "P",
    "OPWR": "w",
    "B3": "T",
    "B": "B",
}

# pin type to kicad pin shape
shapeTypeByValueOfTypeOfPin = {
    "PWR": "",
    "GND": "",
    "DNC": "",
    "I": "",
    "ICLK": "C",
    "O": "",
    "OCLK": "C",
    "O3": "",
    "OCOL": "",
    "OEMT": "",
    "OPSV": "",
    "OPWR": "",
    "B3": "",
    "B": "",
}


def toPinTowardsWest(
    name: str, index: int, x: int, y: int, elecType: str, shapeType: str, unit: int = 0
) -> List[str]:
    """
    Generate a pin that will touch the component at ``(x,y)``, and will point toward the left of the sheet.

    The pin has a width of 300 mils
    """
    return [
        f"X {name} {index} {x - 300} {y} 300 R 50 50 {unit} 0 {elecType} {shapeType}"
    ]


def toPinTowardsEast(
    name: str, index: int, x: int, y: int, elecType: str, shapeType: str, unit: int = 0
) -> List[str]:
    """
    Generate a pin that will touch the component at ``(x,y)``, and will point toward the right of the sheet.

    The pin has a width of 300 mils
    """
    return [
        f"X {name} {index} {x + 300} {y} 300 L 50 50 {unit} 0 {elecType} {shapeType}"
    ]


def toPinTowardsNorth(
    name: str, index: int, x: int, y: int, elecType: str, shapeType: str, unit: int = 0
) -> List[str]:
    """
    Generate a pin that will touch the component at ``(x,y)``, and will point toward the top of the sheet.

    The pin has a width of 300 mils
    """
    return [
        f"X {name} {index} {x} {y + 300} 300 D 50 50 {unit} 0 {elecType} {shapeType}"
    ]


def toPinTowardsSouth(
    name: str, index: int, x: int, y: int, elecType: str, shapeType: str, unit: int = 0
) -> List[str]:
    """
    Generate a pin that will touch the component at ``(x,y)``, and will point toward the bottom of the sheet.

    The pin has a width of 300 mils
    """
    return [
        f"X {name} {index} {x} {y - 300} 300 U 50 50 {unit} 0 {elecType} {shapeType}"
    ]


toPinBySideOfComponent = {
    "n": toPinTowardsNorth,
    "e": toPinTowardsEast,
    "s": toPinTowardsSouth,
    "w": toPinTowardsWest,
}


def toStackOfPins(
    x: int,
    y: int,
    sideOfComponent: SideOfComponent,
    offset: int,
    pins: List[PinDescription],
    unit: int = 0,
    *,
    forcePassive: bool = False,
) -> List[str]:
    locx = x
    locy = y
    dx = (
        offset
        if sideOfComponent == SideOfComponent.NORTH
        or sideOfComponent == SideOfComponent.SOUTH
        else 0
    )
    dy = (
        -offset
        if sideOfComponent == SideOfComponent.EAST
        or sideOfComponent == SideOfComponent.WEST
        else 0
    )
    toPin = toPinBySideOfComponent[sideOfComponent.value]
    result = []
    for pin in pins:
        if pin != None:
            typeOfPin = (
                TypeOfPin.OUTPUT_PASSIVE.value if forcePassive else pin.type.value
            )
            result.extend(
                toPin(
                    pin.name,
                    pin.designator.fullname,
                    locx,
                    locy,
                    elecTypeByValueOfTypeOfPin[typeOfPin],
                    shapeTypeByValueOfTypeOfPin[typeOfPin],
                    unit,
                )
            )
        locx += dx
        locy += dy
    return result
