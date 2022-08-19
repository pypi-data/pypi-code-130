from __future__ import annotations

import fnmatch
import os
from typing import Any, Generator


def collect_files_in_module(filepath: str, ignore_folder: str) -> list[str]:
    """ """
    matches = []
    for root, dirs, filenames in os.walk(filepath):
        [
            dirs.remove(d)  # type: ignore
            for d in list(dirs)
            if ignore_folder and (d in ignore_folder)
        ]
        for filename in fnmatch.filter(filenames, "*.py"):
            matches.append(os.path.join(root, filename))

    return matches


def neighborhood(
    iterable: list[Any],
) -> Generator[Any, Any, Any]:
    """ """
    if not iterable:
        return iterable

    iterator = iter(iterable)
    prev_item = None
    current_item = next(iterator)  # throws StopIteration if empty.
    for next_item in iterator:
        yield (prev_item, current_item, next_item)
        prev_item = current_item
        current_item = next_item
    yield (prev_item, current_item, None)


def search_key_in_iterable(
    key: str,
    value: str,
    iterable: list[Any],
) -> tuple[Any, ...]:
    """ """
    return tuple(
        next(
            (
                (index, thing)
                for index, thing in enumerate(iterable)
                if thing[key] == value
            ),
            (None, None),
        ),
    )


def split_list_in_chunks(
    elements: list[Any],
    chunk_size: int,
) -> Generator[Any, Any, Any]:
    """Yield chunk_size number of striped chunks from elements."""
    for index in range(0, chunk_size):
        yield elements[index::chunk_size]
