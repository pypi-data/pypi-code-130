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
import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter, FileType
from electronic_package_descriptor import *

from typing import List, Union, Optional
from enum import Enum

from .kicad5 import SymbolGeneratorForKicad5


class OutputFormat(Enum):
    """
    The list of supported output format.

    JSON is the serialization format, whereas the other value are for generation of symbols.
    """

    JSON = "json"
    KICAD5 = "kicad5"
    KICAD6 = "kicad6"


def relocateFileIfNeeded(path: str, into: str) -> str:
    return os.path.join(into, os.path.basename(path)) if into != None else path


def prepareWork(s, isJsonSource: bool, extension: str, into: str) -> dict:
    return {
        "targetName": relocateFileIfNeeded(
            f"{s.name[:-5] if isJsonSource else s.name[:-3]}.{extension}", into
        ),
        "package": DeserializerOfPackage().packageFromJsonString("".join(s.readlines()))
        if isJsonSource
        else ParserOfMarkdownDatasheet().parseLines(s.readlines()),
    }


class SymbolGeneratorCli:
    @staticmethod
    def createArgParser() -> ArgumentParser:
        parser = ArgumentParser(
            prog="python3 -m electronic_symbol_generator_for_cad",
            description="Generate symbol libraries from specially crafted source files.",
            epilog="""---
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
""",
            formatter_class=RawDescriptionHelpFormatter,
            allow_abbrev=False,
        )

        # Add the arguments
        parser.add_argument(
            "sources",
            metavar="source files",
            type=FileType("r"),
            nargs="+",
            help="a list of source files",
        )

        parser.add_argument(
            "-f",
            "--format",
            action="store",
            type=OutputFormat,
            required=True,
            help=f"format of the output file : {[f.value for f in OutputFormat]}",
        )
        parser.add_argument(
            "--into",
            action="store",
            type=str,
            required=False,
            help="directory where output files will be generated.",
        )
        return parser

    def __init__(self):
        pass

    def run(self) -> Optional[int]:
        args = SymbolGeneratorCli.createArgParser().parse_args()

        sources = args.sources

        for s in sources:
            # checks input format by extension
            isJsonSource = False
            if s.name.endswith(".json"):
                print(f"File '{s.name}' is deserializable.")
                isJsonSource = True
                if args.format == OutputFormat.JSON:
                    print(f"Skipping already serialized file {s.name}")
                    continue
            elif s.name.endswith(".md"):
                print(f"File '{s.name}' is processable.")
            else:
                print(f"File '{s.name}' is not processable, skip...")
                continue

            # do the processing
            into = None if args.into == None or len(args.into) == 0 else args.into
            if args.format == OutputFormat.JSON:
                if isJsonSource:
                    print(f"skip already serialized file '{s.name}'")
                    continue
                targetName = relocateFileIfNeeded(s.name[:-3] + ".json", into)
                print(f"load datasheet and serialize into {targetName}...")
                serialized = SerializerOfPackage().jsonFrom(
                    ParserOfMarkdownDatasheet().parseLines(s.readlines())
                )
                with open(targetName, "w") as outfile:
                    outfile.write(serialized)
            elif args.format == OutputFormat.KICAD5:
                print(f"load datasheet or deserialize json, generate '*.lib'...")
                work = prepareWork(s, isJsonSource, "lib", into)
                with (open(work["targetName"], "w")) as outfile:
                    SymbolGeneratorForKicad5(work["package"]).emitSymbolSet(outfile)
            else:  # args.format == OutputFormat.KICAD6:
                print(f"load datasheet or deserialize json, generate '*.kycad_sym'...")
                raise RuntimeError("Not implemented yet !")
                targetName = relocateFileIfNeeded(
                    f"{s.name[:-5] if isJsonSource else s.name[:-3]}.kycad_sym", into
                )
                p = (
                    DeserializerOfPackage.packageFromJsonString("".join(s.readlines()))
                    if isJsonSource
                    else ParserOfMarkdownDatasheet().parseLines(s.readlines())
                )

        print("Done")
