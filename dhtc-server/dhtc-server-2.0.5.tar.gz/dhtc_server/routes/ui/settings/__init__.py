from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from dhtc_server.models.Torrent import Torrent, TorrentFile
from dhtc_server.routes.ui import make_response

from dhtc_server.routes.ui.settings.users import router as UsersRouter
from dhtc_server.routes.ui.settings.clients import router as ClientsRouter
from dhtc_server.routes.ui.settings.database import router as DatabaseRouter
from dhtc_server.routes.ui.settings.indexing import router as IndexingRouter
from dhtc_server.routes.ui.settings.telegram import router as TelegramRouter

router = APIRouter()

router.include_router(UsersRouter, tags=["Settings", "Users"], prefix="/settings")
router.include_router(ClientsRouter, tags=["Settings", "Clients"], prefix="/settings")
router.include_router(DatabaseRouter, tags=["Settings", "Database"], prefix="/settings")
router.include_router(IndexingRouter, tags=["Settings", "Indexing"], prefix="/settings")
router.include_router(TelegramRouter, tags=["Settings", "Telegram"], prefix="/settings")


@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    return make_response(request, {}, "settings.html")


@router.post("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    await Torrent.delete_all()  # TODO
    await TorrentFile.delete_all()  # TODO
    return make_response(request, {}, "settings.html")
