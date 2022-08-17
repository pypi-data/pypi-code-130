from beanie.operators import Text

from fastapi import APIRouter, Request, Body, Form
from fastapi.responses import HTMLResponse

from dhtc_server.models.Torrent import Torrent, TorrentFile
from dhtc_server.models.requests.SearchRequest import *
from dhtc_server.routes.ui import make_response

router = APIRouter()


async def search_by(generic, text: str, mode: SearchMode):
    match mode:
        case SearchMode.EQUALS:
            return await Torrent.find(generic == text).to_list()
        case SearchMode.CONTAINS:
            return await Torrent.find(Text(text)).to_list()


@router.get("/search", response_class=HTMLResponse)
async def search(request: Request):
    return make_response(request, {"query": ""}, "search.html")


@router.post("/search", response_class=HTMLResponse)
async def search(request: Request = Body(),
                 type: SearchType = Form(),
                 mode: SearchMode = Form(),
                 text: str = Form()):
    results = []
    match type:
        case SearchType.TITLE:
            results = await search_by(Torrent.Name, text, mode)
        case SearchType.FILENAME:
            results = await search_by(TorrentFile.path, text, mode)

    return make_response(request, {"query": text, "results": list(results)}, "search.html")
