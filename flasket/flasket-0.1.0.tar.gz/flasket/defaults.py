import os

from typing import Dict, List, Optional

from boltons.iterutils import unique_iter, flatten_iter
from xdg import XDG_CONFIG_DIRS

SERVER_CFGNAME: str = "flasket.yml"

SERVER_LISTEN: str = "localhost"
SERVER_PORT: int = 8080

# fmt: off
CFGFILE_SEARCH_PATHS: List[str] = list(unique_iter(flatten_iter(
[
    "./.{cfgname}",                # ./.flasket.yml
    "./{cfgname}",                 # ./flasket.yml
    "$XDG_CONFIG_HOME/{cfgname}",  # ~/.config/flasket.yml
    "~/.{cfgname}",                # ~/.flasket.yml
    [os.path.join(str(e), "{cfgname}") for e in XDG_CONFIG_DIRS],
    "/etc/{cfgname}",              # /etc/flasket.yml
])))
# fmt: on


def default_configuration(defaults: Optional[Dict] = None) -> Dict:
    """
    Convenience function that returns defaults for arguments,
    and for configuration file

    Parameters
    ----------
    defaults: dict
        a dictionnary containing default values.

    Returns
    -------
    dict:
        a dictionnary
    """
    if defaults is None:
        defaults = {}
    if "server" not in defaults:
        defaults["server"] = {}

    # cf. src/middleware/__init__.py
    return {
        "cfgname": defaults.get("cfgname", SERVER_CFGNAME),
        "cfgfile_search_paths": defaults.get("cfgfile_search_paths", CFGFILE_SEARCH_PATHS),
        "server": {
            "description": defaults.get("description", "Flasket server"),
            "debug": defaults["server"].get("debug", False),
            "listen": defaults["server"].get("listen", SERVER_LISTEN),
            "port": defaults["server"].get("port", SERVER_PORT),
            "ui": defaults["server"].get("ui", True),
            "workers": defaults["server"].get("workers", 0),
            "pidfile": defaults["server"].get("pidfile", None),
        },
    }
