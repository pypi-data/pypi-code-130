from collections import defaultdict
import io
from pathlib import Path
import re

from chchart_parser.chart_metadata import ChartMetadata
from chchart_parser.events import Event
from chchart_parser.sync import Sync
from chchart_parser.note_chart import NoteChartMap


section_re = re.compile(r'\[(?P<section>\w+)\]')


class Chart:
    def __init__(self, data: io.IOBase | Path | str):
        if isinstance(data, str):
            if data.endswith('.chart'):
                self.raw_data = Path(data).read_text()
            else:
                self.raw_data = data
        if isinstance(data, io.StringIO):
            self.raw_data = data.read()
        if isinstance(data, Path):
            self.raw_data = data.read_text()
        if isinstance(data, io.BytesIO):
            self.raw_data = data.read().decode('utf8')

        self.data = defaultdict(list)
        current_section_name = None
        for line in self.raw_data.splitlines():
            line = line.strip()
            if match := section_re.search(line):
                current_section_name = match.groupdict()['section']
                continue
            if line == '{' or line == '}':
                continue
            key, value = line.split('=', 1)
            self.data[current_section_name].append((key.strip(), value.strip()))

        self._metadata = None
        self._sync = None
        self._events = None
        self._charts = None

    @property
    def metadata(self) -> ChartMetadata:
        if self._metadata is not None:
            return self._metadata
        self._metadata = ChartMetadata.from_dict(self.data['Song'])
        return self._metadata

    @property
    def events(self) -> list[Event]:
        if self._events is not None:
            return self._events
        self._events = list(Event.from_dict(self.data['Events']))
        return self._events

    @property
    def sync(self) -> list[Sync]:
        if self._sync is not None:
            return self._sync
        self._sync = Sync.from_dict(self.data['SyncTrack'])
        return self._sync

    @property
    def charts(self) -> NoteChartMap:
        if self._charts is not None:
            return self._charts
        self._charts = NoteChartMap.from_dict(
            self.data, self.metadata.resolution
        )
        return self._charts
