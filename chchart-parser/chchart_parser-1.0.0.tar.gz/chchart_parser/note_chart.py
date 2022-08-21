from dataclasses import dataclass

from chchart_parser.enums import (
    EGuitarNote, EDrumNote, EGHLNote
)
from chchart_parser.sync import Sync


@dataclass
class BaseNoteChart:
    tick: int
    sustains: list[int]
    # TODO: For face off, since it's not used much, no point in doing it now
    # is_player1: bool
    # is_player2: bool
    is_starpower: bool
    is_solo: bool

    @staticmethod
    def should_be_hopo(previous_note_tick: int, current_note_tick: int, resolution: int, forced: bool):
        threshold = int((65 / 192) * resolution)
        diff = current_note_tick - previous_note_tick
        if diff > threshold:
            # should be strummed
            # forced flag flips it around
            # Can be simplified to 'return forced' but this way is more easily understood
            if forced:
                return True
            return False
        # diff <= threshold, should be hopo
        if forced:
            return False
        return True

    @staticmethod
    def should_be_starpower(note_tick: int, starpower_start_tick: int, starpower_duration: int) -> bool:
        return (note_tick - starpower_start_tick) >= starpower_duration

    @classmethod
    def from_dict(cls, section: str, data: list[tuple[str, str]], resolution: int):
        if section.endswith('Drums'):
            return DrumNoteChart.from_dict(data, resolution)
        if section.endswith('GHLGuitar') or section.endswith('GHLBass'):
            return GHLNoteChart.from_dict(data, resolution)
        return GuitarNoteChart.from_dict(data, resolution)


@dataclass
class GuitarNoteChart(BaseNoteChart):
    notes: list[EGuitarNote]
    is_tap: bool = False
    is_hopo: bool = False

    def seconds_since_start(self, sync: list[Sync], resolution: int) -> float:
        sync = [s for s in sync if s.tick < self.tick]
        total = 0.0
        for i, s in enumerate(sync[1:], start=1):
            total += (s.tick - sync[i - 1].tick) / resolution * 60.0 / float(s.bpm)
        total += (self.tick - sync[-1].tick) / resolution * 60.0 / float(sync[-1].bpm)
        return total

    @classmethod
    def from_dict(cls, data: list[tuple[str, str]], resolution: int) -> list['GuitarNoteChart']:
        starpower_duration = starpower_start_tick = 0
        # initialize to a large neg number so that should_be_hopo
        # works correctly on the first note of a chart
        previous_tick: int = -9999
        is_forced = is_tap = is_solo = False
        notes = sustains = chart = []
        for tick, info in data:
            tick = int(tick)
            key, *args = info.split(' ')
            if tick > previous_tick:
                # Finished parsing a section we can add the GuitarNoteChart object to the list.
                chart.append(
                    GuitarNoteChart(
                        previous_tick, sustains,
                        BaseNoteChart.should_be_starpower(
                            previous_tick, starpower_start_tick, starpower_duration
                        ), is_solo, notes, is_tap,
                        BaseNoteChart.should_be_hopo(
                            previous_tick, tick, resolution, is_forced
                        )
                    )
                )
                # We can now reset the flags
                notes = sustains = []
                is_forced = is_tap = False
            if key == 'N':
                # This is a note
                note_type, sustain = map(int, args)
                if note_type in (0, 1, 2, 3, 4, 7):
                    notes.append(EGuitarNote(note_type))
                    sustains.append(sustain)
                elif note_type == 5:
                    # Forced note
                    is_forced = True
                elif note_type == 6:
                    # Tap note
                    is_tap = True
            if key == 'E':
                # In chart events
                evt = args[0]
                if evt == 'solo':
                    is_solo = True
                if evt == 'soloend':
                    is_solo = False
            if key == 'S':
                # Special phrases (starpower)
                phrase_type, sustain = map(int, args)
                if phrase_type == 2:
                    starpower_duration = sustain
                    starpower_start_tick = tick
            previous_tick = tick
        return chart


@dataclass
class GHLNoteChart(BaseNoteChart):
    notes: list[EGHLNote]
    is_tap: bool = False
    is_hopo: bool = False

    @classmethod
    def from_dict(cls, data: list[tuple[str, str]], resolution: int) -> list['GHLNoteChart']:
        ...


@dataclass
class DrumNoteChart(BaseNoteChart):
    notes: list[EDrumNote]
    is_cymbal: bool = False
    is_drum_fill: bool = False

    @classmethod
    def from_dict(cls, data: list[tuple[str, str]], resolution: int) -> list['DrumNoteChart']:
        ...


@dataclass
class NoteChartMap:
    ExpertSingle: list[GuitarNoteChart] | None = None
    ExpertDoubleGuitar: list[GuitarNoteChart] | None = None
    ExpertDoubleBass: list[GuitarNoteChart] | None = None
    ExpertDoubleRhythm: list[GuitarNoteChart] | None = None
    ExpertDrums: list[DrumNoteChart] | None = None
    ExpertKeyboard: list[GuitarNoteChart] | None = None
    ExpertGHLGuitar: list[GHLNoteChart] | None = None
    ExpertGHLBass: list[GHLNoteChart] | None = None
    HardSingle: list[GuitarNoteChart] | None = None
    HardDoubleGuitar: list[GuitarNoteChart] | None = None
    HardDoubleBass: list[GuitarNoteChart] | None = None
    HardDoubleRhythm: list[GuitarNoteChart] | None = None
    HardDrums: list[DrumNoteChart] | None = None
    HardKeyboard: list[GuitarNoteChart] | None = None
    HardGHLGuitar: list[GHLNoteChart] | None = None
    HardGHLBass: list[GHLNoteChart] | None = None
    MediumSingle: list[GuitarNoteChart] | None = None
    MediumDoubleGuitar: list[GuitarNoteChart] | None = None
    MediumDoubleBass: list[GuitarNoteChart] | None = None
    MediumDoubleRhythm: list[GuitarNoteChart] | None = None
    MediumDrums: list[DrumNoteChart] | None = None
    MediumKeyboard: list[GuitarNoteChart] | None = None
    MediumGHLGuitar: list[GHLNoteChart] | None = None
    MediumGHLBass: list[GHLNoteChart] | None = None
    EasySingle: list[GuitarNoteChart] | None = None
    EasyDoubleGuitar: list[GuitarNoteChart] | None = None
    EasyDoubleBass: list[GuitarNoteChart] | None = None
    EasyDoubleRhythm: list[GuitarNoteChart] | None = None
    EasyDrums: list[DrumNoteChart] | None = None
    EasyKeyboard: list[GuitarNoteChart] | None = None
    EasyGHLGuitar: list[GHLNoteChart] | None = None
    EasyGHLBass: list[GHLNoteChart] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, list[tuple[str, str]]], resolution: int) -> 'NoteChartMap':
        instruments = [
            'Single', 'DoubleGuitar', 'DoubleBass', 'DoubleRhythm',
            'Drums', 'Keyboard', 'GHLGuitar', 'GHLBass'
        ]
        difficulties = ['Expert', 'Hard', 'Medium', 'Easy']
        sections = [d + i for d in difficulties for i in instruments]
        mapped = {
            section: BaseNoteChart.from_dict(section, d, resolution)
            for section, d in data.items()
            if section in sections
        }
        return NoteChartMap(**mapped)
