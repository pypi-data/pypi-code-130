""" All telegram requests from https://core.telegram.org/bots/api (v 6.0) """

from __future__ import annotations

from .tg_objects import *
from ..base import TgMethod


# ==> Section: https://core.telegram.org/bots/api#getting-updates

@dataclass
class GetUpdates(TgMethod):
    """ https://core.telegram.org/bots/api#getupdates """

    offset: int = None
    limit: int = None
    timeout: int = None
    allowed_updates: list[str] = None

    __response_type__ = list[Update]


@dataclass
class SetWebhook(TgMethod):
    """ https://core.telegram.org/bots/api#setwebhook """

    url: str
    certificate: InputFile = None
    ip_address: str = None
    max_connections: int = None
    allowed_updates: list[str] = None
    drop_pending_updates: bool = None

    __response_type__ = bool


@dataclass
class DeleteWebhook(TgMethod):
    """ https://core.telegram.org/bots/api#deletewebhook """

    drop_pending_updates: bool = None

    __response_type__ = bool


@dataclass
class GetWebhookInfo(TgMethod):
    """ https://core.telegram.org/bots/api#getwebhookinfo """

    __response_type__ = WebhookInfo


# ==> Section: https://core.telegram.org/bots/api#available-methods

@dataclass
class GetMe(TgMethod):
    """ https://core.telegram.org/bots/api#getme """

    __response_type__ = User


@dataclass
class LogOut(TgMethod):
    """ https://core.telegram.org/bots/api#logout """

    __response_type__ = bool


@dataclass
class Close(TgMethod):
    """ https://core.telegram.org/bots/api#close """

    __response_type__ = bool


@dataclass
class SendMessage(TgMethod):
    """ https://core.telegram.org/bots/api#sendmessage """

    chat_id: int | str
    text: str
    parse_mode: str = None
    entities: list[MessageEntity] = None
    disable_web_page_preview: bool = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class ForwardMessage(TgMethod):
    """ https://core.telegram.org/bots/api#forwardmessage """

    chat_id: int | str
    from_chat_id: int | str
    message_id: int
    disable_notification: bool = None
    protect_content: bool = None

    __response_type__ = Message


@dataclass
class CopyMessage(TgMethod):
    """ https://core.telegram.org/bots/api#copymessage """

    chat_id: int | str
    from_chat_id: int | str
    message_id: int
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = MessageId


@dataclass
class SendPhoto(TgMethod):
    """ https://core.telegram.org/bots/api#sendphoto """

    chat_id: int | str
    photo: InputFile | str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendAudio(TgMethod):
    """ https://core.telegram.org/bots/api#sendaudio """

    chat_id: int | str
    audio: InputFile | str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    duration: int = None
    performer: str = None
    title: str = None
    thumb: InputFile | str = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendDocument(TgMethod):
    """ https://core.telegram.org/bots/api#senddocument """

    chat_id: int | str
    document: InputFile | str
    thumb: InputFile | str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    disable_content_type_detection: bool = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendVideo(TgMethod):
    """ https://core.telegram.org/bots/api#sendvideo """

    chat_id: int | str
    video: InputFile | str
    duration: int = None
    width: int = None
    height: int = None
    thumb: InputFile | str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    supports_streaming: bool = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendAnimation(TgMethod):
    """ https://core.telegram.org/bots/api#sendanimation """

    chat_id: int | str
    animation: InputFile | str
    duration: int = None
    width: int = None
    height: int = None
    thumb: InputFile | str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendVoice(TgMethod):
    """ https://core.telegram.org/bots/api#sendvoice """

    chat_id: int | str
    voice: InputFile | str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    duration: int = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendVideoNote(TgMethod):
    """ https://core.telegram.org/bots/api#sendvideonote """

    chat_id: int | str
    video_note: InputFile | str
    duration: int = None
    length: int = None
    thumb: InputFile | str = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendMediaGroup(TgMethod):
    """ https://core.telegram.org/bots/api#sendmediagroup """

    chat_id: int | str
    media: list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo]
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None

    __response_type__ = list[Message]


