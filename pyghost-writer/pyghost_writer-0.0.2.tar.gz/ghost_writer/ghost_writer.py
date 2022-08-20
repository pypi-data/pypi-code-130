# -*- coding: utf-8 -*-

"""Main module."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ghost_writer.utils.logging import setup_logger


class ScriptGenerator(ABC):
    def __init__(self, file_name: str) -> None:

        self._file_name: str = file_name
        self._output: str = ""
        self._build_script()

    @abstractmethod
    def _build_script(self) -> None:
        pass

    def _add_line(self, line: str, indent_level: int = 0) -> None:

        for i in range(indent_level):

            self._output += " " * 4

        # add the line

        self._output += line

        # close the line
        self._end_line()

    @property
    def file_name(self) -> str:
        return self._file_name

    def _end_line(self):

        self._output += "\n"

    def write(self, directory: str = ".") -> None:

        out_file: Path = Path(directory) / self._file_name

        with out_file.open("w") as f:

            f.write(self._output)
