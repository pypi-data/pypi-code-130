from enum import Enum, IntEnum
from dataclasses import dataclass


class Key(IntEnum):
    C = 0
    D = 1
    E = 2
    F = 3
    G = 4
    A = 5
    B = 6


class Mode(Enum):
    MAJOR = 1
    MINOR = 2
    PHRYGIAN = 3
    DORIAN = 4
    LYDIAN = 5
    MIXOLYDIAN = 6
    LOCRIAN = 7


@dataclass(frozen=True)
class Note:
    pitch: int
    velocity: int
    start: float
    end: float


@dataclass(frozen=True)
class Scale:
    notes: list[int]

    def __init__(self, key: Key, mode: Mode):
        def generate_notes(scale):
            return sorted([x + y if x + y < 127 else 0 for x in scale for y in range(key, 127, 12)])

        match mode:
            case Mode.MAJOR:
                object.__setattr__(self, 'notes', generate_notes([0, 2, 4, 5, 7, 9, 11]))
            case Mode.MINOR:
                object.__setattr__(self, 'notes', generate_notes([0, 2, 3, 5, 7, 8, 10]))
            case Mode.PHRYGIAN:
                object.__setattr__(self, 'notes', generate_notes([0, 1, 3, 5, 7, 8, 10]))
            case Mode.DORIAN:
                object.__setattr__(self, 'notes', generate_notes([0, 2, 3, 5, 7, 9, 10]))
            case Mode.LYDIAN:
                object.__setattr__(self, 'notes', generate_notes([0, 2, 4, 6, 7, 9, 11]))
            case Mode.MIXOLYDIAN:
                object.__setattr__(self, 'notes', generate_notes([0, 2, 4, 5, 7, 9, 10]))
            case Mode.LOCRIAN:
                object.__setattr__(self, 'notes', generate_notes([0, 1, 3, 5, 6, 8, 10]))
