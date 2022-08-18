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
from electronic_package_descriptor import *

from .models import RectangularHolderOfRailsOfPins

typesOfPowerDistributionPins = (
    TypeOfPin.POWER,
    TypeOfPin.OUTPUT_POWER,
    TypeOfPin.GROUND,
)


class LayoutManager:
    """
    Interface to implement.

    Subclass this class, define a constructor with any appliable parameters, then use apply to regenerate a the model of the symbol pins.
    """

    def apply(self) -> RectangularHolderOfRailsOfPins:
        return RailOfPins()


class LayoutManagerForSingleUnit(LayoutManager):
    def __init__(self, p: PackageDescription):
        self.p = p
        self.outlineThrough = (
            []
        )  # List of separator outline from west to east side : (top, length)
        self.outlineWest = (
            []
        )  # List of separator outline on the west side : (top, length)
        self.outlineEast = (
            []
        )  # List of separator outline on the east side : (top, length)

    def placeUngroupedPins(self, r: RectangularHolderOfRailsOfPins()):
        # to north
        powerIns = []
        inputs = []
        powerOut = []
        # to south
        grounds = []
        dncs = []
        bidis = []
        outputs = []
        # shuffle
        for pin in self.p.ungroupedPins:
            if pin.type == TypeOfPin.POWER:
                powerIns.append(pin)
            elif pin.type == TypeOfPin.OUTPUT_POWER:
                powerOut.append(pin)
            elif pin.type == TypeOfPin.GROUND:
                grounds.append(pin)
            elif pin.type == TypeOfPin.DO_NOT_CONNECT:
                dncs.append(pin)
            elif pin.directionnality == Directionnality.IN:
                inputs.append(pin)
            elif pin.directionnality == Directionnality.OUT:
                outputs.append(pin)
            elif pin.directionnality == Directionnality.BI:
                bidis.append(pin)
            else:
                print(
                    f"WARN -- unsupported pin {pin.designator.fullname}, type {pin.type}, directionnality {pin.directionnality}"
                )
        # build north side
        for l in [powerIns, inputs, powerOut]:
            r.north.push(l, withSeparator=True)
        for l in [grounds, dncs, bidis, outputs]:
            r.south.push(l, withSeparator=True)
        # center north and south
        if r.north.length > r.south.length:
            r.south.fillToLengthCentered(r.north.length)
        elif r.north.length < r.south.length:
            r.north.fillToLengthCentered(r.south.length)

    def appendBidirectionnalGroupToHolder(
        self, g: GroupOfPins, main: RectangularHolderOfRailsOfPins
    ) -> int:
        """
        Place the pins of the groups on the west and east side of the provided holder, and return the occupied length of the section.

        Args:
            g (GroupOfPins): the group of pins to append
            main (RectangularHolderOfRailsOfPins): the holder of the pins

        Returns:
            int: the length of pins added to both sides.
        """

    def apply(self) -> RectangularHolderOfRailsOfPins:
        result = RectangularHolderOfRailsOfPins()
        outlineThrough = []
        outlineWest = []
        outlineEast = []

        # algorithm

        # -- process ungrouped pins
        self.placeUngroupedPins(result)

        # retrieve grouped pins, append group of ungrouped others if any.
        separatorAtWest = result.west.length
        separatorAtEast = separatorAtWest
        # -- shuffle groups
        bidibuses = []
        bidis = []
        inputs = []
        outputs = []
        for g in sorted(self.p.groupedPins, key=lambda g: g.rank):
            if g.directionnality == Directionnality.BI:
                if g.pattern == PatternOfGroup.BUS:
                    bidibuses.append(g)
                else:
                    bidis.append(g)
            elif g.directionnality == Directionnality.IN:
                inputs.append(g)
            elif g.directionnality == Directionnality.OUT:
                outputs.append(g)
            else:
                print(
                    f"WARN - unsupported group '{g.designator}', rank {g.rank}, directionnality {g.directionnality}, comment : {g.comment}"
                )
        # -- place bidis
        if len(bidis) > 0:
            outlineThrough.append(separatorAtWest)
            for g in bidis:
                # spacing before
                result.west.pushSinglePin(None)
                result.east.pushSinglePin(None)
                slots = g.slots
                if g.pattern == PatternOfGroup.AMPOP_IO:
                    ins = slots["in"]
                    result.west.push([ins[0], None, ins[1]])
                    result.east.push([None] + slots["out"] + [None])
                elif g.pattern == PatternOfGroup.POWER:
                    result.west.push(slots["in"])
                    result.east.push(slots["out"])
                else:
                    # -- general case, bidirectionnal
                    hasTwoGroupAtWest = (
                        0 if "in" not in slots or "others" not in slots else 1
                    )
                    expectedLengthWest = (
                        (0 if "in" not in slots else len(slots["in"]))
                        + (0 if "others" not in slots else len(slots["in"]))
                        + hasTwoGroupAtWest
                    )

                    hasTwoGroupsAtEast = (
                        0 if "out" not in slots or "bi" not in slots else 1
                    )
                    expectedLengthEast = (
                        (0 if "out" not in slots else len(slots["out"]))
                        + (0 if "bi" not in slots else len(slots["bi"]))
                        + hasTwoGroupsAtEast
                    )
                    fillerSizeWest = (
                        0
                        if expectedLengthWest >= expectedLengthEast
                        else expectedLengthEast - expectedLengthWest
                    )
                    fillerSizeEast = (
                        0
                        if expectedLengthEast >= expectedLengthWest
                        else expectedLengthWest - expectedLengthEast
                    )
                    # -- build west rail
                    if "in" in slots:
                        result.west.push(slots["in"])
                    if hasTwoGroupAtWest == 1:
                        result.west.pushSinglePin(None)
                    if fillerSizeWest > 0:
                        result.west.push([None for p in range(fillerSizeWest)])
                    if "others" in slots:
                        result.west.push(slots["others"])

                    # -- build east rail
                    if "out" in slots:
                        result.east.push(slots["out"])
                    if hasTwoGroupsAtEast == 1:
                        result.east.pushSinglePin(None)
                    if fillerSizeEast > 0:
                        result.east.push([None for p in range(fillerSizeEast)])
                    if "bi" in slots:
                        result.east.push(slots["bi"])
                separatorAtWest = result.west.length
                separatorAtEast = separatorAtWest
                outlineThrough.append(separatorAtWest)
        # -- place inputs
        outlineWest.append(separatorAtWest)
        if len(inputs) > 0:
            for g in inputs:
                # spacing before
                result.west.pushSinglePin(None)
                slots = g.slots
                if g.pattern == PatternOfGroup.BUS:
                    result.west.push(slots["bus"])
                else:
                    hasTwoGroupAtWest = (
                        0 if "in" not in slots or "others" not in slots else 1
                    )
                    if "in" in slots:
                        result.west.push(slots["in"])
                    if hasTwoGroupAtWest == 1:
                        result.west.pushSinglePin(None)
                    if "others" in slots:
                        result.west.push(slots["others"])
                separatorAtWest = result.west.length
                outlineWest.append(separatorAtWest)
        # -- place outputs
        outlineEast.append(separatorAtEast)
        if len(outputs) > 0:
            for g in outputs:
                # spacing before
                result.east.pushSinglePin(None)
                slots = g.slots
                if g.pattern == PatternOfGroup.BUS:
                    result.east.push(slots["bus"])
                else:
                    hasTwoGroupAtEast = (
                        0 if "out" not in slots or "bi" not in slots else 1
                    )
                    if "out" in slots:
                        result.east.push(slots["out"])
                    if hasTwoGroupAtEast == 1:
                        result.east.pushSinglePin(None)
                    if "bi" in slots:
                        result.east.push(slots["bi"])
                separatorAtEast = result.east.length
                outlineEast.append(separatorAtEast)
        # -- place bidirectionnal buses, in reversed order by size, to
        if len(bidibuses) > 0:
            # distribute bidirectionnal buses evenly (pin-count wise)
            # by first sorting by size in reverse order,
            # then append each group to the shorter side.
            toWest = True if result.west.length <= result.east.length else False
            rail = result.west if toWest else result.east
            outline = outlineWest if toWest else outlineEast
            for g in sorted(bidibuses, key=lambda g: len(g.pins), reverse=True):
                # spacing before
                rail.pushSinglePin(None)
                rail.push(g.slots["bus"])
                outline.append(rail.length)
                # assess next side to append to
                toWest = True if result.west.length <= result.east.length else False
                rail = result.west if toWest else result.east
                outline = outlineWest if toWest else outlineEast
        # final spacing
        result.west.pushSinglePin(None)
        result.east.pushSinglePin(None)

        # save the outline points
        self.outlineThrough = outlineThrough
        self.outlineWest = outlineWest
        self.outlineEast = outlineEast

        # ready to render
        return result


