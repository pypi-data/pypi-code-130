from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
from typing import AsyncGenerator
from typing import IO
from typing import Type
from typing import TypeVar

import aiohttp
import orjson

from oyabun.telegram import AnswerCallbackQueryRequest
from oyabun.telegram import AnswerCallbackQueryResponse
from oyabun.telegram import Chat
from oyabun.telegram import DeleteWebhookResponse
from oyabun.telegram import EditMessageCaptionRequest
from oyabun.telegram import EditMessageCaptionResponse
from oyabun.telegram import EditMessageReplyMarkupRequest
from oyabun.telegram import EditMessageReplyMarkupResponse
from oyabun.telegram import EditMessageTextRequest
from oyabun.telegram import EditMessageTextResponse
from oyabun.telegram import File
from oyabun.telegram import GetChatRequest
from oyabun.telegram import GetChatResponse
from oyabun.telegram import GetFileRequest
from oyabun.telegram import GetFileResponse
from oyabun.telegram import GetMeResponse
from oyabun.telegram import GetUpdatesRequest
from oyabun.telegram import GetUpdatesResponse
from oyabun.telegram import GetWebhookInfoResponse
from oyabun.telegram import InlineKeyboardMarkup
from oyabun.telegram import Message
from oyabun.telegram import MessageEntity
from oyabun.telegram import SendMessageRequest
from oyabun.telegram import SendMessageResponse
from oyabun.telegram import SendPhotoRequest
from oyabun.telegram import SendPhotoResponse
from oyabun.telegram import SetWebhookRequest
from oyabun.telegram import SetWebhookResponse
from oyabun.telegram import Update
from oyabun.telegram import User
from oyabun.telegram import WebhookInfo
from oyabun.telegram.base import Request
from oyabun.telegram.base import Response
from oyabun.telegram.entities import ReplyMarkupType


