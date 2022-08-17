from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from dhtc_server.models.Torrent import Torrent
from dhtc_server.routes.ui import make_response

router = APIRouter()


@router.get("/discover", response_class=HTMLResponse)
async def discover(request: Request):
    return make_response(request, {
        "results": await Torrent.aggregate([{"$sample": {"size": 50}}]).to_list()
    }, "discover.html")
