from enum import Enum


class Unit(str, Enum):
    """
    https://developers.google.com/docs/api/reference/rest/v1/documents#Unit
    """

    UNIT_UNSPECIFIED = "UNIT_UNSPECIFIED"
    PT = "PT"
