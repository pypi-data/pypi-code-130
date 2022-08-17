"""
Command line tool for generating a directory tree description
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Union

import click
import yaml
from rich import print  # pylint: disable=redefined-builtin
from rich.tree import Tree

from .__version__ import VERSION

DIRDESC_FILE_NAME = ".dirdesc.yaml"


@dataclass
class DirLevel:
    """
    Simple representation of a directory level in the directory tree.
    """

    path: Path
    children: Optional[tuple[DirLevel, ...]] = None
    descdata: Optional[Union[str, tuple[str, Dict]]] = None

    # these are set automatically
    description: Optional[Dict] = None
    basename: str = ""
    isdir: Optional[bool] = None

    def __apply_desc__(self):
        """
        Update self's description and children from the raw descdata, as
        applicable
        """
        if self.descdata is None:
            return

        if isinstance(self.descdata, str):
            self.description = self.descdata
        else:
            self.description, child_descriptions = self.descdata

            for child in self.children:
                if child.description is None:
                    child.description = child_descriptions.get(child.basename)

    def __post_init__(self):
        """
        After initial field setup, auto load some other fields based on those
        values.
        """
        self.basename = self.path.name
        self.isdir = self.path.is_dir()

        self.__apply_desc__()


def sort_children(
    children: list[DirLevel],
    dirsfirst: bool = False,
    filesfirst: bool = False,
) -> list[DirLevel]:
    """sort children lexically depending on settings"""

    def basename_sorter(child: DirLevel) -> str:
        return child.basename

    dirchildren = sorted(
        [child for child in children if child.isdir],
        key=basename_sorter,
    )
    filechildren = sorted(
        [child for child in children if not child.isdir],
        key=basename_sorter,
    )

    if dirsfirst:
        return dirchildren + filechildren
    if filesfirst:
        return filechildren + dirchildren
    return sorted(children, key=basename_sorter)


def load_dirdesc_yaml(path):
    """

    4 different formats supported:

    1. empty file
    2. single document, only string, no keys:

       ```yaml
       hello single string
       ```

    3. two documents, first is empy, second is mapping

       ```yaml
       ---
       somefile: somefile description
       ```

    4. two documents, first is only string, second is mapping

       ```yaml
       hello single string
       ---
       somefile: somefile description
       ```

    """
    with open(path, "r", encoding="utf-8") as yamlfile:
        descdata = tuple(yaml.load_all(yamlfile, Loader=yaml.Loader))

        if not descdata:
            return None

        if (len(descdata) == 1) and isinstance(descdata[0], str):
            return descdata[0]

        if (len(descdata) == 1) and isinstance(descdata[0], dict):
            return None, descdata[0]

        assert len(descdata) == 2, f"Error, {yamlfile.name} malformed"

        assert isinstance(descdata[0], str)
        assert isinstance(descdata[1], dict)

        return descdata


def walk(
    top,
    maxdepth,
    dirsfirst: bool,
    filesfirst: bool,
    hidden: bool,
):
    """walk the directory tree and add every matching directory"""
    dirs: list[str] = []
    nondirs: list[str] = []
    for entry in os.scandir(top):
        (dirs if entry.is_dir() else nondirs).append(entry.path)

    nondirs = [os.path.relpath(d, top) for d in nondirs]

    if DIRDESC_FILE_NAME not in nondirs:
        return None
    descdata = load_dirdesc_yaml(os.path.join(top, DIRDESC_FILE_NAME))
    nondirs.remove(DIRDESC_FILE_NAME)

    if not hidden:
        nondirs = [d for d in nondirs if not d.startswith(".")]

    children = []
    if maxdepth > 1:
        children = [
            walk(path, maxdepth - 1, dirsfirst, filesfirst, hidden) for path in dirs
        ]
    children += [DirLevel(Path(path)) for path in nondirs]
    children = list(filter(None, children))
    return DirLevel(
        Path(top),
        tuple(sort_children(children, dirsfirst, filesfirst)),
        descdata,
    )


def get_desc(dirtree):
    """generate the annotation for a dirtree entry, if available"""
    return f"  [green]# {dirtree.description}[/green]" if dirtree.description else ""


def build_tree(dirtree, tree):
    """construct the Rich tree from the dirtree"""
    for child in dirtree.children:
        desc = get_desc(child)
        if child.isdir:
            branch = tree.add("📂 " + child.basename + desc)
            build_tree(child, branch)
        else:
            tree.add("📄 " + child.basename + desc)


@click.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--depth", default=1, help="Depth of listing")
@click.option("--dirsfirst", is_flag=True, help="List directories first")
@click.option("--filesfirst", is_flag=True, help="List files first")
@click.option("--hidden", is_flag=True, help="Show hidden files too")
@click.version_option(version=VERSION)
def dirdesc(directory, depth, dirsfirst, filesfirst, hidden):
    """
    List directory contents in a tree format.
    """

    dirtree = walk(directory, depth, dirsfirst, filesfirst, hidden)
    tree = Tree(directory + get_desc(dirtree))
    build_tree(dirtree, tree)

    print(tree)
