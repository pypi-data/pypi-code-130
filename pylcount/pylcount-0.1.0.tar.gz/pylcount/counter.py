import os
import pathlib

from typing import List, Tuple


def check_ignore(path: str, ignore_list: list) -> bool:
    for i in ignore_list:
        if path.startswith(i):
            return True

    return False


def count_directory(path: str, ignore: list = [], ext: list = []) -> List[Tuple[str]]:
    counted_files = []

    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)

            if not check_ignore(filepath, ignore):
                if ext:
                    file_ext = pathlib.Path(filepath).suffix
                    if file_ext not in ext:
                        continue

                result = count_file(filepath)
                counted_files.extend(result)

    return counted_files


def count_file(path: str) -> List[Tuple[str]]:
    try:
        with open(path, 'r') as reader:
            file_lines = len(reader.readlines())
    except UnicodeDecodeError:
        return []

    return [(path, str(file_lines))]