class LayoutManagerForSingleGroup(LayoutManager):
    def __init__(self, g: GroupOfPins):
        self.g = g

    def apply(self) -> RectangularHolderOfRailsOfPins:
        main = RectangularHolderOfRailsOfPins()
        slots = self.g.slots
        if self.g.pattern == PatternOfGroup.BUS:
            if self.g.directionnality == Directionnality.IN:
                main.west.push(slots["bus"])
            else:
                main.east.push(slots["bus"])
        elif self.g.pattern == PatternOfGroup.AMPOP_IO:
            ins = slots["in"]
            main.west.push([ins[0], None, ins[1]])
            main.east.push([None] + slots["out"] + [None])
        elif self.g.pattern == PatternOfGroup.AMPOP_VREF:
            ins = slots["in"]
            main.north.pushSinglePin(ins[0])
            main.south.pushSinglePin(ins[1])
        elif self.g.pattern == PatternOfGroup.POWER:
            main.west.push(slots["in"])
            main.south.push(slots["out"])
        else:
            # -- compute building metrics
            expectedLengthWest = 0 if "in" not in slots else len(slots["in"])

            hasTwoGroupsAtEast = 0 if "out" not in slots or "bi" not in slots else 1
            expectedLengthEast = (
                (0 if "out" not in slots else len(slots["out"]))
                + (0 if "bi" not in slots else len(slots["bi"]))
                + (0 if "out" not in slots or "bi" not in slots else 1)
            )
            fillerSizeWest = (
                0
                if expectedLengthWest >= expectedLengthEast
                else expectedLengthEast - expectedLengthWest
            )
            fillerSizeEast = (
                0
                if expectedLengthEast >= expectedLengthWest
                else expectedLengthWest - expectedLengthEast
            )
            # -- build west rail
            if "in" in slots:
                main.west.push(slots["in"])
            if fillerSizeWest > 0:
                main.west.push([None for p in range(fillerSizeWest)])
            # -- build east rail
            if "out" in slots:
                main.east.push(slots["out"])
            if hasTwoGroupsAtEast == 1:
                main.east.pushSinglePin(None)
            if fillerSizeEast > 0:
                main.east.push([None for p in range(fillerSizeEast)])
            if "bi" in slots:
                main.east.push(slots["bi"])
        # manage others
        if "others" in slots:
            others = slots["others"]
            # -- pins that are not power/ground
            needSpacerAtEast = True if main.east.length > 0 else False
            for pin in others:
                if pin.type not in typesOfPowerDistributionPins:
                    if needSpacerAtEast:
                        main.east.push([None, pin])
                        needSpacerAtEast = False
                    else:
                        main.east.pushSinglePin(pin)

            # -- pins that are power/ground
            needSpacerAtWest = True if main.west.length > 0 else False
            needSpacerAtEast = True if main.east.length > 0 else False
            for pin in slots["others"]:
                if pin.type == TypeOfPin.POWER:
                    if needSpacerAtWest:
                        main.west.push([None, pin])
                        needSpacerAtWest = False
                    else:
                        main.west.pushSinglePin(pin)
                elif pin.type == TypeOfPin.GROUND:
                    main.south.pushSinglePin(pin)
                elif pin.type == TypeOfPin.OUTPUT_POWER:
                    if needSpacerAtEast:
                        main.east.push([None, pin])
                        needSpacerAtEast = False
                    else:
                        main.east.pushSinglePin(pin)
        # -- Begin surface
        return main


