from datetime import datetime
from typing import Optional
from typing import Type

from pydantic import Field

from oyabun.telegram.base import TelegramBotApiType


class Audio(TelegramBotApiType):
    """
    This object represents an audio file
    to be treated as music by the Telegram clients.

    https://core.telegram.org/bots/api#audio
    """

    duration: int = Field(...)
    file_id: str = Field(...)
    file_name: None | str = Field(None)
    file_size: None | int = Field(None)
    file_unique_id: str = Field(...)
    mime_type: None | str = Field(None)
    performer: None | str = Field(None)
    thumb: Optional["PhotoSize"] = Field(None)
    title: None | str = Field(None)


class BotCommand(TelegramBotApiType):
    command: str = Field(..., min_length=1, max_length=32)
    description: str = Field(..., min_length=3, max_length=256)


class BotCommandScope(TelegramBotApiType):
    type: str = Field(...)  # noqa: A003,VNE003


class BotCommandScopeDefault(BotCommandScope):
    type: str = Field("default")  # noqa: A003,VNE003


class CallbackQuery(TelegramBotApiType):
    """
    This object represents an incoming callback query
    from a callback button in an inline keyboard.

    If the button that originated the query
    was attached to a message sent by the bot,
    the field message will be present.

    If the button was attached to a message
    sent via the bot (in inline mode),
    the field inline_message_id will be present.

    Exactly one of the fields data or game_short_name will be present.

    https://core.telegram.org/bots/api#callbackquery
    """

    chat_instance: str = Field(...)
    data: None | str = Field(None)
    from_: "User" = Field(..., alias="from")
    game_short_name: None | str = Field(None)
    id: str = Field(...)  # noqa: A003,VNE003
    inline_message_id: None | str = Field(None)
    message: Optional["Message"] = Field(None)

    class Config:
        fields = {
            "from_": "from",
        }


class Chat(TelegramBotApiType):
    """
    This object represents a chat.

    https://core.telegram.org/bots/api#chat
    """

    bio: None | str = Field(None)
    can_set_sticker_set: None | bool = Field(None)
    description: None | bool = Field(None)
    first_name: None | str = Field(None)
    has_private_forwards: None | bool = Field(None)
    has_protected_content: None | bool = Field(None)
    has_restricted_voice_and_video_messages: None | bool = Field(None)
    id: int = Field(...)  # noqa: A003, VNE003
    invite_link: None | bool = Field(None)
    join_by_request: None | bool = Field(None)
    join_to_send_messages: None | bool = Field(None)
    last_name: None | str = Field(None)
    linked_chat_id: None | int = Field(None)
    location: Optional["ChatLocation"] = Field(None)
    message_auto_delete_time: None | int = Field(None)
    permissions: Optional["ChatPermissions"] = Field(None)
    photo: Optional["ChatPhoto"] = Field(None)
    pinned_message: Optional["Message"] = Field(None)
    slow_mode_delay: None | int = Field(None)
    sticker_set_name: None | str = Field(None)
    title: None | str = Field(None)
    type: str = Field(...)  # noqa: A003, VNE003
    username: None | str = Field(None)


class ChatLocation(TelegramBotApiType):
    """
    Represents a location to which a chat is connected.

    https://core.telegram.org/bots/api#chatlocation
    """

    address: str = Field(...)
    location: "Location" = Field(...)


class ChatPermissions(TelegramBotApiType):
    """
    Describes actions that a non-administrator user is allowed to take in a chat.

    https://core.telegram.org/bots/api#chatpermissions
    """

    can_add_web_page_previews: None | bool = Field(None)
    can_change_info: None | bool = Field(None)
    can_invite_users: None | bool = Field(None)
    can_pin_messages: None | bool = Field(None)
    can_send_media_messages: None | bool = Field(None)
    can_send_messages: None | bool = Field(None)
    can_send_other_messages: None | bool = Field(None)
    can_send_polls: None | bool = Field(None)


