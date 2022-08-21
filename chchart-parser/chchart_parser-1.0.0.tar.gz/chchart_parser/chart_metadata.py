from dataclasses import dataclass

from chchart_parser.enums import EPlayer2


@dataclass
class ChartMetadata:
    name: str
    artist: str
    charter: str
    album: str
    year: int
    offset: int
    resolution: int
    player2: EPlayer2
    difficulty: int
    preview_start: int
    preview_end: int
    genre: str
    media_type: str
    music_stream: str | None = None
    guitar_stream: str | None = None
    rhythm_stream: str | None = None
    bass_stream: str | None = None
    drum_stream: str | None = None
    drum2_stream: str | None = None
    drum3_stream: str | None = None
    drum4_stream: str | None = None
    vocal_stream: str | None = None
    keys_stream: str | None = None
    crowd_stream: str | None = None

    @classmethod
    def from_dict(cls, data: list[tuple[str, str]]):
        data: dict[str, str] = {k: v for k, v in data}
        name = data['Name'].strip('"')
        artist = data['Artist'].strip('"')
        charter = data['Charter'].strip('"')
        album = data['Album'].strip('"')
        year = int(data['Year'].strip('"').split(' ').pop())
        offset = int(data['Offset'])
        resolution = int(data['Resolution'])
        player2 = EPlayer2[data['Player2']]
        difficulty = int(data['Difficulty'])
        preview_start = int(data['PreviewStart'])
        preview_end = int(data['PreviewEnd'])
        genre = data['Genre'].strip('"')
        media_type = data['MediaType'].strip('"')
        streams = {
            f'{instrument.lower()}_stream': data.get(f'{instrument.capitalize()}Stream', '').strip('"')
            if f'{instrument.capitalize()}Stream' in data else None
            for instrument in (
                'music', 'guitar', 'rhythm', 'bass', 'drum',
                'drum2', 'drum3', 'drum4', 'vocal', 'keys', 'crowd'
            )
        }
        return ChartMetadata(
            name, artist, charter, album, year,
            offset, resolution, player2, difficulty,
            preview_start, preview_end, genre,
            media_type, **streams,
        )