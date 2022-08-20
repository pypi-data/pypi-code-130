from typing import Any
from typing import Type

from pydantic import Field

from oyabun.telegram.base import Request
from oyabun.telegram.entities import InlineKeyboardMarkup
from oyabun.telegram.entities import MessageEntity
from oyabun.telegram.entities import ReplyMarkupType


class AnswerCallbackQueryRequest(Request):
    cache_time: None | int = Field(None)
    callback_query_id: str = Field(...)
    show_alert: None | bool = Field(None)
    text: None | str = Field(None)
    url: None | str = Field(None)


class DeleteWebhookRequest(Request):
    drop_pending_updates: None | bool = Field(None)


class EditMessageCaptionRequest(Request):
    caption: None | str = Field(None)
    caption_entities: None | list[MessageEntity] = Field(None)
    chat_id: None | int | str = Field(None)
    inline_message_id: None | str = Field(None)
    message_id: None | int = Field(None)
    parse_mode: None | str = Field(None)
    reply_markup: None | InlineKeyboardMarkup = Field(None)


class EditMessageReplyMarkupRequest(Request):
    chat_id: None | int | str = Field(None)
    inline_message_id: None | str = Field(None)
    message_id: None | int = Field(None)
    reply_markup: None | InlineKeyboardMarkup = Field(None)


class EditMessageTextRequest(Request):
    chat_id: None | int | str = Field(None)
    disable_web_page_preview: None | bool = Field(None)
    entities: None | list[MessageEntity] = Field(None)
    inline_message_id: None | str = Field(None)
    message_id: None | int = Field(None)
    parse_mode: None | str = Field(None)
    reply_markup: None | InlineKeyboardMarkup = Field(None)
    text: str = Field(...)


class GetChatRequest(Request):
    chat_id: int | str = Field(...)


class GetFileRequest(Request):
    file_id: str = Field(...)


class GetMeRequest(Request):
    pass


class GetUpdatesRequest(Request):
    allowed_updates: None | list[str] = Field(None)
    limit: None | int = Field(None, le=100, ge=1)
    offset: None | int = Field(None)
    timeout: None | int = Field(None, ge=0)


class GetWebhookInfoRequest(Request):
    pass


class SendMessageRequest(Request):
    allow_sending_without_reply: None | bool = Field(None)
    chat_id: int | str = Field(...)
    disable_notification: None | bool = Field(None)
    disable_web_page_preview: None | bool = Field(None)
    entities: None | list[MessageEntity] = Field(None)
    parse_mode: None | str = Field(None)
    reply_markup: None | ReplyMarkupType = Field(None)
    reply_to_message_id: None | int = Field(None)
    text: str = Field(...)


class SendPhotoRequest(Request):
    allow_sending_without_reply: None | bool = Field(None)
    caption: None | str = Field(None)
    caption_entities: None | list[MessageEntity] = Field(None)
    chat_id: int | str = Field(...)
    disable_notification: None | bool = Field(None)
    parse_mode: None | str = Field(None)
    photo: Any = Field(...)
    reply_markup: None | ReplyMarkupType = Field(None)
    reply_to_message_id: None | int = Field(None)


class SetWebhookRequest(Request):
    allowed_updates: None | list[str] = Field(None)
    certificate: Any = Field(None)
    drop_pending_updates: None | bool = Field(None)
    ip_address: None | str = Field(None)
    max_connections: None | int = Field(None)
    url: str = Field(...)


__models__: set[Type[Request]] = {
    AnswerCallbackQueryRequest,
    DeleteWebhookRequest,
    EditMessageCaptionRequest,
    EditMessageReplyMarkupRequest,
    EditMessageTextRequest,
    GetChatRequest,
    GetFileRequest,
    GetMeRequest,
    GetUpdatesRequest,
    GetWebhookInfoRequest,
    SendMessageRequest,
    SendPhotoRequest,
    SetWebhookRequest,
}

__all__ = (
    "__models__",
    "AnswerCallbackQueryRequest",
    "DeleteWebhookRequest",
    "EditMessageCaptionRequest",
    "EditMessageReplyMarkupRequest",
    "EditMessageTextRequest",
    "GetChatRequest",
    "GetFileRequest",
    "GetMeRequest",
    "GetUpdatesRequest",
    "GetWebhookInfoRequest",
    "SendMessageRequest",
    "SendPhotoRequest",
    "SetWebhookRequest",
)
