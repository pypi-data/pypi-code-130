import random, string
from datetime import datetime


def get_id() -> str:
    """Returns a random alphanumeric id."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

def tstamp_to_american_datestr(tstamp: datetime) -> str:
    return tstamp.strftime('%m/%d/%y')

def tstamp_to_friendly_datestr(tstamp: datetime) -> str:
    return tstamp.strftime('%a %b %d')

def tstamp_to_datestr(tstamp: datetime) -> str:
    return tstamp.strftime('%Y-%m-%d')

def tstamp_to_timestr(tstamp: datetime) -> str:
    return tstamp.strftime('%H:%M:%S')

def tstamp_to_tstr(tstamp: datetime) -> str:
    if tstamp is not None:
        return f'{tstamp_to_datestr(tstamp)} {tstamp_to_timestr(tstamp)}'
    return None

def tstr_to_tstamp(tstr: str) -> datetime:
    if tstr is not None:
        return datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')
    return None
