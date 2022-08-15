import json
import logging
from typing import Awaitable, Callable, Type
from functools import partial

from pydantic import BaseModel, ValidationError

from .models import core as _c, actions as _a, game as _g
from .core import InvalidServerDataFormatException
from .gamemanager import GameManager
from .sio import sio

logger = logging.getLogger("ploupy")


def _with_model(
    func: Callable[[BaseModel], Awaitable[str]], Model: Type[BaseModel]
) -> Callable[[dict], Awaitable[str]]:
    """Implementation of `with_model`"""

    async def event(data: dict) -> str:
        try:
            model = Model(**json.loads(data))
        except ValidationError as e:
            raise InvalidServerDataFormatException("Invalid server data")
        return await func(model)

    return event


def with_model(Model: Type[BaseModel]) -> Callable[[dict], Awaitable[str]]:
    """
    Event function decorator

    Build an instance of the `Model` class using
    the `data` argument of the raw event and pass it
    as `model` argument on the given function.`
    """
    return partial(_with_model, Model=Model)


class EventsHandler:
    def __init__(self, game_manager: GameManager) -> None:
        self._game_manager = game_manager
        _bind_events(self)


def _bind_events(handler: EventsHandler):
    """
    Bind events methods to sio instance
    """

    @sio.event
    async def connect():
        logger.info("Connected.")

    @sio.event
    async def connect_error(data):
        msg = data["message"]
        logger.error(f"Connection failed: {msg}")

    @sio.event
    async def disconnect():
        logger.info("Disconnected.")

    @sio.on("queue_invitation")
    @with_model(_c.QueueInvitation)
    async def queue_invitation(model: _c.QueueInvitation):
        await sio.emit("join_queue", _a.JoinQueue(qid=model.qid).dict())

    @sio.on("start_game")
    @with_model(_c.StartGame)
    async def start_game(data: _c.StartGame):
        await sio.emit("game_state", _a.GameState(gid=data.gid).dict())

    @sio.on("game_state")
    @with_model(_g.GameState)
    async def game_state(state: _g.GameState):

        game = handler._game_manager.get_game(state.gid)

        if game is None:
            logger.info(f"[gid: {state.gid[:4]}] New game")
            await handler._game_manager.create_game(state)
        else:
            await game._update_state(state)
