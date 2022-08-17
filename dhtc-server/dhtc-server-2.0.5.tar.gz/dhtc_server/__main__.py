from os.path import join, dirname
from argparse import ArgumentParser
from json import dump

import uvicorn
from starlette import status

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from loguru import logger as log

from dhtc_server.models.Torrent import Torrent, TorrentFile, TorrentTag
from dhtc_server.models.Watch import Watch
from dhtc_server.models.BlacklistItem import BlacklistItem

from dhtc_server.routes.api.torrents import router as TorrentsRouter
from dhtc_server.routes.api.watches import router as WatchesRouter
from dhtc_server.routes.api.blacklist import router as BlacklistRouter

from dhtc_server.routes.ui.dashboard import router as UIDashboardRouter
from dhtc_server.routes.ui.search import router as UISearchRouter
from dhtc_server.routes.ui.discover import router as UIDiscoverRouter
from dhtc_server.routes.ui.watches import router as UIWatchesRouter
from dhtc_server.routes.ui.blacklist import router as UIBlacklistRouter
from dhtc_server.routes.ui.settings import router as UISettingsRouter


def parse_args():
    ap = ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1", help="server address")
    ap.add_argument("--port", default=7331, help="server port")

    ap.add_argument("--generate-openapi", action="store_true", help="Generate OpenAPI specification")

    # ap.add_argument("--telegram-token", help="telegram token")

    # ap.add_argument("--disable-client-auth", action="store_true", default=False, help="Accept every client request")
    ap.add_argument("--add-client", type=str, help="Add new client which is authenticated by this token")

    return ap.parse_args()


def main():
    args = parse_args()
    app = FastAPI()

    @app.on_event("startup")
    async def start_database():
        client = AsyncIOMotorClient("mongodb://127.0.0.1:27017/dhtc")
        await init_beanie(
            client.get_default_database(),
            document_models=[
                Torrent, TorrentFile, TorrentTag,
                Watch,
                BlacklistItem
            ]
        )
        await TorrentTag.create_all()

    app.mount("/static", StaticFiles(directory=join(dirname(__file__), "static")), name="static")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        log.error("{} -> {}", request, exc)
        content = {'status_code': 10422, 'message': exc_str, 'data': None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    app.include_router(TorrentsRouter, tags=["Torrents"], prefix="/api/torrent")
    app.include_router(WatchesRouter, tags=["Watches"], prefix="/api/watches")
    app.include_router(BlacklistRouter, tags=["Blacklist"], prefix="/api/blacklist")

    app.include_router(UIDashboardRouter, tags=["Dashboard"])
    app.include_router(UISearchRouter, tags=["Search"])
    app.include_router(UIDiscoverRouter, tags=["Discover"])
    app.include_router(UIWatchesRouter, tags=["Watches"])
    app.include_router(UIBlacklistRouter, tags=["Blacklist"])
    app.include_router(UISettingsRouter, tags=["Settings"])

    if args.generate_openapi:
        with open("openapi.json", "w") as output:
            dump(get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes
            ), output)
        log.debug("Wrote OpenAPI specification to openapi.json")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == '__main__':
    main()
