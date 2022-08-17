# Copyright (C) 2022 Panther Labs Inc
#
# Panther Enterprise is licensed under the terms of a commercial license available from
# Panther Labs Inc ("Panther Commercial License") by contacting contact@runpanther.com.
# All use, distribution, and/or modification of this software, whether commercial or non-commercial,
# falls under the Panther Commercial License to the extent it is permitted.

# coding=utf-8
# *** WARNING: generated file

import typing
import dataclasses

from .. import _utilities

__all__ = ["ScheduledQuery"]


@dataclasses.dataclass(frozen=True)
class ScheduledQuery(_utilities.ConfigNode):
    """
    A query, but scheduled. #data

    Attributes:
    name -- query name
    """

    # required
    name: str

    # internal private methods
    def _typename(self) -> str:
        return "ScheduledQuery"

    def _output_key(self) -> str:
        return "query"

    def _fields(self) -> typing.List[str]:
        return ["name"]