@dataclass
class SendLocation(TgMethod):
    """ https://core.telegram.org/bots/api#sendlocation """

    chat_id: int | str
    latitude: float
    longitude: float
    horizontal_accuracy: float = None
    live_period: int = None
    heading: int = None
    proximity_alert_radius: int = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class EditMessageLiveLocation(TgMethod):
    """ https://core.telegram.org/bots/api#editmessagelivelocation """

    latitude: float
    longitude: float
    chat_id: int | str = None
    message_id: int = None
    inline_message_id: str = None
    horizontal_accuracy: float = None
    heading: int = None
    proximity_alert_radius: int = None
    reply_markup: InlineKeyboardMarkup = None

    __response_type__ = Message | bool


@dataclass
class StopMessageLiveLocation(TgMethod):
    """ https://core.telegram.org/bots/api#stopmessagelivelocation """

    chat_id: int | str = None
    message_id: int = None
    inline_message_id: str = None
    reply_markup: InlineKeyboardMarkup = None

    __response_type__ = Message | bool


@dataclass
class SendVenue(TgMethod):
    """ https://core.telegram.org/bots/api#sendvenue """

    chat_id: int | str
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: str = None
    foursquare_type: str = None
    google_place_id: str = None
    google_place_type: str = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendContact(TgMethod):
    """ https://core.telegram.org/bots/api#sendcontact """

    chat_id: int | str
    phone_number: str
    first_name: str
    last_name: str = None
    vcard: str = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendPoll(TgMethod):
    """ https://core.telegram.org/bots/api#sendpoll """

    chat_id: int | str
    question: str
    options: list[str]
    is_anonymous: bool = None
    type: str = None
    allows_multiple_answers: bool = None
    correct_option_id: int = None
    explanation: str = None
    explanation_parse_mode: str = None
    explanation_entities: list[MessageEntity] = None
    open_period: int = None
    close_date: int = None
    is_closed: bool = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendDice(TgMethod):
    """ https://core.telegram.org/bots/api#senddice """

    chat_id: int | str
    emoji: str = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class SendChatAction(TgMethod):
    """ https://core.telegram.org/bots/api#sendchataction """

    chat_id: int | str
    action: str

    __response_type__ = bool


@dataclass
class GetUserProfilePhotos(TgMethod):
    """ https://core.telegram.org/bots/api#getuserprofilephotos """

    user_id: int
    offset: int = None
    limit: int = None

    __response_type__ = UserProfilePhotos


@dataclass
class GetFile(TgMethod):
    """ https://core.telegram.org/bots/api#getfile """

    file_id: str

    __response_type__ = File


@dataclass
class BanChatMember(TgMethod):
    """ https://core.telegram.org/bots/api#banchatmember """

    chat_id: int | str
    user_id: int
    until_date: int = None
    revoke_messages: bool = None

    __response_type__ = bool


@dataclass
class UnbanChatMember(TgMethod):
    """ https://core.telegram.org/bots/api#unbanchatmember """

    chat_id: int | str
    user_id: int
    only_if_banned: bool = None

    __response_type__ = bool


@dataclass
class RestrictChatMember(TgMethod):
    """ https://core.telegram.org/bots/api#restrictchatmember """

    chat_id: int | str
    user_id: int
    permissions: ChatPermissions
    until_date: int = None

    __response_type__ = bool


@dataclass
class PromoteChatMember(TgMethod):
    """ https://core.telegram.org/bots/api#promotechatmember """

    chat_id: int | str
    user_id: int
    is_anonymous: bool = None
    can_manage_chat: bool = None
    can_post_messages: bool = None
    can_edit_messages: bool = None
    can_delete_messages: bool = None
    can_manage_video_chats: bool = None
    can_restrict_members: bool = None
    can_promote_members: bool = None
    can_change_info: bool = None
    can_invite_users: bool = None
    can_pin_messages: bool = None

    __response_type__ = bool


@dataclass
class SetChatAdministratorCustomTitle(TgMethod):
    """ https://core.telegram.org/bots/api#setchatadministratorcustomtitle """

    chat_id: int | str
    user_id: int
    custom_title: str

    __response_type__ = bool


@dataclass
class BanChatSenderChat(TgMethod):
    """ https://core.telegram.org/bots/api#banchatsenderchat """

    chat_id: int | str
    sender_chat_id: int

    __response_type__ = bool


@dataclass
class UnbanChatSenderChat(TgMethod):
    """ https://core.telegram.org/bots/api#unbanchatsenderchat """

    chat_id: int | str
    sender_chat_id: int

    __response_type__ = bool