class Bot:
    """
    The class represents an entrypoint to communicate with Telegram Bot API.

    The methods are synchronized with those from official API doc.

    Usage: instantiate using bot token and go.

    If something is wrong, you'll get the `Bot.RequestError` exception raised.
    """

    TELEGRAM_BOT_API_URL = "https://api.telegram.org"

    class RequestError(RuntimeError):
        """
        A base exception for any internal error, including those
        caused by malformed requests and invalid data.
        """

        pass

    def __init__(
        self,
        token: str,
        *,
        session: aiohttp.ClientSession | None = None,
    ):
        """
        Sets up the new Bot instance.

        :param token: a bot token which BotFather gives to you.
        :param session: existing ClientSession or None (bot will use its own)
        """

        self.__session = session
        self.__token = token

    @asynccontextmanager
    async def client_session(
        self,
    ) -> AsyncGenerator[aiohttp.ClientSession, None]:
        if self.__session:
            yield self.__session
            return

        async with aiohttp.ClientSession() as session:
            prev = self.__session
            try:
                self.__session = session
                yield self.__session
            finally:
                self.__session = prev

    @property
    def api_url(self) -> str:
        """
        An API URL to make requests to.

        :return: the completed API URL as a string
        """

        return f"{self.TELEGRAM_BOT_API_URL}/bot{self.__token}"

    @property
    def file_url(self) -> str:
        """
        A URL to download files from.

        :return: the completed URL as a string
        """

        return f"{self.TELEGRAM_BOT_API_URL}/file/bot{self.__token}"

    async def answerCallbackQuery(
        self,
        *,
        callback_query_id: str,
        text: None | str = None,
        show_alert: None | bool = None,
        url: None | str = None,
        cache_time: None | int = None,
    ) -> bool:
        request = AnswerCallbackQueryRequest(
            cache_time=cache_time,
            callback_query_id=callback_query_id,
            show_alert=show_alert,
            text=text,
            url=url,
        )

        return await self._call_api(
            "answerCallbackQuery",
            request,
            response_cls=AnswerCallbackQueryResponse,
        )

    async def deleteWebhook(self) -> bool:
        return await self._call_api(
            "deleteWebhook",
            response_cls=DeleteWebhookResponse,
        )

    async def downloadFile(self, *, file: File) -> BytesIO:
        """
        Downloads the file's content into the BytesIO object.

        https://core.telegram.org/bots/api#getfile
        https://core.telegram.org/bots/api#file

        :param file: a File object

        :return: a BytesIO object with content of the file
        """

        if not file.file_path:
            raise self.RequestError(f"file {file} has no file_path set")

        return await self._download_file(file.file_path)

    async def editMessageCaption(
        self,
        *,
        caption: None | str = None,
        caption_entities: None | list[MessageEntity] | None = None,
        chat_id: None | int | str | None = None,
        inline_message_id: None | str | None = None,
        message_id: None | int | None = None,
        parse_mode: None | str | None = None,
        reply_markup: None | InlineKeyboardMarkup | None = None,
    ) -> bool | Message:
        """
        Use this method to edit captions of messages.

        On success, if the edited message is not an inline message,
        the edited Message is returned, otherwise True is returned.

        https://core.telegram.org/bots/api#editmessagecaption
        """

        request = EditMessageCaptionRequest(
            caption=caption,
            caption_entities=caption_entities,
            chat_id=chat_id,
            inline_message_id=inline_message_id,
            message_id=message_id,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )

        return await self._call_api(
            "editMessageCaption",
            request,
            response_cls=EditMessageCaptionResponse,
        )

    async def editMessageReplyMarkup(
        self,
        *,
        chat_id: None | int | str | None = None,
        inline_message_id: None | str | None = None,
        message_id: None | int | None = None,
        reply_markup: None | InlineKeyboardMarkup | None = None,
    ) -> bool | Message:
        """
        Use this method to edit only the reply markup of messages.

        On success, if the edited message is not an inline message,
        the edited Message is returned, otherwise True is returned.

        https://core.telegram.org/bots/api#editmessagereplymarkup
        """

        request = EditMessageReplyMarkupRequest(
            chat_id=chat_id,
            inline_message_id=inline_message_id,
            message_id=message_id,
            reply_markup=reply_markup,
        )

        return await self._call_api(
            "editMessageReplyMarkup",
            request,
            response_cls=EditMessageReplyMarkupResponse,
        )

    async def editMessageText(
        self,
        *,
        chat_id: None | int | str | None = None,
        disable_web_page_preview: None | bool = None,
        entities: None | list[MessageEntity] = None,
        inline_message_id: None | str = None,
        message_id: None | int = None,
        parse_mode: None | str = None,
        reply_markup: None | InlineKeyboardMarkup = None,
        text: str,
    ) -> bool | Message:
        """
        Use this method to edit text and game messages.

        On success, if the edited message is not an inline message,
        the edited Message is returned, otherwise True is returned.

        https://core.telegram.org/bots/api#editmessagetext
        """

        request = EditMessageTextRequest(
            chat_id=chat_id,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
            inline_message_id=inline_message_id,
            message_id=message_id,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            text=text,
        )

        return await self._call_api(
            "editMessageText",
            request,
            response_cls=EditMessageTextResponse,
        )

    async def getChat(self, *, chat_id: int | str) -> Chat:
        """
        Use this method to get up-to-date information about the chat
        (current name of the user for one-on-one conversations,
        current username of a user, group or channel, etc.).

        Returns a Chat object on success.

        https://core.telegram.org/bots/api#getchat
        """

        request = GetChatRequest(
            chat_id=chat_id,
        )

        return await self._call_api(
            "getChat",
            request,
            response_cls=GetChatResponse,
        )

    async def getFile(self, *, file_id: str) -> File:
        """
        Use this method to get basic info about a file
        and prepare it for downloading.

        For the moment, bots can download files of up to 20MB in size.

        The file can then be downloaded
        via the link https://api.telegram.org/file/bot<token>/<file_path>,
        where <file_path> is taken from the response.

        It is guaranteed that the link will be valid for at least 1 hour.

        When the link expires,
        a new one can be requested by calling getFile again.

        https://core.telegram.org/bots/api#getfile

        :return: on success, a File object
        """

        request = GetFileRequest(file_id=file_id)

        return await self._call_api(
            "getFile",
            request,
            response_cls=GetFileResponse,
        )

    async def getMe(self) -> User:
        """
        A simple method for testing your bot auth token.

        https://core.telegram.org/bots/api#getme

        :return: basic information about the bot in form of a User object
        """

        return await self._call_api(
            "getMe",
            response_cls=GetMeResponse,
        )

    async def getUpdates(
        self,
        *,
        offset: None | int = None,
        limit: None | int = None,
        timeout: None | int = None,
        allowed_updates: None | list[str] = None,
    ) -> list[Update]:
        request = GetUpdatesRequest(
            allowed_updates=allowed_updates,
            limit=limit,
            offset=offset,
            timeout=timeout,
        )

        return await self._call_api(
            "getUpdates",
            request,
            response_cls=GetUpdatesResponse,
            timeout=timeout,
        )

    async def getWebhookInfo(self) -> WebhookInfo:
        return await self._call_api(
            "getWebhookInfo",
            response_cls=GetWebhookInfoResponse,
        )

    async def sendMessage(
        self,
        *,
        chat_id: int | str,
        text: str,
        parse_mode: None | str = None,
        entities: None | list[MessageEntity] = None,
        disable_web_page_preview: None | bool = None,
        disable_notification: None | bool = None,
        reply_to_message_id: None | int = None,
        allow_sending_without_reply: None | bool = None,
        reply_markup: None | ReplyMarkupType = None,
    ) -> Message:
        """
        Use this method to send text messages.

        https://core.telegram.org/bots/api#sendmessage

        :param chat_id: Unique identifier for the target chat
        or username of the target channel
        (in the format @channelusername).

        :param text: Text of the message to be sent,
        1-4096 characters after entities parsing.

        :param parse_mode: Mode for parsing entities in the message text.
        See formatting options for more details.

        :param entities: A JSON-serialized list of special entities
        that appear in message text,
        which can be specified instead of parse_mode.

        :param disable_web_page_preview: Disables link previews
        for links in this message.

        :param disable_notification: Sends the message silently.
        Users will receive a notification with no sound.

        :param reply_to_message_id: If the message is a reply,
        ID of the original message.

        :param allow_sending_without_reply: Pass True,
        if the message should be sent
        even if the specified replied-to message is not found.

        :param reply_markup: Additional interface options.
        A JSON-serialized object for an inline keyboard,
        custom reply keyboard,
        instructions to remove reply keyboard
        or to force a reply from the user.

        :return: on success, the Message sent.
        """

        request = SendMessageRequest(
            allow_sending_without_reply=allow_sending_without_reply,
            chat_id=chat_id,
            disable_notification=disable_notification,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            text=text,
        )

        return await self._call_api(
            "sendMessage",
            request,
            response_cls=SendMessageResponse,
        )

    async def sendPhoto(
        self,
        *,
        chat_id: int | str,
        photo: str | Path | IO,
        caption: None | str = None,  # 0-1024
        parse_mode: None | str = None,
        caption_entities: None | list[MessageEntity] = None,
        disable_notification: None | bool = None,
        reply_to_message_id: None | int = None,
        allow_sending_without_reply: None | bool = None,
        reply_markup: None | ReplyMarkupType = None,
    ) -> Message:
        """
        Use this method to send photos.

        https://core.telegram.org/bots/api#sendphoto

        :param chat_id: Unique identifier for the target chat
        or username of the target channel
        (in the format @channelusername).

        :param photo: Photo to send.
        Pass a file_id as String to send a photo
        that exists on the Telegram servers (recommended),
        pass an HTTP URL as a String for Telegram
        to get a photo from the Internet,
        or upload a new photo using multipart/form-data.

        The photo must be at most 10 MB in size.
        The photo's width and height must not exceed 10000 in total.
        Width and height ratio must be at most 20.

        :param caption: Photo caption
        (may also be used when resending photos by file_id),
        0-1024 characters after entities parsing.

        :param parse_mode: Mode for parsing entities in the message text.
        See formatting options for more details.

        :param caption_entities: A JSON-serialized list of special entities
        that appear in the caption,
        which can be specified instead of parse_mode.

        :param disable_notification: Sends the message silently.
        Users will receive a notification with no sound.

        :param reply_to_message_id: If the message is a reply,
        ID of the original message.

        :param allow_sending_without_reply: Pass True,
        if the message should be sent
        even if the specified replied-to message is not found.

        :param reply_markup: Additional interface options.
        A JSON-serialized object for an inline keyboard,
        custom reply keyboard,
        instructions to remove reply keyboard
        or to force a reply from the user.

        :return: on success, the Message sent.
        """

        request = SendPhotoRequest(
            allow_sending_without_reply=allow_sending_without_reply,
            caption=caption,
            caption_entities=caption_entities,
            chat_id=chat_id,
            disable_notification=disable_notification,
            parse_mode=parse_mode,
            photo=photo,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
        )

        return await self._call_api(
            "sendPhoto", request, response_cls=SendPhotoResponse
        )

    async def setWebhook(self, *, url: str) -> bool:
        request = SetWebhookRequest(
            url=url,
        )

        return await self._call_api(
            "setWebhook",
            request,
            response_cls=SetWebhookResponse,
        )

    _T = TypeVar(
        "_T"
    )  # don't worry about this: used as a generic type var in `_call_api`

    async def _call_api(
        self,
        method: str,
        request: None | Request = None,
        *,
        response_cls: Type[Response[_T]] = Response[_T],
        timeout: None | int = None,
    ) -> _T:
        """
        Performs the call to the Bot API returning a value of proper type.
        In case of error raises `Bot.RequestError`.

        https://core.telegram.org/bots/api#making-requests

        :param method: name of the supported Telegram Bot API method

        :param request: request object,
        composed of input params of public method

        :param response_cls: desired response class with actual result type

        :return: object of response class' result type
        """

        url = f"{self.api_url}/{method}"

        try:
            # for methods which do not need the request at all
            request = request or Request()

            async with self.client_session() as session:
                data: aiohttp.FormData | bytes

                with request.files() as files:
                    if files:
                        headers = {}
                        data = aiohttp.FormData(
                            {_f: str(_v) for _f, _v in request.dict().items()}
                        )
                        for field, stream in files.items():
                            data.add_field(field, stream, filename="InputFile")
                    else:
                        headers = {"Content-Type": "application/json"}
                        data = request.jsonb()

                    kw = {}
                    if timeout:
                        kw["timeout"] = timeout * 2

                    send_request = session.post(
                        url,
                        data=data,
                        headers=headers,
                        **kw,
                    )

                    async with send_request as http_response:
                        body = await http_response.read()

                        if http_response.status != 200:
                            raise self.RequestError(body.decode())

            payload = orjson.loads(body)
            if not payload:
                err = f"unexpected empty payload on /{method}"
                raise self.RequestError(err)

            # actual&valid Telegram response
            response = response_cls.parse_obj(payload)

            if not response.ok:
                raise self.RequestError(response.description)

            if response.result is None:
                err = f"unexpected null result on /{method} -> {response}"
                raise self.RequestError(err)

            return response.result

        except Exception as err:
            raise self.RequestError(err) from err

    async def _download_file(
        self,
        file_path: str,
    ) -> BytesIO:
        """
        Downloads a file using file path from API.

        https://core.telegram.org/bots/api#getfile
        https://core.telegram.org/bots/api#file

        :param file_path: File path.
        Use https://api.telegram.org/file/bot<token>/<file_path>
        to get the file.

        :return: a BytesIO object with file content.
        """

        try:
            url = f"{self.file_url}/{file_path}"

            async with self.client_session() as session:
                async with session.get(url) as http_response:
                    body = await http_response.read()
                    if http_response.status != 200:
                        raise self.RequestError(body.decode())

            buffer = BytesIO()
            buffer.write(body)
            buffer.seek(0)

            return buffer

        except Exception as err:
            raise self.RequestError(err) from err
