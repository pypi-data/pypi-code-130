from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from dhtc_server.routes.ui import make_response

from dhtc_server.enums.SearchType import SearchType
from dhtc_server.enums.SearchMode import SearchMode

from dhtc_server.models.BlacklistItem import BlacklistItem

router = APIRouter()


@router.get("/blacklist", response_class=HTMLResponse)
async def blacklist(request: Request):
    return make_response(request, {
        "query": "",
        "results": await BlacklistItem.find_all().to_list()
    }, "blacklist.html")


@router.post("/blacklist", response_class=HTMLResponse)
async def blacklist(request: Request,
                    type: SearchType,
                    mode: SearchMode,
                    text: str):
    item = BlacklistItem(
        type=type,
        mode=mode,
        text=text
    )

    await item.save()

    return make_response(request, {
        "query": text,
        "results": await BlacklistItem.find_all().to_list()
    }, "blacklist.html")