class LayoutManagerForPhysicalSingleUnit(LayoutManager):
    def __init__(self, p: PackageDescription):
        self.p = p

    @property
    def pins(self) -> List[PinDescription]:
        """Gathers all the pins from the package into a list"""
        allThePins = []
        allThePins += self.p.ungroupedPins
        for g in self.p.groupedPins:
            allThePins += g.pins
        return sorted(allThePins, key=lambda p: p.designator.rank)

    def apply(self) -> RectangularHolderOfRailsOfPins:
        layout = self.p.layoutOfPins.value
        return getattr(self, f"apply_{layout}")()

    def apply_BRD(self):
        sortedPins = self.pins
        halfLength = int(len(sortedPins) / 2)

        result = RectangularHolderOfRailsOfPins()
        result.west.push(sortedPins[:halfLength])
        result.east.push(sortedPins[halfLength:])

        return result

    def apply_DIM(self):
        sortedPins = self.pins

        result = RectangularHolderOfRailsOfPins()
        result.west.push(sortedPins[0::2])
        result.east.push(sortedPins[1::2])

        return result

    def apply_DIP(self):
        sortedPins = self.pins
        halfLength = int(len(sortedPins) / 2)

        result = RectangularHolderOfRailsOfPins()
        result.west.push(sortedPins[:halfLength])
        result.east.push(list(reversed(sortedPins[halfLength:])))

        return result

    def apply_LCC(self):
        sortedPins = self.pins
        sideLength = int(len(sortedPins) / 4)
        deltaLeft = int(sideLength / 2) + 1

        result = RectangularHolderOfRailsOfPins()
        result.west.push(sortedPins[deltaLeft : deltaLeft + sideLength])
        result.south.push(
            sortedPins[deltaLeft + sideLength : deltaLeft + 2 * sideLength]
        )
        result.east.push(
            list(
                reversed(
                    sortedPins[deltaLeft + 2 * sideLength : deltaLeft + 3 * sideLength]
                )
            )
        )
        result.north.push(
            list(
                reversed(
                    sortedPins[deltaLeft + 3 * sideLength : len(sortedPins)]
                    + sortedPins[0:deltaLeft]
                )
            )
        )

        return result

    def apply_QFP(self):
        sortedPins = self.pins
        sideLength = int(len(sortedPins) / 4)

        result = RectangularHolderOfRailsOfPins()
        result.west.push(sortedPins[0:sideLength])
        result.south.push(sortedPins[sideLength : 2 * sideLength])
        result.east.push(list(reversed(sortedPins[2 * sideLength : 3 * sideLength])))
        result.north.push(list(reversed(sortedPins[3 * sideLength : len(sortedPins)])))

        return result

    def apply_SIM(self):
        sortedPins = self.pins

        result = RectangularHolderOfRailsOfPins()
        result.west.push(sortedPins)

        return result
