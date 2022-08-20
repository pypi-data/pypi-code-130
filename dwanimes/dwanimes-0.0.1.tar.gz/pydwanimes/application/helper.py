from ..domain.site import Site
from ..domain.player import Player

from importlib import import_module

SITES = {
    "animefenix": "Animefenix",
}

PLAYERS = {
    "fireload": "Fireload",
    "your_upload": "YourUpload",
}


def get_player_class(name:str)->Player:
    try:
        m = import_module(f"application.players.{name}")
    except ImportError as e:
        raise e
    return getattr(m,PLAYERS[name])

def get_site_class(name:str)->Site:
    try:
        m = import_module(f"application.sites.{name}")
    except ImportError as e:
        raise e
    return getattr(m,SITES[name])
