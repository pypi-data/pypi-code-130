import sys
import pathlib
import xml.etree.ElementTree as ET


def get_wwise_datadir() -> pathlib.Path:

    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming/Audiokinetic/Wwise"
    elif sys.platform == "linux":
        return home / ".local/share/Audiokinetic/Wwise"
    elif sys.platform == "darwin":
        return home / "Library/Application Support/Audiokinetic/Wwise"
    else:
        return None

def get_wwise_usersetting(settingName = None):
    if not settingName:
        return None
    ww_datadir = get_wwise_datadir()
    if not ww_datadir or not ww_datadir.exists():
        return None
    settingsFile = ww_datadir / "Wwise.wsettings"
    if not settingsFile.exists():
        return None
    tree = ET.parse(settingsFile)
    root = tree.getroot()
    matches = root.findall(".//Property[@Name='{0}']".format(settingName))
    for match in matches:
        #print(match.attrib)
        return match.attrib
    else:
        return None

def get_wamp_port():
    attrib = get_wwise_usersetting("Waapi\WampPort")
    if not attrib:
        return None
    return attrib["Value"]


