from enum import Enum


class SearchMode(str, Enum):
    CONTAINS = "contains"
    EQUALS = "equals"