@dataclass
class SetChatPermissions(TgMethod):
    """ https://core.telegram.org/bots/api#setchatpermissions """

    chat_id: int | str
    permissions: ChatPermissions

    __response_type__ = bool


@dataclass
class ExportChatInviteLink(TgMethod):
    """ https://core.telegram.org/bots/api#exportchatinvitelink """

    chat_id: int | str

    __response_type__ = str


@dataclass
class CreateChatInviteLink(TgMethod):
    """ https://core.telegram.org/bots/api#createchatinvitelink """

    chat_id: int | str
    name: str = None
    expire_date: int = None
    member_limit: int = None
    creates_join_request: bool = None

    __response_type__ = ChatInviteLink


@dataclass
class EditChatInviteLink(TgMethod):
    """ https://core.telegram.org/bots/api#editchatinvitelink """

    chat_id: int | str
    invite_link: str
    name: str = None
    expire_date: int = None
    member_limit: int = None
    creates_join_request: bool = None

    __response_type__ = ChatInviteLink


@dataclass
class RevokeChatInviteLink(TgMethod):
    """ https://core.telegram.org/bots/api#revokechatinvitelink """

    chat_id: int | str
    invite_link: str

    __response_type__ = ChatInviteLink


@dataclass
class ApproveChatJoinRequest(TgMethod):
    """ https://core.telegram.org/bots/api#approvechatjoinrequest """

    chat_id: int | str
    user_id: int

    __response_type__ = bool


@dataclass
class DeclineChatJoinRequest(TgMethod):
    """ https://core.telegram.org/bots/api#declinechatjoinrequest """

    chat_id: int | str
    user_id: int

    __response_type__ = bool


@dataclass
class SetChatPhoto(TgMethod):
    """ https://core.telegram.org/bots/api#setchatphoto """

    chat_id: int | str
    photo: InputFile

    __response_type__ = bool


@dataclass
class DeleteChatPhoto(TgMethod):
    """ https://core.telegram.org/bots/api#deletechatphoto """

    chat_id: int | str

    __response_type__ = bool


@dataclass
class SetChatTitle(TgMethod):
    """ https://core.telegram.org/bots/api#setchattitle """

    chat_id: int | str
    title: str

    __response_type__ = bool


@dataclass
class SetChatDescription(TgMethod):
    """ https://core.telegram.org/bots/api#setchatdescription """

    chat_id: int | str
    description: str = None

    __response_type__ = bool


@dataclass
class PinChatMessage(TgMethod):
    """ https://core.telegram.org/bots/api#pinchatmessage """

    chat_id: int | str
    message_id: int
    disable_notification: bool = None

    __response_type__ = bool


@dataclass
class UnpinChatMessage(TgMethod):
    """ https://core.telegram.org/bots/api#unpinchatmessage """

    chat_id: int | str
    message_id: int = None

    __response_type__ = bool


@dataclass
class UnpinAllChatMessages(TgMethod):
    """ https://core.telegram.org/bots/api#unpinallchatmessages """

    chat_id: int | str

    __response_type__ = bool


@dataclass
class LeaveChat(TgMethod):
    """ https://core.telegram.org/bots/api#leavechat """

    chat_id: int | str

    __response_type__ = bool


@dataclass
class GetChat(TgMethod):
    """ https://core.telegram.org/bots/api#getchat """

    chat_id: int | str

    __response_type__ = Chat


@dataclass
class GetChatAdministrators(TgMethod):
    """ https://core.telegram.org/bots/api#getchatadministrators """

    chat_id: int | str

    __response_type__ = list[ChatMember]


@dataclass
class GetChatMemberCount(TgMethod):
    """ https://core.telegram.org/bots/api#getchatmembercount """

    chat_id: int | str

    __response_type__ = int


@dataclass
class GetChatMember(TgMethod):
    """ https://core.telegram.org/bots/api#getchatmember """

    chat_id: int | str
    user_id: int

    __response_type__ = ChatMemberT


@dataclass
class SetChatStickerSet(TgMethod):
    """ https://core.telegram.org/bots/api#setchatstickerset """

    chat_id: int | str
    sticker_set_name: str

    __response_type__ = bool


@dataclass
class DeleteChatStickerSet(TgMethod):
    """ https://core.telegram.org/bots/api#deletechatstickerset """

    chat_id: int | str

    __response_type__ = bool


