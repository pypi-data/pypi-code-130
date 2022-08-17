from fastapi import APIRouter, Request
from dhtc_server.routes.ui import make_response

router = APIRouter()


@router.get("/indexing")
def clients(req: Request):
    return make_response(req, {}, "settings_indexing.html")


@router.post("/indexing")
def clients(req: Request):
    return make_response(req, {}, "settings_indexing.html")
