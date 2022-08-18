from dataclasses import dataclass

from loguru import logger
from pymongo import GEOSPHERE, TEXT


@dataclass
class Index:
    fields: dict
    name: str = None
    comment: str = ""
    unique: bool = False
    sparse: bool = False
    partial: dict = None
    expire: int = None
    language_override: str = "language"
    text_index_version: int = 3
    weights: dict = None
    geosphere_index_version: int = 2

    def __post_init__(self):
        if not self.name:
            self.name = "_".join(f"{f}_{dire}" for f, dire in self.fields.items())

    @property
    def properties(self) -> str:
        vret = ""
        if self.unique:
            vret += "unique,"
        if self.sparse:
            vret += "sparse,"
        if self.partial:
            vret += f"partialFilterExpression={self.partial},"
        if self.expire:
            vret += f"expireAfterSeconds({self.expire}),"
        if self.weights:
            vret += f"weights({self.weights}),"
        return vret.rstrip(",")

    @property
    def creation_query(self):
        obj = {
            "comment": self.comment,
            "keys": self.fields.items(),
            "unique": self.unique,
            "sparse": self.sparse,
        }
        if self.partial:
            obj.update({"partialFilterExpression": self.partial})
        if self.expire is not None:
            obj.update({"expireAfterSeconds": self.expire})
        # If we have at least one of 2dsphere, then it's a geospatial index
        if GEOSPHERE in self.fields.values():
            obj.update({"2dsphereIndexVersion": self.geosphere_index_version})
        # If we have at least one field of type text, then it's a text index
        if TEXT in self.fields.values():
            obj.update(
                {
                    "language_override": self.language_override,
                    "textIndexVersion": self.text_index_version,
                    "weights": self.weights,
                }
            )
        return obj

    def __eq__(self, other):
        if isinstance(other, dict):
            # Convert to an Index instance first
            other = Index(
                fields=other["key"],
                name=other["name"],
                comment=other.get("comment", ""),
                unique=other.get("unique", False),
                sparse=other.get("sparse", False),
                partial=other.get("partialFilterExpression"),
                expire=other.get("expireAfterSeconds"),
                geosphere_index_version=other.get("2dsphereIndexVersion", 2),
                language_override=other.get("language_override", "language"),
                text_index_version=other.get("textIndexVersion", 3),
                weights=other.get("weights"),
            )
        # Comment is not considered, since pymongo doesn't support it yet
        conditionals = (
            "unique",
            "sparse",
            "partial",
            "expire",
            "language_override",
            "text_index_version",
            "weights",
            "geosphere_index_version",
        )
        for conditional in conditionals:
            if getattr(self, conditional) != getattr(other, conditional):
                logger.debug(f"{self.name} compare: {conditional} is different")
                return False
        my_fields = dict(self.fields)
        other_fields = dict(other.fields)
        # We need to compare keys, values and order (hence the lists)
        return my_fields == other_fields and list(my_fields) == list(other_fields)
