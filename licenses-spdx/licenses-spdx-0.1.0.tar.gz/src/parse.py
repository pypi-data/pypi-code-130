# parse "https://spdx.org/licenses/" and get the table with sortable class beautifulsoup4

from pathlib import Path
from enum import Enum
from typing import List, Union, IO
import json
import importlib.resources as pkg_resources

from .type import License, Licenses


def dump_licenses(
    licenses: List[License], filepath: Path = Path("./licenses.json"), join: bool = True
):  # join do nothing
    with open(str(filepath.resolve()), "w", encoding="utf-8") as f:
        licenses = [license.dict() for license in licenses]
        json.dump(licenses, f, ensure_ascii=False, indent=4)

def load_licenses(licenses:Union[str, Path, IO[str], IO[bytes]] = Path("./licenses.json")):
    if (licenses is str):
        pass
    if (licenses is Path):
        licenses = licenses.resolve().read_text()
    if (licenses is IO[str]):
        licenses = licenses.read() # test
    if (licenses is IO[bytes]):
        licenses = licenses.read().decode("utf-8")  # test
    licenses = json.loads(licenses) # convert to licenses data type and each one a license class
    return Licenses([License(**license) for license in licenses])

def load_builtin_licenses():
    from . import data
    licenses = pkg_resources.read_text(data, "licenses_nonobsolete_only.json")
    return load_licenses(licenses)