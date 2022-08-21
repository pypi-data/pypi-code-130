from enum import Enum


class EInstrument(str, Enum):
    lead = 'lead'
    bass = 'bass'
    rythm = 'rythm'
    drums = 'drums'
    keys = 'keys'


class EPlayer2(str, Enum):
    rhythm = 'rhythm'
    bass = 'bass'


class EEventType(int, Enum):
    TEXT = 0
    SECTION = 1
    LYRIC = 2


class EGuitarNote(int, Enum):
    GREEN = 0
    RED = 1
    YELLOW = 2
    BLUE = 3
    ORANGE = 4
    OPEN = 7


class EDrumNote(int, Enum):
    KICK = 0
    GREEN = 1
    RED = 2
    YELLOW = 3
    BLUE = 4
    ORANGE = 5
    DOUBLE_KICK = 32


class EGHLNote(int, Enum):
    W1 = 0
    W2 = 1
    W3 = 2
    B1 = 3
    B2 = 4
    OPEN = 7
    B3 = 8
