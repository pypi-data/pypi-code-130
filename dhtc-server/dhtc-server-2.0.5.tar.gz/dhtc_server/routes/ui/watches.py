from enum import Enum

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

from dhtc_server.routes.ui import make_response

from dhtc_server.models.Watch import Watch

from dhtc_server.enums.SearchType import SearchType
from dhtc_server.enums.SearchMode import SearchMode

router = APIRouter()


class Operation(Enum):
    ADD = "add"
    DELETE = "delete"


@router.get("/watches", response_class=HTMLResponse)
async def watches(request: Request):
    return make_response(request, {
        "query": "",
        "results": await Watch.find_all().to_list()
    }, "watches.html")


@router.post("/watches", response_class=HTMLResponse)
async def watches(request: Request,
                  type: SearchType = Form(SearchType.TITLE),
                  mode: SearchMode = Form(SearchMode.CONTAINS),
                  text: str = Form(""),
                  op: Operation = Form(Operation.ADD),
                  id: str = Form("")):

    print(text, mode, type, op, id)

    result = False

    match op:
        case Operation.ADD:
            if text != "":
                await Watch(type=type, mode=mode, text=text).save()
                result = True
        case Operation.DELETE:
            if id != "":
                await Watch.delete(id=id)
                result = True

    return make_response(request, {
        "result": result,
        "results": await Watch.find_all().to_list()
    }, "watches.html")
