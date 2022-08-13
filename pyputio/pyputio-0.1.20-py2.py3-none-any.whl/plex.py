from plexapi.myplex import MyPlexAccount
import os
import requests

def plexAuth():
    plex_auth_info = {
        "username": os.environ['PLEX_USERNAME'],
        "password": os.environ['PLEX_PASSWORD'],
        "server": os.environ['PLEX_SERVER_NAME']
    }

    account = MyPlexAccount(plex_auth_info['username'], plex_auth_info['password'])
    plex = account.resource(plex_auth_info['server']).connect()
    return plex

