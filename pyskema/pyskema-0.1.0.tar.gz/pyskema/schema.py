from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
from abc import abstractmethod


class Structure:
    """Abstract structure of a node"""

    @abstractmethod
    def accept(self, visitor, *args, **kwargs):
        pass

    @classmethod
    def structure_default(cls):
        raise ValueError(
            f"In {cls} it is an error to set the node optional without a default value."
        )


@dataclass
class Node:
    """Base class for a node of the schema"""

    structure: Structure
    description: Optional[str] = None
    optional: bool = False
    default: Any = None

    def __init__(
        self,
        structure: Structure,
        description: Optional[str] = None,
        optional: bool = False,
        default: Any = None,
    ):
        self.structure = structure
        self.description = description
        self.optional = optional
        self.default = default

        if self.optional and self.default is None:
            self.default = self.structure.structure_default()

    @classmethod
    def of_atom(cls, atom, options=None, **kwargs):
        return cls(Atom(atom, options=options), **kwargs)

    @classmethod
    def of_union(cls, options, **kwargs):
        return cls(Union(options), **kwargs)

    @classmethod
    def of_collection(cls, element, **kwargs):
        return cls(Collection(element), **kwargs)

    @classmethod
    def of_record(cls, fields, **kwargs):
        return cls(Record(fields), **kwargs)

    @classmethod
    def of_map(cls, element, **kwargs):
        return cls(Map(element), **kwargs)

    @classmethod
    def of_tuple(cls, elements, **kwargs):
        return cls(Tuple(elements), **kwargs)


class AtomType(Enum):
    INT = 0
    FLOAT = 1
    STR = 2
    BOOL = 3
    OPTION = 4

    def name(self, options=None):
        if self == self.INT:
            return "int"
        elif self == self.FLOAT:
            return "float"
        elif self == self.STR:
            return "bool"
        elif self == self.OPTION:
            return "option(" + ", ".join(repr(s) for s in options) + ")"


@dataclass
class Atom(Structure):
    """Structure of an atomic piece of data"""

    type_: AtomType
    options: Optional[List[str]] = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_atom(self, *args, **kwargs)


@dataclass
class Union(Structure):
    """Structure for the union of several nodes"""

    options: List[Node]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_union(self, *args, **kwargs)


@dataclass
class Collection(Structure):
    """An ordered collection of similar nodes"""

    element: Node

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_collection(self, *args, **kwargs)

    @classmethod
    def structure_default(cls):
        return []


@dataclass
class Record(Structure):
    """A key-value pair collection.

    Keys are from a defined set and values are defined per-key.
    Keys are supposed to be valid identifiers.
    """

    fields: Dict[str, Node]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_record(self, *args, **kwargs)

    @classmethod
    def structure_default(cls):
        return {}


@dataclass
class Map(Structure):
    """A key-value pair collection.

    Keys are not restricted and values are of a single type.
    """

    element: Node

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_map(self, *args, **kwargs)

    @classmethod
    def structure_default(cls):
        return {}


@dataclass
class Tuple(Structure):
    """A fixed set of ordered fields.

    Each field can have a different structure.
    """

    fields: List[Node]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visit_tuple(self, *args, **kwargs)

    @classmethod
    def structure_default(cls):
        return []
