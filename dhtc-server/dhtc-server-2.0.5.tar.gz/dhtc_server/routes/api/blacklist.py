from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List

from dhtc_server.models.BlacklistItem import BlacklistItem

router = APIRouter()


class AddBlacklistItemResponse(BaseModel):
    Id: str


class SearchBlacklistResponse(BaseModel):
    items: List[BlacklistItem]


@router.post("/add", response_model=AddBlacklistItemResponse)
async def blacklist_add(item: BlacklistItem = Body(...)):
    return {"Id": (await item.create()).id}


@router.get("/all", response_model=SearchBlacklistResponse)
async def blacklist_all():
    return {"items": await BlacklistItem.all().to_list()}