class ChatPhoto(TelegramBotApiType):
    """
    This object represents a chat photo.

    https://core.telegram.org/bots/api#chatphoto
    """

    big_file_id: str = Field(...)
    big_file_unique_id: str = Field(...)
    small_file_id: str = Field(...)
    small_file_unique_id: str = Field(...)


class Dice(TelegramBotApiType):
    """
    This object represents an animated emoji that displays a random value.

    https://core.telegram.org/bots/api#dice
    """

    emoji: str = Field(...)
    value: int = Field(...)


class Document(TelegramBotApiType):
    """
    This object represents a general file
    (as opposed to photos, voice messages and audio files).

    https://core.telegram.org/bots/api#document
    """

    file_id: str = Field(...)
    file_name: None | str = Field(None)
    file_size: None | int = Field(None)
    file_unique_id: str = Field(...)
    mime_type: None | str = Field(None)
    thumb: Optional["PhotoSize"] = Field(None)


class File(TelegramBotApiType):
    file_id: str = Field(...)
    file_path: None | str = Field(None)
    file_size: None | int = Field(None)
    file_unique_id: str = Field(...)


class ForceReply(TelegramBotApiType):
    """
    Upon receiving a message with this object,
    Telegram clients will display a reply interface to the user
    (act as if the user has selected the bot's message and tapped 'Reply').

    This can be extremely useful
    if you want to create user-friendly step-by-step interfaces
    without having to sacrifice privacy mode.

    Example: A poll bot for groups runs in privacy mode
    (only receives commands, replies to its messages and mentions).

    There could be two ways to create a new poll:

    -   Explain the user how to send a command with parameters
        (e.g. /newpoll question answer1 answer2).

        May be appealing for hardcore users but lacks modern day polish.

    -   Guide the user through a step-by-step process.
        'Please send me your question',
        'Cool, now let's add the first answer option',
        'Great. Keep adding answer options,
         then send /done when you're ready'.

        The last option is definitely more attractive.

        And if you use ForceReply in your bot's questions,
        it will receive the user's answers
        even if it only receives replies, commands and mentions —
        without any extra work for the user.

    https://core.telegram.org/bots/api#forcereply
    """

    force_reply: bool = Field(True)


class InlineKeyboardButton(TelegramBotApiType):
    """
    This object represents one button of an inline keyboard.

    You MUST use exactly one of the optional fields.

    https://core.telegram.org/bots/api#inlinekeyboardbutton
    """

    callback_data: None | str = Field(None, min_length=1, max_length=64)
    text: str = Field(...)
    url: None | str = Field(None)


class InlineKeyboardMarkup(TelegramBotApiType):
    """
    This object represents an inline keyboard
    that appears right next to the message it belongs to.

    https://core.telegram.org/bots/api#inlinekeyboardmarkup
    """

    inline_keyboard: list[list[InlineKeyboardButton]] = Field(
        default_factory=list,
    )


class KeyboardButton(TelegramBotApiType):
    """
    This object represents one button of the reply keyboard.

    For simple text buttons String can be used
    instead of this object to specify text of the button.

    Optional fields request_contact, request_location,
    and request_poll are mutually exclusive.

    https://core.telegram.org/bots/api#keyboardbutton
    """

    text: str = Field(...)


class Location(TelegramBotApiType):
    """
    This object represents a point on the map.

    https://core.telegram.org/bots/api#location
    """

    heading: None | int = Field(None, ge=1, le=360)
    horizontal_accuracy: None | float = Field(None, ge=0, le=1500)
    latitude: float = Field(...)
    live_period: None | int = Field(None)
    longitude: float = Field(...)
    proximity_alert_radius: None | int = Field(None)


class MaskPosition(TelegramBotApiType):
    """
    This object describes the position on faces where a mask should be placed by default.

    https://core.telegram.org/bots/api#maskposition
    """

    point: str = Field(...)
    scale: float = Field(...)
    x_shift: float = Field(...)
    y_shift: float = Field(...)


