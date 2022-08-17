from fastapi import APIRouter, Request
from dhtc_server.routes.ui import make_response

router = APIRouter()


@router.get("/clients")
def clients(req: Request):
    return make_response(req, {}, "settings_clients.html")


@router.post("/clients")
def clients(req: Request):
    return make_response(req, {}, "settings_clients.html")
