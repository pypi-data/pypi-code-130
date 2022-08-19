__all__ = ['Path', 'StdIOE', 'StdOE']


import pathlib as p
import typing as t


Path = t.Union[str, p.Path]
StdIOE = t.Tuple[bytes, bytes, bytes]
StdOE = t.Tuple[bytes, bytes]
