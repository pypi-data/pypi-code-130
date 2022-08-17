from fastapi import APIRouter, Request
from dhtc_server.routes.ui import make_response

router = APIRouter()


@router.get("/telegram")
def clients(req: Request):
    return make_response(req, {}, "settings_telegram.html")


@router.post("/telegram")
def clients(req: Request):
    return make_response(req, {}, "settings_telegram.html")
