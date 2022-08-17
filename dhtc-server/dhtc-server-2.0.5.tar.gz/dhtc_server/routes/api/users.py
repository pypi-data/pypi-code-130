from fastapi import APIRouter, Body
from typing import List

from dhtc_server.models.User import User

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/")
async def all_users() -> List[User]:
    return await User.all().to_list()


@user_router.post("/")
async def add_user(user: User = Body(...)):
    return await user.create()
