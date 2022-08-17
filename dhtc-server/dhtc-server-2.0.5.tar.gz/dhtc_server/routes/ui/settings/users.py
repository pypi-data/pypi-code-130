from fastapi import APIRouter, Request
from dhtc_server.routes.ui import make_response

router = APIRouter()


@router.get("/users")
def clients(req: Request):
    return make_response(req, {}, "settings_users.html")


@router.post("/users")
def clients(req: Request):
    return make_response(req, {}, "settings_users.html")
