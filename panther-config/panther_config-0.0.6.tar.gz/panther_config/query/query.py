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

"""
The query module provides classes representing Panther datalake queries
"""

from .. import _utilities

__all__ = ["CronSchedule", "IntervalSchedule", "Query"]


@dataclasses.dataclass(frozen=True)
class CronSchedule(_utilities.ConfigNode):
    """Cron expression based schedule definition for a query

    Attributes:
        - expression -- Defines how often queries using this schedule run (required)
        - timeout_minutes -- Defines the timeout applied to queries with this schedule (required)

    https://docs.panther.com/data-analytics/scheduled-queries
    """

    # required
    expression: str

    # required
    timeout_minutes: int

    # internal private methods
    def _typename(self) -> str:
        return "CronSchedule"

    def _output_key(self) -> str:
        return ""

    def _fields(self) -> typing.List[str]:
        return ["expression", "timeout_minutes"]


@dataclasses.dataclass(frozen=True)
class IntervalSchedule(_utilities.ConfigNode):
    """Interval based schedule definition for a query

    Attributes:
        - rate_minutes -- Defines how often queries using this schedule run (required)
        - timeout_minutes -- Defines the timeout applied to queries with this schedule (required)

    https://docs.panther.com/data-analytics/scheduled-queries
    """

    # required
    rate_minutes: int

    # required
    timeout_minutes: int

    # internal private methods
    def _typename(self) -> str:
        return "IntervalSchedule"

    def _output_key(self) -> str:
        return ""

    def _fields(self) -> typing.List[str]:
        return ["rate_minutes", "timeout_minutes"]


@dataclasses.dataclass(frozen=True)
class Query(_utilities.ConfigNode):
    """A saved or scheduled query

    Attributes:
        - name -- Unique name for the query (required)
        - sql -- SQL statement (required)
        - default_database -- Default database for the query (optional, default: "")
        - description -- Short description for the query (optional, default: "")
        - enabled -- Short description for the query (optional, default: True)
        - schedule -- Schedule attached to the query (optional, default: None)
        - tags -- Tags for the query (optional, default: None)

    https://docs.panther.com/data-analytics/scheduled-queries
    """

    # required
    name: str

    # required
    sql: str

    # optional
    default_database: str = ""

    # optional
    description: str = ""

    # optional
    enabled: bool = True

    # optional
    schedule: typing.Optional[
        typing.Optional[typing.Union[IntervalSchedule, CronSchedule]]
    ] = None

    # optional
    tags: typing.Optional[typing.Union[str, typing.List[str]]] = None

    # internal private methods
    def _typename(self) -> str:
        return "Query"

    def _output_key(self) -> str:
        return "config-node:query"

    def _fields(self) -> typing.List[str]:
        return [
            "name",
            "sql",
            "default_database",
            "description",
            "enabled",
            "schedule",
            "tags",
        ]
