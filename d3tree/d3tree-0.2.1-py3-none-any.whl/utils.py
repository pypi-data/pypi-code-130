import sys
from os import scandir
from typing import Generator, Iterator, Literal

from d3tree import node

AllowedTemplate = Literal["tree", "circles", "flame", "treemap"]


def read_from_stdin():
    line = sys.stdin.readline().strip()
    while line:
        yield line
        line = sys.stdin.readline()


def read_from_filepath(path: str, max_depth: int = 1, cur_depth: int = 1) -> Generator:
    """Retrieves files and directories from path recursively, up to max depth"""
    for entry in scandir(path):
        if entry.is_dir() and cur_depth < max_depth:
            yield from read_from_filepath(entry.path, max_depth=max_depth, cur_depth=cur_depth + 1)
        elif entry.is_file():
            yield entry


def create_node(iter_: Iterator) -> node.Node:
    """Prints the elements of the provided iterator"""
    root = node.Node(name="/")
    try:
        while True:
            filepath = next(iter_)
            try:
                filepath = "".join(filter(None, filepath.name.strip()))
            except AttributeError:
                filepath = "".join(filter(None, filepath.strip()))
            root.insert_node(path=filepath.split("/"))
    except StopIteration:
        pass

    return root
