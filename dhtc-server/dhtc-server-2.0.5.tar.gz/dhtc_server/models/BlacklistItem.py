from beanie import Document, Indexed
import pymongo

from dhtc_server.models.requests.SearchRequest import SearchRequest


class BlacklistItem(Document, SearchRequest):
    text = Indexed(str, pymongo.TEXT)
