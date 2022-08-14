import dataclasses
import re
from typing import List

REGEX_OPTIONAL_TYPE = re.compile(
    r"^typing\.Optional\[.+\]$|^typing\.Union\[.+, NoneType\]$"
)
REGEX_LIST_TYPE = re.compile(r"^typing\.List\[.+\]$")


def nonoptional_fields(klass: type) -> List[str]:
    # kludgy, yes
    return [
        f.name
        for f in dataclasses.fields(klass)
        if f.default == dataclasses.MISSING
        and REGEX_OPTIONAL_TYPE.match(str(f.type)) is None
    ]


def nonoptional_nonlist_fields(klass: type) -> List[str]:
    # kludgy, yes
    return [
        f.name
        for f in dataclasses.fields(klass)
        if (
            f.default == dataclasses.MISSING
            and REGEX_OPTIONAL_TYPE.match(str(f.type)) is None
            and REGEX_LIST_TYPE.match(str(f.type)) is None
        )
    ]
