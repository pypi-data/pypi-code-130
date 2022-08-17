# coding=utf-8
# *** WARNING: generated file
import typing
import dataclasses

from .. import _utilities

__all__ = [
    "_BaseFilter",
    "PythonFilter",
    "_BaseUnitTest",
    "JSONUnitTest",
    "DictUnitTest",
    "Rule",
    "SeverityLow",
    "SeverityInfo",
    "SeverityMedium",
    "SeverityHigh",
    "SeverityCritical",
]


SeverityLow = "LOW"
SeverityInfo = "INFO"
SeverityMedium = "MEDIUM"
SeverityHigh = "HIGH"
SeverityCritical = "CRITICAL"


@dataclasses.dataclass(frozen=True)
class _BaseFilter(_utilities.ConfigNode):
    """
    Base filter
    """

    # internal private methods
    def _typename(self) -> str:
        return "_BaseFilter"

    def _output_key(self) -> str:
        return ""

    def _fields(self) -> typing.List[str]:
        return []


@dataclasses.dataclass(frozen=True)
class PythonFilter(_BaseFilter):
    """
    Custom python filter

    Attributes:
    func -- Custom python filter
    """

    # required
    func: typing.Callable[[typing.Any], bool]

    # internal private methods
    def _typename(self) -> str:
        return "PythonFilter"

    def _output_key(self) -> str:
        return ""

    def _fields(self) -> typing.List[str]:
        return ["func"]


@dataclasses.dataclass(frozen=True)
class _BaseUnitTest(_utilities.ConfigNode):
    """
    Base unit test
    """

    # internal private methods
    def _typename(self) -> str:
        return "_BaseUnitTest"

    def _output_key(self) -> str:
        return ""

    def _fields(self) -> typing.List[str]:
        return []


@dataclasses.dataclass(frozen=True)
class JSONUnitTest(_BaseUnitTest):
    """
    Unit test with json content

    Attributes:
    data -- json data
    name -- name of the unit test
    """

    # required
    data: str

    # required
    name: str

    # internal private methods
    def _typename(self) -> str:
        return "JSONUnitTest"

    def _output_key(self) -> str:
        return ""

    def _fields(self) -> typing.List[str]:
        return ["data", "name"]


@dataclasses.dataclass(frozen=True)
class DictUnitTest(_BaseUnitTest):
    """
    Unit test with python dict content

    Attributes:
    data -- json data
    """

    # required
    data: typing.Dict[str, typing.Any]

    # internal private methods
    def _typename(self) -> str:
        return "DictUnitTest"

    def _output_key(self) -> str:
        return ""

    def _fields(self) -> typing.List[str]:
        return ["data"]


@dataclasses.dataclass(frozen=True)
class Rule(_utilities.ConfigNode):
    """
    Define a rule

    Attributes:
    filters -- Define event filters for the rule
    log_types -- Severity for the rule
    rule_id -- ID for the rule
    severity -- Severity for the rule
    title -- Severity for the rule
    unit_tests -- Define event filters for the rule
    """

    # required
    filters: typing.Union[_BaseFilter, typing.List[_BaseFilter]]

    # required
    log_types: typing.Union[str, typing.List[str]]

    # required
    rule_id: str

    # required
    severity: str

    # optional
    title: typing.Optional[str] = None

    # optional
    unit_tests: typing.Optional[
        typing.Union[_BaseFilter, typing.List[_BaseFilter]]
    ] = None

    # internal private methods
    def _typename(self) -> str:
        return "Rule"

    def _output_key(self) -> str:
        return "config-node:rule"

    def _fields(self) -> typing.List[str]:
        return ["filters", "log_types", "rule_id", "severity", "title", "unit_tests"]
