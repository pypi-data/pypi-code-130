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

from electronic_package_descriptor import PackageDescription


def writeLinesWithSeparator(out, lines: List[str]):
    """
    This utilities wraps ``out.writelines(line + '\n' for line in lines)``.

    Python breaks my expectations regarding semantics of what is a line of text.

    As a Java developper, I expect line separator to be NOT part of a line (noise). Python expect line separator to be part of a line (signal).
    """
    out.writelines(line + "\n" for line in lines)


class SymbolGenerator:
    """
    The interface to implement by a specific output format
    """

    def __init__(self, p: PackageDescription):
        """
        A symbol generator works on a given package description.
        """
        pass

    @property
    def symbolSet(self) -> Dict[str, List[str]]:
        """
        A symbol generator create a set of symbol for a particular tool that uses a text file format to import them.

        The symbol generator thus create a list of text lines for each symbol of the set.
        """
        return {}

    def emitSymbolSet(self, out):
        """
        The generator will stream the set of symbols using ``out.write(...)``.
        """
        pass


class SingleSymbolGenerator:
    """
    A delegate that generate a single symbol.
    """

    def __init__(self, p: PackageDescription):
        pass

    @property
    def symbol(self) -> List[str]:
        """
        A single symbol is a set of lines of text describing the symbol using the syntax of the supported CAD software.
        """
        return []

    @property
    def suffix(self) -> str:
        return ""

    @property
    def title(self) -> str:
        return f"{self.p.name}"
