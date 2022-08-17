from fastapi import APIRouter, Request
from dhtc_server.routes.ui import make_response

router = APIRouter()


@router.get("/database")
def clients(req: Request):
    return make_response(req, {}, "settings_database.html")


@router.post("/database")
def clients(req: Request):
    return make_response(req, {}, "settings_database.html")
