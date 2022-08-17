from beanie import Document, Indexed
import pymongo

from dhtc_server.models.requests.SearchRequest import SearchRequest


class Watch(Document, SearchRequest):
    text = Indexed(str, pymongo.TEXT)


async def contains(text):
    """
    :param text:
    :return: if text exists as db entry
    """
    return (await Watch.find_one(text=text)) is not None


async def create(text, type, mode):
    """
    creates a watch if it does not exist yet
    :param text:
    :param type:
    :param mode:
    :return: stringified id of document
    """
    if not (await contains(text)):
        return (await Watch(text=text, type=type, mode=mode).create()).id.__str__()
    return None