@dataclass
class AnswerCallbackQuery(TgMethod):
    """ https://core.telegram.org/bots/api#answercallbackquery """

    callback_query_id: str
    text: str = None
    show_alert: bool = None
    url: str = None
    cache_time: int = None

    __response_type__ = bool


@dataclass
class SetMyCommands(TgMethod):
    """ https://core.telegram.org/bots/api#setmycommands """

    commands: list[BotCommand]
    scope: BotCommandScope = None
    language_code: str = None

    __response_type__ = bool


@dataclass
class DeleteMyCommands(TgMethod):
    """ https://core.telegram.org/bots/api#deletemycommands """

    scope: BotCommandScope = None
    language_code: str = None

    __response_type__ = bool


@dataclass
class GetMyCommands(TgMethod):
    """ https://core.telegram.org/bots/api#getmycommands """

    scope: BotCommandScope = None
    language_code: str = None

    __response_type__ = list[BotCommand]


@dataclass
class SetChatMenuButton(TgMethod):
    """ https://core.telegram.org/bots/api#setchatmenubutton """

    chat_id: int = None
    menu_button: MenuButton = None

    __response_type__ = bool


@dataclass
class GetChatMenuButton(TgMethod):
    """ https://core.telegram.org/bots/api#getchatmenubutton """

    chat_id: int = None

    __response_type__ = MenuButton


@dataclass
class SetMyDefaultAdministratorRights(TgMethod):
    """ https://core.telegram.org/bots/api#setmydefaultadministratorrights """

    rights: ChatAdministratorRights = None
    for_channels: bool = None

    __response_type__ = bool


@dataclass
class GetMyDefaultAdministratorRights(TgMethod):
    """ https://core.telegram.org/bots/api#getmydefaultadministratorrights """

    for_channels: bool = None

    __response_type__ = ChatAdministratorRights


# ==> Section: https://core.telegram.org/bots/api#updating-messages

@dataclass
class EditMessageText(TgMethod):
    """ https://core.telegram.org/bots/api#editmessagetext """

    text: str
    chat_id: int | str = None
    message_id: int = None
    inline_message_id: str = None
    parse_mode: str = None
    entities: list[MessageEntity] = None
    disable_web_page_preview: bool = None
    reply_markup: InlineKeyboardMarkup = None

    __response_type__ = Message | bool


@dataclass
class EditMessageCaption(TgMethod):
    """ https://core.telegram.org/bots/api#editmessagecaption """

    chat_id: int | str = None
    message_id: int = None
    inline_message_id: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None

    __response_type__ = Message | bool


@dataclass
class EditMessageMedia(TgMethod):
    """ https://core.telegram.org/bots/api#editmessagemedia """

    media: InputMedia
    chat_id: int | str = None
    message_id: int = None
    inline_message_id: str = None
    reply_markup: InlineKeyboardMarkup = None

    __response_type__ = Message | bool


@dataclass
class EditMessageReplyMarkup(TgMethod):
    """ https://core.telegram.org/bots/api#editmessagereplymarkup """

    chat_id: int | str = None
    message_id: int = None
    inline_message_id: str = None
    reply_markup: InlineKeyboardMarkup = None

    __response_type__ = Message | bool


@dataclass
class StopPoll(TgMethod):
    """ https://core.telegram.org/bots/api#stoppoll """

    chat_id: int | str
    message_id: int
    reply_markup: InlineKeyboardMarkup = None

    __response_type__ = Poll


@dataclass
class DeleteMessage(TgMethod):
    """ https://core.telegram.org/bots/api#deletemessage """

    chat_id: int | str
    message_id: int

    __response_type__ = bool


# ==> Section: https://core.telegram.org/bots/api#stickers

@dataclass
class SendSticker(TgMethod):
    """ https://core.telegram.org/bots/api#sendsticker """

    chat_id: int | str
    sticker: InputFile | str
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None

    __response_type__ = Message


@dataclass
class GetStickerSet(TgMethod):
    """ https://core.telegram.org/bots/api#getstickerset """

    name: str

    __response_type__ = StickerSet


@dataclass
class UploadStickerFile(TgMethod):
    """ https://core.telegram.org/bots/api#uploadstickerfile """

    user_id: int
    png_sticker: InputFile

    __response_type__ = File


