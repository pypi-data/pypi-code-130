import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests

from instagrapi.extractors import extract_track
from instagrapi.types import Track
from instagrapi.utils import json_value


class TrackMixin:

    def track_download_by_url(self, url: str, filename: str = "", folder: Path = "") -> Path:
        """
        Download track by URL

        Parameters
        ----------
        url: str
            URL for a track
        filename: str, optional
            Filename for the track
        folder: Path, optional
            Directory in which you want to download the track, default is "" and will download the files to working directory

        Returns
        -------
        Path
            Path for the file downloaded
        """
        fname = urlparse(url).path.rsplit("/", 1)[1].strip()
        assert fname, """The URL must contain the path to the file (m4a or mp3)."""
        filename = "%s.%s" % (filename, fname.rsplit(".", 1)[1]) if filename else fname
        path = Path(folder) / filename
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, "wb") as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        return path.resolve()

    def track_info_by_canonical_id(self, music_canonical_id: str) -> Track:
        """
        Get Track by music_canonical_id

        Parameters
        ----------
        music_canonical_id: str
            Unique identifier of the track

        Returns
        -------
        Track
            An object of Track type
        """
        data = {
            "tab_type": "clips",
            "referrer_media_id": "",
            "_uuid": self.uuid,
            "music_canonical_id": str(music_canonical_id),
        }
        result = self.private_request("clips/music/", data)
        track = json_value(result, "metadata", "music_info", "music_asset_info")
        return extract_track(track)
