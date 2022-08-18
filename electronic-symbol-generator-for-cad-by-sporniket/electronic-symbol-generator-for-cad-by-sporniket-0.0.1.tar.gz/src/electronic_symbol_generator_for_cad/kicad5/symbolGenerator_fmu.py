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
from typing import List, Dict

from electronic_package_descriptor import *
from ..symbolGenerator import (
    SymbolGenerator,
    SingleSymbolGenerator,
    writeLinesWithSeparator,
)
from ..engine import (
    RectangularHolderOfRailsOfPins,
    LayoutManagerForSingleGroup,
    typesOfPowerDistributionPins,
)

from .comments import *
from .pins import *
from .symbols import *
from .metrics import metrics


class SymbolGeneratorForKicad5_Functionnal_MultiUnit(SingleSymbolGenerator):
    """
    Symbol generator for functionnal, multi-unit symbols.

    Given that each unit will have a variable width, depending on the pins of the unit :
    * the top-left corner of the main rectangle will be stucked at (0,0)
    * the text fields and the text describing the unit will be tacked at x = 0 and just above the main rectangle
      (no pins on the north side of the unit, ever)
    """

    def __init__(self, p: PackageDescription, m: Dict[str, int] = metrics):
        self.p = p
        self.metrics = m

    @property
    def suffix(self) -> str:
        return "_mu"

    @property
    def title(self) -> str:
        return f"{self.p.name} -- Multiple units symbol"

    def renderGroup(
        self, g: GroupOfPins, spacing: int, currentUnit: int, result: List[str]
    ):
        # prolog
        result.extend(toSubtitle(f"{g.designator} -- {g.comment}"))
        # specific text
        result += toText(g.comment, 0, 100, currentUnit)
        # pins
        # -- prepare rails
        main = LayoutManagerForSingleGroup(g).apply()
        result.extend(
            toSurface(
                0,
                0,
                spacing * main.width,
                -spacing * main.height,
                currentUnit,
            )
        )
        result.extend(
            toStackOfPins(
                0,
                spacing * main.paddingNorth,
                SideOfComponent.WEST,
                spacing,
                [None] + main.west.items,
                currentUnit,
            ),
        )
        result.extend(
            toStackOfPins(
                spacing * main.width,
                spacing * main.paddingNorth,
                SideOfComponent.EAST,
                spacing,
                [None] + main.east.items,
                currentUnit,
            ),
        )
        result.extend(
            toStackOfPins(
                spacing * main.paddingWest,
                -spacing * main.height,
                SideOfComponent.SOUTH,
                spacing,
                [None] + main.south.items,
                currentUnit,
            ),
        )
        # epilog

    @property
    def symbol(self) -> List[str]:
        result = []
        # --- prepare ---
        ungroupedOthers = [
            pin
            for pin in self.p.ungroupedPins
            if pin.type not in typesOfPowerDistributionPins
        ]
        ungroupedPower = [
            pin
            for pin in self.p.ungroupedPins
            if pin.type in typesOfPowerDistributionPins
        ]
        numberOfUnits = (
            len(self.p.groupedPins)
            + (1 if len(ungroupedOthers) > 0 else 0)
            + (1 if len(ungroupedPower) > 0 else 0)
        )

        # --- generate statements ---
        spacing = metrics["spacing"]
        # prolog
        result.extend(toTitle(self.title))
        # main text
        result.extend(toBeginSymbol((self.p.name + self.suffix).upper(), numberOfUnits))
        if len(self.p.aliases) > 0:
            result.extend(toAliases([a + self.suffix for a in self.p.aliases]))
        result += toFieldVisible(0, self.p.prefix, 0, 300, StyleOfField.NORMAL)
        result += toFieldVisible(1, self.p.name, 0, 200, StyleOfField.BOLD)
        if self.p.footprintDesignator != None:
            result += toFieldInvisible(
                2, self.p.footprintDesignator, 0, 400, StyleOfField.NORMAL
            )
        if self.p.datasheet != None:
            result += toFieldInvisible(3, self.p.datasheet, 0, 500, StyleOfField.NORMAL)
        result.extend(toBeginDraw())

        currentUnit = 1
        for g in self.p.groupedPins:
            self.renderGroup(g, spacing, currentUnit, result)
            currentUnit += 1
        # ungrouped pins : others (no pwr, opwr or gnd)
        if len(ungroupedOthers) > 0:
            self.renderGroup(
                GroupOfPins("OTHERS", 9998, "Other pins", ungroupedOthers),
                spacing,
                currentUnit,
                result,
            )
            currentUnit += 1
        # ungrouped pins : power distribution (pwr, opwr and gnd)
        if len(ungroupedPower) > 0:
            self.renderGroup(
                GroupOfPins("POWER", 9999, "Power distribution", ungroupedPower),
                spacing,
                currentUnit,
                result,
            )
            currentUnit += 1
        # epilog
        result.extend(toEndDraw())
        result.extend(toEndSymbol())
        return result