class Message(TelegramBotApiType):
    """
    This object represents a message.

    https://core.telegram.org/bots/api#message
    """

    audio: None | Audio = Field(None)
    caption: None | str = Field(None)
    chat: Chat = Field(...)
    date: datetime = Field(...)
    dice: None | Dice = Field(None)
    document: None | Document = Field(None)
    edit_date: None | datetime = Field(None)
    entities: Optional[list["MessageEntity"]] = Field(None)
    from_: Optional["User"] = Field(None, alias="from")
    message_id: int = Field(...)
    photo: Optional[list["PhotoSize"]] = Field(None)
    reply_markup: Optional["InlineKeyboardMarkup"] = Field(None)
    reply_to_message: Optional["Message"] = Field(None)
    sticker: Optional["Sticker"] = Field(None)
    text: None | str = Field(None)
    video: Optional["Video"] = Field(None)
    video_note: Optional["VideoNote"] = Field(None)
    voice: Optional["Voice"] = Field(None)

    class Config:
        fields = {
            "from_": "from",
        }


class MessageEntity(TelegramBotApiType):
    """
    This object represents one special entity in a text message.

    For example, hashtags, usernames, URLs, etc.

    https://core.telegram.org/bots/api#messageentity
    """

    language: None | str = Field(None)
    length: int = Field(...)
    offset: int = Field(...)
    type: str = Field(...)  # noqa: A003, VNE003
    url: None | str = Field(None)
    user: Optional["User"] = Field(None)


class PhotoSize(TelegramBotApiType):
    """
    This object represents one size of a photo or a file / sticker thumbnail.

    https://core.telegram.org/bots/api#photosize
    """

    file_id: str = Field(...)
    file_size: None | int = Field(None)
    file_unique_id: str = Field(...)
    height: int = Field(...)
    width: int = Field(...)


class ReplyKeyboardMarkup(TelegramBotApiType):
    """
    This object represents a custom keyboard with reply options
    (see Introduction to bots for details and examples).

    https://core.telegram.org/bots#keyboards
    https://core.telegram.org/bots/api#replykeyboardmarkup
    """

    keyboard: list[list[KeyboardButton]] = Field(default_factory=list)
    one_time_keyboard: bool = Field(False)
    resize_keyboard: bool = Field(False)


class ReplyKeyboardRemove(TelegramBotApiType):
    """
    Upon receiving a message with this object,
    Telegram clients will remove the current custom keyboard
    and display the default letter-keyboard.

    By default, custom keyboards are displayed
    until a new keyboard is sent by a bot.

    An exception is made for one-time keyboards
    that are hidden immediately
    after the user presses a button (see ReplyKeyboardMarkup).

    https://core.telegram.org/bots/api#replykeyboardremove
    """

    remove_keyboard: bool = Field(True)


class Sticker(TelegramBotApiType):
    """
    This object represents a sticker.

    https://core.telegram.org/bots/api#sticker
    """

    custom_emoji_id: None | str = Field(None)
    emoji: None | str = Field(None)
    file_id: str = Field(...)
    file_size: None | int = Field(None)
    file_unique_id: str = Field(...)
    height: int = Field(...)
    is_animated: bool = Field(...)
    is_premium: None | bool = Field(None)
    is_video: bool = Field(...)
    mask_position: None | MaskPosition = Field(None)
    premium_animation: None | File = Field(None)
    set_name: None | str = Field(None)
    thumb: None | PhotoSize = Field(None)
    type: str = Field(...)  # noqa: A003,VNE003
    width: int = Field(...)


class Update(TelegramBotApiType):
    """
    This object represents an incoming update.

    At most one of the optional parameters
    can be present in any given update.

    https://core.telegram.org/bots/api#update
    """

    callback_query: None | CallbackQuery = Field(None)
    channel_post: None | Message = Field(None)
    edited_channel_post: None | Message = Field(None)
    edited_message: None | Message = Field(None)
    message: None | Message = Field(None)
    update_id: int = Field(...)

    def get_chat(self) -> Chat:
        if self.message:
            return self.message.chat

        if self.edited_message:
            return self.edited_message.chat

        if (cbq := self.callback_query) and cbq.message:
            return cbq.message.chat

        raise ValueError(f"cannot get chat from {self}")

    def get_user(self) -> "User":
        if (obj := self.message) and obj.from_:
            return obj.from_

        if (obj := self.edited_message) and obj.from_:
            return obj.from_

        if self.callback_query:
            return self.callback_query.from_

        raise ValueError(f"cannot get user from {self}")


