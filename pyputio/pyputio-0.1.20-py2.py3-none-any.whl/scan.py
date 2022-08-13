from plexapi.myplex import MyPlexAccount
import os
import requests
from pyputio.plex import plexAuth

def readPlexCollections():
    plex = plexAuth()
    collections = plex.library.sections()
    return collections

def plexUpdate():
	plex = plexAuth()
	update(plex)
	notify("Plex Update Requested.")	
	return 0

def update(plex):
    collections = plex.library.sections()
    task = plex.library.update()
    if os.environ.get('PUTIO_PLEX_METADATA_REFRESH_HARD') is not None:
        plex.library.refresh()
    return task

def notify(message):
	if os.environ.get('PUTIO_NOTIFY') is not None:
		if os.environ.get('PUSHOVER_USER') is None and os.environ.get('PUSHOVER_TOKEN') is None:
			print("[WARN] Ensure PUSHOVER_TOKEN and PUSHOVER_USER are set in environment.")
		else:
			notification_data = "token=%s&user=%s&device=putio-cli&message=%s" % (os.environ['PUSHOVER_TOKEN'], os.environ['PUSHOVER_USER'], message)
			headers = {"Content-type": "application/x-www-form-urlencoded"}
			notification = requests.post("https://api.pushover.net/1/messages.json", headers=headers, data=notification_data)
	return 0

def main():
    plex = plexAuth()
    try:
        scan = update(plex)
        notify("Plex Updated.")
    except Exception as e:
        scan = e
    return scan