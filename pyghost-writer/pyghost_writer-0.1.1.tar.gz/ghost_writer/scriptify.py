from pathlib import Path
from typing import List

from .ghost_writer import ScriptGenerator
from .utils.logging import setup_logger

log = setup_logger(__name__)


class PythonMetaGenerator(ScriptGenerator):
    def __init__(
        self, file_name: str, lines: List[str], indents: List[int]
    ) -> None:

        """

        This will generate a generator from an
        existing python script

        :param file_name:
        :type file_name: str
        :param lines:
        :type lines: List[str]
        :param indents:
        :type indents: List[int]
        :returns:

        """
        self._lines: List[str] = lines
        self._indents: List[int] = indents

        super().__init__(file_name)

    def _build_script(self) -> None:

        self._add_line("from ghost_writer import ScriptGenerator")
        self._end_line()
        self._end_line()

        self._add_line("class NewGenerator(ScriptGenerator):")
        self._add_line(
            "def __init__(self, file_name: str) -> None:", indent_level=1
        )
        self._add_line("super().__init__(file_name)", indent_level=2)
        self._end_line()

        self._add_line("def _build_script(self) -> None:", indent_level=1)

        for line, indent in zip(self._lines, self._indents):

            if line == "":

                self._add_line("self._end_line()", indent_level=2)

            else:

                if indent == 0:

                    arg = ""

                else:

                    arg = f", indent_level={indent}"

                self._add_line(
                    f"self._add_line('{line}'{arg})",
                    indent_level=2,
                )


def scriptify_python(file_name: str) -> None:

    """
    Convert a python script into a generator that
    can be used to parameterize the original script.

    A file will created named generated_<filename>.py

    :param file_name:
    :type file_name: str
    :returns:

    """
    gen_lines: List[str] = []
    indents: List[int] = []
    with Path(file_name).open("r") as f:

        script_lines: List[str] = f.readlines()

    for line in script_lines:

        tmp = []

        indent_factor = 1

        if line.startswith(" "):

            indent_factor = 4

            for char in line:

                if char == " ":

                    tmp.append(char)

                else:

                    break

        elif line.startswith("\t"):

            for char in line:

                if char == "\t":

                    tmp.append(char)

                else:

                    break

        num_indents = len(tmp) // indent_factor

        gen_lines.append(line[num_indents:].strip())

        indents.append(num_indents)

    # directory = Path(file_name).parent

    name = Path(file_name).name

    out_file = f"generated_{name}"

    script_gen = PythonMetaGenerator(out_file, gen_lines, indents)

    script_gen.write()

    log.info(f"{out_file}")