@dataclass
class CreateNewStickerSet(TgMethod):
    """ https://core.telegram.org/bots/api#createnewstickerset """

    user_id: int
    name: str
    title: str
    emojis: str
    png_sticker: InputFile | str = None
    tgs_sticker: InputFile = None
    webm_sticker: InputFile = None
    contains_masks: bool = None
    mask_position: MaskPosition = None

    __response_type__ = bool


@dataclass
class AddStickerToSet(TgMethod):
    """ https://core.telegram.org/bots/api#addstickertoset """

    user_id: int
    name: str
    emojis: str
    png_sticker: InputFile | str = None
    tgs_sticker: InputFile = None
    webm_sticker: InputFile = None
    mask_position: MaskPosition = None

    __response_type__ = bool


@dataclass
class SetStickerPositionInSet(TgMethod):
    """ https://core.telegram.org/bots/api#setstickerpositioninset """

    sticker: str
    position: int

    __response_type__ = bool


@dataclass
class DeleteStickerFromSet(TgMethod):
    """ https://core.telegram.org/bots/api#deletestickerfromset """

    sticker: str

    __response_type__ = bool


@dataclass
class SetStickerSetThumb(TgMethod):
    """ https://core.telegram.org/bots/api#setstickersetthumb """

    name: str
    user_id: int
    thumb: InputFile | str = None

    __response_type__ = bool


# ==> Section: https://core.telegram.org/bots/api#inline-mode

@dataclass
class AnswerInlineQuery(TgMethod):
    """ https://core.telegram.org/bots/api#answerinlinequery """

    inline_query_id: str
    results: list[InlineQueryResult]
    cache_time: int = None
    is_personal: bool = None
    next_offset: str = None
    switch_pm_text: str = None
    switch_pm_parameter: str = None

    __response_type__ = bool


@dataclass
class AnswerWebAppQuery(TgMethod):
    """ https://core.telegram.org/bots/api#answerwebappquery """

    web_app_query_id: str
    result: InlineQueryResult

    __response_type__ = SentWebAppMessage


# ==> Section: https://core.telegram.org/bots/api#payments

@dataclass
class SendInvoice(TgMethod):
    """ https://core.telegram.org/bots/api#sendinvoice """

    chat_id: int | str
    title: str
    description: str
    payload: str
    provider_token: str
    currency: str
    prices: list[LabeledPrice]
    max_tip_amount: int = None
    suggested_tip_amounts: list[int] = None
    start_parameter: str = None
    provider_data: str = None
    photo_url: str = None
    photo_size: int = None
    photo_width: int = None
    photo_height: int = None
    need_name: bool = None
    need_phone_number: bool = None
    need_email: bool = None
    need_shipping_address: bool = None
    send_phone_number_to_provider: bool = None
    send_email_to_provider: bool = None
    is_flexible: bool = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup = None

    __response_type__ = Message


@dataclass
class AnswerShippingQuery(TgMethod):
    """ https://core.telegram.org/bots/api#answershippingquery """

    shipping_query_id: str
    ok: bool
    shipping_options: list[ShippingOption] = None
    error_message: str = None

    __response_type__ = bool


@dataclass
class AnswerPreCheckoutQuery(TgMethod):
    """ https://core.telegram.org/bots/api#answerprecheckoutquery """

    pre_checkout_query_id: str
    ok: bool
    error_message: str = None

    __response_type__ = bool


# ==> Section: https://core.telegram.org/bots/api#telegram-passport

@dataclass
class SetPassportDataErrors(TgMethod):
    """ https://core.telegram.org/bots/api#setpassportdataerrors """

    user_id: int
    errors: list[PassportElementError]

    __response_type__ = bool


# ==> Section: https://core.telegram.org/bots/api#games

@dataclass
class SendGame(TgMethod):
    """ https://core.telegram.org/bots/api#sendgame """

    chat_id: int
    game_short_name: str
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: InlineKeyboardMarkup = None

    __response_type__ = Message


@dataclass
class SetGameScore(TgMethod):
    """ https://core.telegram.org/bots/api#setgamescore """

    user_id: int
    score: int
    force: bool = None
    disable_edit_message: bool = None
    chat_id: int = None
    message_id: int = None
    inline_message_id: str = None

    __response_type__ = Message | bool


@dataclass
class GetGameHighScores(TgMethod):
    """ https://core.telegram.org/bots/api#getgamehighscores """

    user_id: int
    chat_id: int = None
    message_id: int = None
    inline_message_id: str = None

    __response_type__ = list[GameHighScore]
