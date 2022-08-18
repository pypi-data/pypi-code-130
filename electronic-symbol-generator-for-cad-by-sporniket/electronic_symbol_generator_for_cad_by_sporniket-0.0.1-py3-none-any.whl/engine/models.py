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
from typing import List, Dict, Union
from electronic_package_descriptor import PinDescription


class RailOfPins:
    """
    Collection of pins to put on one side of a component symbol.

    The pins may be separated by an arbitrary numbers of 'None' items to create spacing.

    A rail has a length and a width. The length count the number of pins, the width count the max length of a pin name.
    """

    def __init__(self):
        self.items = []
        self.width = 0

    @property
    def length(self) -> int:
        return len(self.items)

    def updateWidth(self, pins: List[PinDescription]):
        self.width = max(
            [self.width]
            + [
                0 if p is None else len("".join(c for c in p.name if c not in "~")) + 1
                for p in pins
            ]
        )

    def push(self, pins: List[PinDescription], *, withSeparator=False):
        if len(pins) > 0:
            if withSeparator and self.length > 0:
                self.items.append(None)
            self.items.extend(pins)
            self.updateWidth(pins)

    def pushSinglePin(self, pin: PinDescription):
        self.push([pin])

    def fillToLength(self, lengthToReach: int):
        delta = lengthToReach - self.length
        if delta > 0:
            self.items += [None for p in range(delta)]

    def fillToLengthBefore(self, lengthToReach: int):
        delta = lengthToReach - self.length
        if delta > 0:
            self.items = [None for p in range(delta)] + self.items

    def fillToLengthCentered(self, lengthToReach: int):
        delta = lengthToReach - self.length
        if delta > 0:
            countBefore = 0 if delta < 2 else int(delta / 2)
            self.items = (
                [None for p in range(countBefore)]
                + self.items
                + [None for p in range(delta - countBefore)]
            )

    def trim(self):
        """
        Removes any ``None`` elements before the first actual pin and after the last actual pin.
        """
        indexOfFirst = 0
        for p in self.items:
            if p != None:
                break
            indexOfFirst += 1

        indexOfLast = self.length
        for p in reversed(self.items):
            if p != None:
                break
            indexOfLast -= 1

        self.items = self.items[indexOfFirst:indexOfLast]

    def equalize(self, rail: "RailOfPins"):
        """
        Make this rail and the provided one have the same length.

        Args:
            rail (RailOfPins): the rail to equalize with.
        """
        if self.length < rail.length:
            self.fillToLength(rail.length)
        elif self.length > rail.length:
            rail.fillToLength(self.length)


class RectangularHolderOfRailsOfPins:
    """
    Model of an electronic graphic symbol consisting of a rectangle that can have pins on each side.
    """

    def __init__(self):
        self.north = RailOfPins()
        self.east = RailOfPins()
        self.south = RailOfPins()
        self.west = RailOfPins()

    @property
    def paddingNorth(self) -> int:
        """
        Padding from the north side.

        Returns:
            int: padding
        """
        return int(self.north.width / 2 + 1 if self.north.width > 0 else 0)

    @property
    def paddingWest(self) -> int:
        """
        Padding from the West side.

        Returns:
            int: padding
        """
        return int(self.west.width / 2 + 1 if self.west.width > 0 else 0)

    @property
    def paddingSouth(self) -> int:
        """
        Padding from the south side.

        Returns:
            int: padding
        """
        return int(self.south.width / 2 + 1 if self.south.width > 0 else 0)

    @property
    def paddingEast(self) -> int:
        """
        Padding from the east side.

        Returns:
            int: padding
        """
        return int(self.east.width / 2 + 1 if self.east.width > 0 else 0)

    @property
    def width(self) -> int:
        return (
            (
                self.north.length
                if self.north.length > self.south.length
                else self.south.length
            )
            + self.paddingWest
            + self.paddingEast
            + 1  # to add a space before rendering the first pin
        )

    @property
    def height(self) -> int:
        return (
            (
                self.west.length
                if self.west.length > self.east.length
                else self.east.length
            )
            + self.paddingNorth
            + self.paddingSouth
            + 1  # to add a space before rendering the first pin
        )
