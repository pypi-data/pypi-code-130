import asyncio
import logging
import jwt
from typing import Type

from .core import InvalidBotKeyException, URL_SIO, setup_logger
from .behaviour import Behaviour
from .gamemanager import GameManager
from .events import EventsHandler
from .sio import sio

setup_logger()

logger = logging.getLogger("ploupy")


class Bot:
    def __init__(self, bot_key: str, behaviour_class: Type[Behaviour]) -> None:
        self._bot_key = bot_key
        self._uid = self._extract_uid(bot_key)
        self._game_man = GameManager(self._uid, behaviour_class)
        self._events_handler = EventsHandler(self._game_man)

    def _extract_uid(self, bot_key: str) -> str:
        """
        Extract uid from bot_key.

        Note: do not verify token signature
        """
        headers = jwt.get_unverified_header(bot_key)

        uid = headers.get("uid")
        if uid is None:
            raise InvalidBotKeyException("Missing 'uid' header.")

        return uid

    async def _run(self):
        await sio.connect(URL_SIO, headers={"bot-jwt": self._bot_key})
        await sio.wait()

    async def _disconnect(self):
        await sio.disconnect()

    def run(self):
        """"""
        try:
            asyncio.get_event_loop().run_until_complete(self._run())
        except RuntimeError:  # ctr-C causes a RuntimeError
            pass
        asyncio.get_event_loop().run_until_complete(self._disconnect())
