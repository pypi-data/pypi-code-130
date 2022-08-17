"""Utilities for bibliography."""

from typing import Optional, List
from dataclasses import dataclass
from mff_pytex.utils import File
from mff_pytex.packages import add_package, Package


@dataclass
class Bib:
    """Abstract class for bibliography.
    """
    name: str

    def __post_init__(self) -> None:
        add_package(Package('natbib'))

    def __str__(self) -> str:
        """Generate a record of given bibliography

        Returns:
            str: Bib record
        """
        text = '@' + self.__class__.__name__.lower() + '{'
        for field in self.__dataclass_fields__:
            if getattr(self, field) is not None:
                if field == 'name':
                    text += f"{getattr(self, field)},\n"
                elif field == 'typ':
                    text += f"  {field}e = \"{str(getattr(self, field))}\" ,\n"
                else:
                    text += f"  {field} = \"{str(getattr(self, field))}\" ,\n"
        return text + '}'


@dataclass
class Article(Bib):
    """An article from a magazine or a journal.
    """
    title: str
    year: int
    author: str
    journal: str
    month: Optional[str] = None
    note: Optional[str] = None
    number: Optional[int] = None
    pages: Optional[str] = None
    volume: Optional[str] = None


@dataclass
class Book(Bib):
    """A published book
    """
    title: str
    year: int
    author: str
    publisher: str
    address: Optional[str] = None
    edition: Optional[str] = None
    editor: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None
    number: Optional[int] = None
    series: Optional[str] = None
    volume: Optional[str] = None


@dataclass
class Booklet(Bib):
    """A bound work without a named publisher or sponsor.
    """
    title: str
    author: Optional[str] = None
    howpublished: Optional[str] = None
    year: Optional[int] = None
    month: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Conference(Bib):
    """Equal to inproceedings
    """
    author: str
    title: str
    booktitle: str
    year: int
    editor: Optional[str] = None
    number: Optional[int] = None
    volume: Optional[str] = None
    series: Optional[str] = None
    address: Optional[str] = None
    page: Optional[str] = None
    month: Optional[str] = None
    organization: Optional[str] = None
    publisher: Optional[str] = None
    note: Optional[str] = None


@dataclass
class InBook(Bib):
    """A section of a book without its own title.
    """
    title: str
    year: int
    author: str
    publisher: str
    pages: str
    chapter: Optional[str] = None
    address: Optional[str] = None
    edition: Optional[str] = None
    editor: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None
    number: Optional[int] = None
    series: Optional[str] = None
    volume: Optional[str] = None


@dataclass
class InCollection(Bib):
    """A section of a book having its own title.
    """
    author: str
    title: str
    booktitle: str
    year: int
    publisher: str
    editor: Optional[str] = None
    number: Optional[int] = None
    volume: Optional[str] = None
    series: Optional[str] = None
    typ: Optional[str] = None
    chapter: Optional[str] = None
    pages: Optional[str] = None
    address: Optional[str] = None
    edition: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None


class InProceedings(Conference):
    """An article in a conference proceedings.
    """
    pass


@dataclass
class Manual(Bib):
    """Technical manual.
    """
    title: str
    author: Optional[str] = None
    organization: Optional[str] = None
    address: Optional[str] = None
    edition: Optional[str] = None
    month: Optional[str] = None
    year: Optional[int] = None
    note: Optional[str] = None


@dataclass
class MasterThesis(Bib):
    """Master's thesis.
    """
    author: str
    title: str
    school: str
    year: int
    typ: Optional[str] = None
    address: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Misc(Bib):
    """Template useful for other kinds of publication.
    """
    author: Optional[str] = None
    title: Optional[str] = None
    howpublished: Optional[str] = None
    month: Optional[str] = None
    year: Optional[int] = None
    note: Optional[str] = None


class PhdThesis(MasterThesis):
    """Ph.D. thesis.
    """
    pass


@dataclass
class Proceedings(Bib):
    """The proceedings of a conference.
    """
    title: str
    year: int
    editor: Optional[str] = None
    number: Optional[int] = None
    volume: Optional[str] = None
    series: Optional[str] = None
    address: Optional[str] = None
    month: Optional[str] = None
    organization: Optional[str] = None
    publisher: Optional[str] = None
    note: Optional[str] = None


@dataclass
class TechReport(Bib):
    """Technical report from educational, commercial or standardization institution.
    """
    author: str
    title: str
    institution: str
    year: int
    typ: Optional[str] = None
    number: Optional[int] = None
    address: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Unpublished(Bib):
    """An unpublished article, book, thesis, etc.
    """
    author: str
    title: str
    note: str
    month: Optional[str] = None
    year: Optional[int] = None


class Bibliography(File):
    """Bib file

    Note:
        Requires natbib package to import, added with autopackage management.
    """
    file_type = 'bib'
    bib_list: List[Bib] = []

    def create(self, mode: str = 'w+') -> None:
        """Creates .bib file

        Args:
            mode (str, optional): Mode of given file. Same as open() function. Defaults to 'w+'
        """
        bib = open(self.file_path, mode)
        bib.write(*map(str, self.bib_list))
        bib.close()

    def add(self, *bibs: Bib) -> None:
        """Adds a book, etc. to the list of bibliohraphy.

        Args:
            *bibs (Bib): A Bib object
        """
        for bib in bibs:
            self.bib_list.append(bib)
