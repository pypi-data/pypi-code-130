import asyncio
import logging
from typing import Optional

import aiohttp
from versions import Version, parse_version
from yarl import URL

from ._client_ws import ServerSocket
from ._logging import hlog, log
from ._messages import BaseMessagable, MessageListener
from ._typing import MessageListeners, Payload, UrlLike, VersionLike
from .exceptions import (
    AlreadyConnectedError, ConnectionFailedError, InvalidVersionError,
    NotConnectedError, ServerConnectError
)
from .message import Message

__all__ = ("Connection",)


class Connection(BaseMessagable, MessageListener):
    """Class handling a connection to a server."""

    def __init__(
        self,
        url: UrlLike,
        token: Optional[str] = None,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        session: Optional[aiohttp.ClientSession] = None,
        extra_listeners: Optional[MessageListeners] = None,
        minimum_version: Optional[VersionLike] = None,
    ) -> None:
        self._url = url
        self._token: Optional[str] = token
        self._connected: bool = False
        self._loop = loop or asyncio.get_event_loop()
        self._session = session or aiohttp.ClientSession(loop=self._loop)
        self._ws: Optional[ServerSocket] = None
        self._minimum_version = minimum_version
        self._closed: bool = False
        self._message_id: int = 0
        self._waiting_listeners: Optional[MessageListeners] = None
        super().__init__(extra_listeners)

    @property
    def closed(self) -> bool:
        """Whether the client is closed."""
        return self._closed

    @property
    def url(self) -> UrlLike:
        """URL of the server."""
        return self._url

    @property
    def token(self) -> Optional[str]:
        """Authentication token of the server."""
        return self._token

    @property
    def connected(self) -> bool:
        """Whether the server is currently connected."""
        return self._connected

    async def close(self) -> None:
        """Close the connection."""
        if self.closed:
            raise NotConnectedError(
                "connection is already closed (did you call close twice?)",
            )

        if self._ws:
            await self._ws.close()

        await self._session.close()
        self._closed = True

    async def _ack(self, url: URL) -> None:
        """Acknowledge that the server supports hoist."""
        async with self._session.get(url.with_path("/hoist/ack")) as response:
            try:
                json = await response.json()
            except aiohttp.ContentTypeError as e:
                raise ServerConnectError(
                    "failed to acknowledge the server (does it support hoist?)"
                ) from e

            hlog(
                "ack",
                json,
                level=logging.DEBUG,
            )

            version: str = json["version"]
            minver = self._minimum_version

            if minver:
                minver_actual = (
                    minver
                    if isinstance(minver, Version)
                    else parse_version(minver)  # fmt: off
                )

                if not (parse_version(version) >= minver_actual):
                    raise InvalidVersionError(
                        f"server has version {version}, but required is {minver_actual.to_string()}",  # noqa
                    )

    async def connect(self, token: Optional[str] = None) -> None:
        """Open the connection."""
        if self.connected:
            raise AlreadyConnectedError(
                "already connected to socket",
            )

        raw_url = self.url
        url_obj = raw_url if isinstance(raw_url, URL) else URL(raw_url)

        try:
            await self._ack(url_obj)
        except aiohttp.ClientConnectionError as e:
            raise ServerConnectError(
                f"could not connect to {url_obj} (is the server turned on?)"
            ) from e

        url = url_obj.with_scheme(
            "wss" if url_obj.scheme == "https" else "ws",
        ).with_path("/hoist")

        auth: Optional[str] = token or self.token

        if not auth:
            raise ValueError(
                "no authentication token (did you forget to pass it?)",
            )

        self._connected = True
        try:
            conn = await self._session.ws_connect(url)
        except aiohttp.WSServerHandshakeError as e:
            raise ConnectionFailedError(
                f"failed to connect to {url}, does it support hoist?"
            ) from e

        self._ws = ServerSocket(
            self,
            conn,
            auth,
        )
        hlog(
            "connect",
            f"connected to {url}",
            level=logging.DEBUG,
        )
        await self._ws.login(self._call_listeners)

    async def _execute_action(
        self,
        action: str,
        payload: Optional[Payload] = None,
        *,
        process_messages: bool = True,
    ):
        """Run an action."""
        if not self._ws:
            raise NotConnectedError(
                "not connected to websocket (did you forget to call connect?)"
            )

        self._message_id += 1

        res = await self._ws.send(
            {
                "action": action,
                "data": payload or {},
            },
            self._message_id,
            reply=True,
        )

        if process_messages:
            await self._ws.process_messages()

        return res

    async def message(
        self,
        msg: str,
        data: Optional[Payload] = None,
        replying: Optional[Message] = None,
        listeners: Optional[MessageListeners] = None,
    ) -> Message:
        """Send a message to the server."""
        if not self._ws:
            raise NotConnectedError(
                "not connected to websocket (did you forget to call connect?)"
            )

        d = data or {}

        self._waiting_listeners = listeners
        res = await self._execute_action(
            "message",
            {
                "message": msg,
                "data": d,
                "replying": replying.to_dict() if replying else None,
            },
            process_messages=False,
        )

        assert res.data

        obj = await self.new_message(
            self,
            msg,
            d,
            replying,
            listeners=listeners,
            id=res.data["id"],
        )

        await self._ws.process_messages()
        return obj

    def __del__(self) -> None:
        if not self.closed:
            log(
                "close",
                "connection was not closed",
                level=logging.DEBUG,
            )
