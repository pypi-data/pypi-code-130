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

from .symbols import *
from .symbolGenerator_fsu import SymbolGeneratorForKicad5_Functionnal
from .symbolGenerator_fmu import SymbolGeneratorForKicad5_Functionnal_MultiUnit
from .symbolGenerator_psu import (
    SymbolGeneratorForKicad5_Physical_SingleUnit,
    SymbolGeneratorForKicad5_Physical_SingleUnit_Socket,
)


class SymbolGeneratorForKicad5(SymbolGenerator):
    def __init__(self, p: PackageDescription):
        self.p = p
        self.generators = {
            "functionnal_single_unit": SymbolGeneratorForKicad5_Functionnal(p),
            "functionnal_multi_unit": SymbolGeneratorForKicad5_Functionnal_MultiUnit(p),
            "physical_single_unit": SymbolGeneratorForKicad5_Physical_SingleUnit(p),
            "physical_single_unit_socket": SymbolGeneratorForKicad5_Physical_SingleUnit_Socket(
                p
            ),
        }

    @property
    def symbolSet(self) -> Dict[str, List[str]]:
        return {key: self.generators[key].symbol for key in self.generators}

    def emitSymbolSet(self, out):
        # emit prolog
        writeLinesWithSeparator(out, toBeginSymbolSet(self.p.name))
        # body
        sset = self.symbolSet
        for k in sset:
            writeLinesWithSeparator(out, sset[k])
        # emit epilog
        writeLinesWithSeparator(out, toEndSymbolSet())
