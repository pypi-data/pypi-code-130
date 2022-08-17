from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from dhtc_server.models.Torrent import Torrent
from dhtc_server.routes.ui import make_response

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return make_response(request, {
        "info_hash_count": await Torrent.count()
    }, "dashboard.html")


@router.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse("/dashboard")
