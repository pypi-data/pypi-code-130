"""Module containing basic structure of file."""

from datetime import date as datum
from typing import Optional
from mff_pytex.utils import command, Writing, Environment, get_func_name, File
import os
from dataclasses import dataclass
from mff_pytex.packages import get_packages


# TODO document structuring


class DocumentClass:
    """Document class command.
    """
    def __init__(self, name: str, *params: str) -> None:
        """Initialize Docuemnt class.

        Args:
            name (str): name of docuemnt type
            *params (str): settings of document
        """
        self.name = name
        self.params = params

    def __str__(self) -> str:
        """Returns documentclass command.

        Returns:
            str: documentclass command
        """
        return command('documentclass', self.name, *self.params)


@dataclass
class Preamble(Writing):
    """Preamble contains basic info about author and document.
    """
    documentclass: DocumentClass = DocumentClass('article')
    author: Optional[str] = None
    title: Optional[str] = None
    date: Optional[datum] = None

    def __str__(self) -> str:
        """Returns Preamble as string in TeX form.

        Returns:
            str: Preamble in TeX form.
        """
        text = Writing()
        text.write(str(self.documentclass))
        text.write('')
        text.write(*map(str, get_packages()))
        text.write('')
        text.write(self._text)
        text.write('')
        text.write(command('title', self.title))
        text.write(command('author', self.author))
        text.write(command('date', str(self.date)))
        return str(text)


class Document(Environment):
    """Content of document."""

    def __init__(self) -> None:
        """Initialize document.
        """
        self._text = ""
        self.en_type = "document"
        self.write(command('begin', self.en_type))

    def tableofcontents(self) -> None:
        """Adds a tableofcontents command to the TeX file."""
        self.write(command(get_func_name()))

    def maketitle(self) -> None:
        """Adds a maketitle command to the TeX file."""
        self.write(command(get_func_name()))

    def newpage(self) -> None:
        """Adds a newpage command to the TeX file."""
        self.write(command(get_func_name()))

    def clearpage(self) -> None:
        """Adds a clearpage command to the TeX file."""
        self.write(command(get_func_name()))

    def bibliography(self, name: str) -> None:
        """Adds a bibliography command to the TeX file.

        Args:
            name (str): Name of a bib file
        """
        self.write(command(get_func_name(), name))

    def listoffigures(self) -> None:
        """Adds a listoffigures command to the TeX file."""
        self.write(command(get_func_name()))

    def listoftables(self) -> None:
        """Adds a listoftables command to the TeX file."""
        self.write(command(get_func_name()))


class TexFile(File):
    """TeX file.
    """
    file_type = 'tex'
    preamble: Preamble = Preamble()
    document: Document = Document()

    def create(self, mode: str = 'w+') -> None:
        """Creates file and writes its content.

        Args:
            mode (str, optional): Mode of given file. Same as open() function. Defaults to 'w+'
        """
        tex = open(self.file_path, mode)
        tex.write(str(self.preamble))
        tex.write(str(self.document))
        tex.close()

    def make_pdf(self, mode: str = 'r') -> None:
        """Creates pdf file, if neccessary writes its content and create pdf document.

        Args:
            mode (str, optional): mode of given file. Same as open() function. Defaults to 'r'.
        """
        if mode not in ['r']:
            self.create(mode)
        print('first')
        os.system(f"pdflatex {self.file_path}")
        print('bib')
        os.system(f"bibtex {self.file_name}")
        print('second')
        os.system(f"pdflatex {self.file_path}")
        print('third')
        os.system(f"pdflatex {self.file_path}")
