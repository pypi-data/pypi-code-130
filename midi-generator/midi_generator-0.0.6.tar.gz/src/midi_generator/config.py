from dataclasses import field
from midi_generator.note import *

LOOP_WAIT = 1.0 / 200  # 200 Hz
BEATS_PER_BAR = 4
MIDI_EVENT_NOTE_ON = 0x90


@dataclass
class Configuration:
    bars: int = 4
    density: float = 0.4
    rate: list[float] = field(default_factory=lambda: [1 / 4, 1 / 8])
    syncopation: float = 0.3
    scale: Scale = Scale(Key.C, Mode.MINOR)
    is_polyphonic: bool = False
