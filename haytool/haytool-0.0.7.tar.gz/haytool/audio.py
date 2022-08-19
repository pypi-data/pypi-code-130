import wave
import io
import requests


def url_audio_length(url):
    """Get audio length in seconds from URL

    Args:
        url (str): Audio URL

    Returns:
        int: Audio length in seconds
    """
    r = requests.get(url)
    infofile = wave.open(io.BytesIO(r.content), 'r')
    frames = infofile.getnframes()
    rate = infofile.getframerate()
    duration = frames / float(rate)
    return duration
