__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

__all__ = ["path2workdir"]

from pathlib import Path
from bitia.common.checksumdir import dirhash
from bitia.common import hash256, bitia_workdir


def str2workdir(string: str) -> Path:
    return _hash2dir(hash256(string.encode()))


def path2workdir(path: Path) -> Path:
    """Given a path, return subdirectory for executing the pipeline. Read the
    content the of the directory and compute the hash. The hash is the name of
    the sub-directory.
    """
    return _hash2dir(_path2hash(path))


def get_workdir(user_input) -> Path:
    return (
        bitia_workdir() / path2workdir(user_input)
        if Path(user_input).exists()
        else bitia_workdir() / str2workdir(user_input)
    )


def _path2hash(path: Path) -> str:
    return str(dirhash(path.resolve(), "md5"))


def _hash2dir(hash: str) -> Path:
    return Path(hash[0:2]) / hash
