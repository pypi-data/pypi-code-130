from dataclasses import dataclass
from typing import Generator

from chchart_parser.enums import EEventType


@dataclass
class Event:
    tick: int
    text: str
    type: EEventType

    @classmethod
    def from_dict(cls, data: list[tuple[str, str]]) -> Generator['Event', None, None]:
        for tick, evt in data:
            txt = evt.split(' ', 1).pop().strip('"')
            typ = EEventType.TEXT
            if txt.startswith('section'):
                typ = EEventType.SECTION
                txt = txt.split(' ', 1).pop()
            elif txt.startswith('lyric'):
                typ = EEventType.LYRIC
                txt = txt.split(' ', 1).pop()

            yield Event(int(tick), txt, typ)
