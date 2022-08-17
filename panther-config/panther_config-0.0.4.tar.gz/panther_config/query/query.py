# coding=utf-8
# *** WARNING: generated file
import typing
import dataclasses

from .. import _utilities

__all__ = ["Query"]


@dataclasses.dataclass(frozen=True)
class Query(_utilities.ConfigNode):
    """
    A saved or scheduled query

    Attributes:
    name -- Unique name for the query
    """

    # required
    name: str

    # internal private methods
    def _typename(self) -> str:
        return "Query"

    def _output_key(self) -> str:
        return "config-node:query"

    def _fields(self) -> typing.List[str]:
        return ["name"]
