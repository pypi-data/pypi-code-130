from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Optional

from dhtc_server.models.Watch import Watch
from dhtc_server.models.requests.SearchRequest import SearchRequest

router = APIRouter()


class Response(BaseModel):
    error: bool
    text: str
    watch: Optional[Watch]


class SearchWatchResponse(BaseModel):
    Watches: List[Watch]


class DeleteRequest(BaseModel):
    Id: str


@router.post("/add", response_model=Response)
async def watches_add(watch: SearchRequest = Body(...)):
    if watch.text != "":
        w = await Watch.find({"text": watch.text, "mode": watch.mode, "type": watch.type}).to_list()
        if len(w) == 0:
            w = await Watch(text=watch.text, mode=watch.mode, type=watch.type).create()
            return {"error": False, "text": "Created watch {}".format(str(w.id)), "watch": w}
        else:
            return {"error": True, "text": "Watch with same parameters already exists"}
    return {"error": True, "text": "No regex specified"}


@router.get("/all", response_model=SearchWatchResponse)
async def watches_all():
    return {"Watches": (await Watch.all().to_list())}


@router.post("/delete", response_model=Response)
async def watches_delete(req: DeleteRequest = Body(...)):
    watch = Watch.find_one(_id=req.Id)
    if watch is not None:
        await watch.delete()
        return {"error": False, "text": "Successfully deleted item id {}".format(req.Id)}
    return {"error": True, "text": "Watch with id {} does not exist".format(req.Id)}