class User(TelegramBotApiType):
    """
    This object represents a Telegram user or bot.

    https://core.telegram.org/bots/api#user
    """

    added_to_attachment_menu: None | bool = Field(None)
    can_join_groups: None | bool = Field(None)
    can_read_all_group_messages: None | bool = Field(None)
    first_name: str = Field(...)
    id: int = Field(...)  # noqa: A003, VNE003
    is_bot: bool = Field(...)
    is_premium: None | bool = Field(None)
    language_code: None | str = Field(None)
    last_name: None | str = Field(None)
    supports_inline_queries: None | bool = Field(None)
    username: None | str = Field(None)


class Video(TelegramBotApiType):
    """
    This object represents a video file.

    https://core.telegram.org/bots/api#video
    """

    duration: int = Field(...)
    file_id: str = Field(...)
    file_name: None | str = Field(None)
    file_size: None | int = Field(None)
    file_unique_id: str = Field(...)
    height: int = Field(...)
    mime_type: None | str = Field(None)
    thumb: None | PhotoSize = Field(None)
    width: int = Field(...)


class VideoNote(TelegramBotApiType):
    """
    This object represents a video message.

    https://core.telegram.org/bots/api#videonote
    """

    duration: int = Field(...)
    file_id: str = Field(...)
    file_size: None | int = Field(None)
    file_unique_id: str = Field(...)
    length: int = Field(...)
    thumb: None | PhotoSize = Field(None)


class Voice(TelegramBotApiType):
    """
    This object represents a voice note.

    https://core.telegram.org/bots/api#voice
    """

    duration: int = Field(...)
    file_id: str = Field(...)
    file_size: None | int = Field(None)
    file_unique_id: str = Field(...)
    mime_type: None | str = Field(None)


class WebhookInfo(TelegramBotApiType):
    """
    Contains information about the current status of a webhook.

    https://core.telegram.org/bots/api#webhookinfo
    """

    allowed_updates: list[str] | None = Field(None)
    has_custom_certificate: bool = Field(...)
    ip_address: None | str = Field(None)
    last_error_date: None | datetime = Field(None)
    last_error_message: None | str = Field(None)
    max_connections: None | int = Field(None)
    pending_update_count: int = Field(0)
    url: str = Field(...)


ReplyMarkupType = (
    ForceReply
    | InlineKeyboardMarkup  # noqa: W503
    | ReplyKeyboardMarkup  # noqa: W503
    | ReplyKeyboardRemove  # noqa: W503
)

__models__: set[Type[TelegramBotApiType]] = {
    Audio,
    BotCommand,
    BotCommandScope,
    BotCommandScopeDefault,
    CallbackQuery,
    Chat,
    ChatLocation,
    ChatPermissions,
    ChatPhoto,
    Dice,
    Document,
    File,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Location,
    MaskPosition,
    Message,
    MessageEntity,
    PhotoSize,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Sticker,
    Update,
    User,
    Video,
    VideoNote,
    Voice,
    WebhookInfo,
}

__all__ = (
    "__models__",
    "Audio",
    "BotCommand",
    "BotCommandScope",
    "BotCommandScopeDefault",
    "CallbackQuery",
    "Chat",
    "ChatLocation",
    "ChatPermissions",
    "ChatPhoto",
    "Dice",
    "Document",
    "File",
    "ForceReply",
    "InlineKeyboardButton",
    "InlineKeyboardMarkup",
    "KeyboardButton",
    "Location",
    "MaskPosition",
    "Message",
    "MessageEntity",
    "PhotoSize",
    "ReplyKeyboardMarkup",
    "ReplyKeyboardRemove",
    "ReplyMarkupType",
    "Sticker",
    "Update",
    "User",
    "Video",
    "VideoNote",
    "Voice",
    "WebhookInfo",
)
