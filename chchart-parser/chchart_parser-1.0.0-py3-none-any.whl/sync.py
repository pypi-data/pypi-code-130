from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256


@dataclass
class Sync:
    tick: int
    time_signature: Fraction
    bpm: Decimal

    def __hash__(self) -> int:
        return int(
            sha256(
                f'{self.tick}{self.time_signature}{self.bpm}'.encode('ascii')
            ).hexdigest(), base=16
        )

    @classmethod
    def from_dict(cls, data: list[tuple[str, str]]) -> list['Sync']:
        signatures: dict[int, Fraction] = {}
        bpms: dict[int, Decimal] = {}
        syncs: set['Sync'] = set()

        for tick, evt in data:
            evt_name, *evt_args = evt.split(' ')
            if evt_name == 'TS':
                if len(evt_args) == 1:
                    evt_args.append(4)
                signatures[int(tick)] = Fraction(
                    int(evt_args[0]), 2**int(evt_args[1])
                )
            if evt_name == 'B':
                bpms[int(tick)] = Decimal(int(evt_args[0])) / 1000

        for tick, signature in signatures.items():
            bpm = next(b for t, b in bpms.items() if t <= tick)
            syncs.add(Sync(tick, signature, bpm))

        for tick, bpm in bpms.items():
            ts = next(ts for t, ts in signatures.items() if t <= tick)
            syncs.add(Sync(tick, ts, bpm))

        return list(sorted(syncs, key=lambda s: s.tick))
