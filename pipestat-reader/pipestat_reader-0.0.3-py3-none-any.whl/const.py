from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.sql.sqltypes import Boolean, Float, Integer, String

PACKAGE_NAME = "pipestat_reader"

FILTERS_BY_CLASS = {
    String().__class__.__name__: [
        "eq",
        "ne",
        "like",
        "ilike",
        "in",
        "not_in",
        "is_null",
    ],
    Float().__class__.__name__: [
        "lt",
        "lte",
        "gt",
        "gte",
        "range",
        "eq",
        "ne",
        "in",
        "not_in",
        "is_null",
    ],
    Integer().__class__.__name__: [
        "lt",
        "lte",
        "gt",
        "gte",
        "range",
        "eq",
        "ne",
        "in",
        "not_in",
        "is_null",
    ],
    Boolean().__class__.__name__: ["is_null", "in", "not_in"],
    JSONB().__class__.__name__: ["is_null", "contains"],
}
