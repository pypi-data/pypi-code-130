from plexapi.myplex import MyPlexAccount
import os
from pyputio.plex import plexAuth

if os.environ.get('PLEX_PRUNE_EMPTY_COLLECTION') is None:
        LIBRARY="Movies"
else:
        LIBRARY=os.environ['PLEX_PRUNE_EMPTY_COLLECTION']

def pruneEmptyCollections(plex,collections):

        for idx, val in enumerate(collections):
                if plex.library.section(LIBRARY).collection(title=collections[idx].title).childCount != 0:
                        continue
                else:
                        plex.library.section(LIBRARY).collection(title=collections[idx].title).delete()
        return 0

def main():
    plex = plexAuth()
    collections = plex.library.section(LIBRARY).collections()
    try:
        prune = pruneEmptyCollections(plex, collections)
    except Exception as e:
        prune = e
    return prune