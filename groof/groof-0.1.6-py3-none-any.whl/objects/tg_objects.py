""" All telegram objects from https://core.telegram.org/bots/api (v 6.0) """

from __future__ import annotations

from dataclasses import dataclass

from ..base import TgObject


# ==> Section: https://core.telegram.org/bots/api#getting-updates

@dataclass
class Update(TgObject):
    """ https://core.telegram.org/bots/api#update """

    update_id: int
    message: Message = None
    edited_message: Message = None
    channel_post: Message = None
    edited_channel_post: Message = None
    inline_query: InlineQuery = None
    chosen_inline_result: ChosenInlineResult = None
    callback_query: CallbackQuery = None
    shipping_query: ShippingQuery = None
    pre_checkout_query: PreCheckoutQuery = None
    poll: Poll = None
    poll_answer: PollAnswer = None
    my_chat_member: ChatMemberUpdated = None
    chat_member: ChatMemberUpdated = None
    chat_join_request: ChatJoinRequest = None


@dataclass
class WebhookInfo(TgObject):
    """ https://core.telegram.org/bots/api#webhookinfo """

    url: str
    has_custom_certificate: bool
    pending_update_count: int
    ip_address: str = None
    last_error_date: int = None
    last_error_message: str = None
    last_synchronization_error_date: int = None
    max_connections: int = None
    allowed_updates: list[str] = None


# ==> Section: https://core.telegram.org/bots/api#available-types

@dataclass
class User(TgObject):
    """ https://core.telegram.org/bots/api#user """

    id: int
    is_bot: bool
    first_name: str
    last_name: str = None
    username: str = None
    language_code: str = None
    can_join_groups: bool = None
    can_read_all_group_messages: bool = None
    supports_inline_queries: bool = None


@dataclass
class Chat(TgObject):
    """ https://core.telegram.org/bots/api#chat """

    id: int
    type: str
    title: str = None
    username: str = None
    first_name: str = None
    last_name: str = None
    photo: ChatPhoto = None
    bio: str = None
    has_private_forwards: bool = None
    description: str = None
    invite_link: str = None
    pinned_message: Message = None
    permissions: ChatPermissions = None
    slow_mode_delay: int = None
    message_auto_delete_time: int = None
    has_protected_content: bool = None
    sticker_set_name: str = None
    can_set_sticker_set: bool = None
    linked_chat_id: int = None
    location: ChatLocation = None


@dataclass
class Message(TgObject):
    """ https://core.telegram.org/bots/api#message """

    message_id: int
    date: int
    chat: Chat
    from_user: User = None
    sender_chat: Chat = None
    forward_from: User = None
    forward_from_chat: Chat = None
    forward_from_message_id: int = None
    forward_signature: str = None
    forward_sender_name: str = None
    forward_date: int = None
    is_automatic_forward: bool = None
    reply_to_message: Message = None
    via_bot: User = None
    edit_date: int = None
    has_protected_content: bool = None
    media_group_id: str = None
    author_signature: str = None
    text: str = None
    entities: list[MessageEntity] = None
    animation: Animation = None
    audio: Audio = None
    document: Document = None
    photo: list[PhotoSize] = None
    sticker: Sticker = None
    video: Video = None
    video_note: VideoNote = None
    voice: Voice = None
    caption: str = None
    caption_entities: list[MessageEntity] = None
    contact: Contact = None
    dice: Dice = None
    game: Game = None
    poll: Poll = None
    venue: Venue = None
    location: Location = None
    new_chat_members: list[User] = None
    left_chat_member: User = None
    new_chat_title: str = None
    new_chat_photo: list[PhotoSize] = None
    delete_chat_photo: bool = None
    group_chat_created: bool = None
    supergroup_chat_created: bool = None
    channel_chat_created: bool = None
    message_auto_delete_timer_changed: MessageAutoDeleteTimerChanged = None
    migrate_to_chat_id: int = None
    migrate_from_chat_id: int = None
    pinned_message: Message = None
    invoice: Invoice = None
    successful_payment: SuccessfulPayment = None
    connected_website: str = None
    passport_data: PassportData = None
    proximity_alert_triggered: ProximityAlertTriggered = None
    video_chat_scheduled: VideoChatScheduled = None
    video_chat_started: VideoChatStarted = None
    video_chat_ended: VideoChatEnded = None
    video_chat_participants_invited: VideoChatParticipantsInvited = None
    web_app_data: WebAppData = None
    reply_markup: InlineKeyboardMarkup = None


@dataclass
class MessageId(TgObject):
    """ https://core.telegram.org/bots/api#messageid """

    message_id: int


@dataclass
class MessageEntity(TgObject):
    """ https://core.telegram.org/bots/api#messageentity """

    type: str
    offset: int
    length: int
    url: str = None
    user: User = None
    language: str = None


@dataclass
class PhotoSize(TgObject):
    """ https://core.telegram.org/bots/api#photosize """

    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: int = None


@dataclass
class Animation(TgObject):
    """ https://core.telegram.org/bots/api#animation """

    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: PhotoSize = None
    file_name: str = None
    mime_type: str = None
    file_size: int = None


@dataclass
class Audio(TgObject):
    """ https://core.telegram.org/bots/api#audio """

    file_id: str
    file_unique_id: str
    duration: int
    performer: str = None
    title: str = None
    file_name: str = None
    mime_type: str = None
    file_size: int = None
    thumb: PhotoSize = None


@dataclass
class Document(TgObject):
    """ https://core.telegram.org/bots/api#document """

    file_id: str
    file_unique_id: str
    thumb: PhotoSize = None
    file_name: str = None
    mime_type: str = None
    file_size: int = None


@dataclass
class Video(TgObject):
    """ https://core.telegram.org/bots/api#video """

    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: PhotoSize = None
    file_name: str = None
    mime_type: str = None
    file_size: int = None


@dataclass
class VideoNote(TgObject):
    """ https://core.telegram.org/bots/api#videonote """

    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumb: PhotoSize = None
    file_size: int = None


@dataclass
class Voice(TgObject):
    """ https://core.telegram.org/bots/api#voice """

    file_id: str
    file_unique_id: str
    duration: int
    mime_type: str = None
    file_size: int = None


@dataclass
class Contact(TgObject):
    """ https://core.telegram.org/bots/api#contact """

    phone_number: str
    first_name: str
    last_name: str = None
    user_id: int = None
    vcard: str = None


@dataclass
class Dice(TgObject):
    """ https://core.telegram.org/bots/api#dice """

    emoji: str
    value: int


@dataclass
class PollOption(TgObject):
    """ https://core.telegram.org/bots/api#polloption """

    text: str
    voter_count: int


@dataclass
class PollAnswer(TgObject):
    """ https://core.telegram.org/bots/api#pollanswer """

    poll_id: str
    user: User
    option_ids: list[int]


@dataclass
class Poll(TgObject):
    """ https://core.telegram.org/bots/api#poll """

    id: str
    question: str
    options: list[PollOption]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type: str
    allows_multiple_answers: bool
    correct_option_id: int = None
    explanation: str = None
    explanation_entities: list[MessageEntity] = None
    open_period: int = None
    close_date: int = None


@dataclass
class Location(TgObject):
    """ https://core.telegram.org/bots/api#location """

    longitude: float
    latitude: float
    horizontal_accuracy: float = None
    live_period: int = None
    heading: int = None
    proximity_alert_radius: int = None


@dataclass
class Venue(TgObject):
    """ https://core.telegram.org/bots/api#venue """

    location: Location
    title: str
    address: str
    foursquare_id: str = None
    foursquare_type: str = None
    google_place_id: str = None
    google_place_type: str = None


@dataclass
class WebAppData(TgObject):
    """ https://core.telegram.org/bots/api#webappdata """

    data: str
    button_text: str


@dataclass
class ProximityAlertTriggered(TgObject):
    """ https://core.telegram.org/bots/api#proximityalerttriggered """

    traveler: User
    watcher: User
    distance: int


@dataclass
class MessageAutoDeleteTimerChanged(TgObject):
    """ https://core.telegram.org/bots/api#messageautodeletetimerchanged """

    message_auto_delete_time: int


@dataclass
class VideoChatScheduled(TgObject):
    """ https://core.telegram.org/bots/api#videochatscheduled """

    start_date: int


@dataclass
class VideoChatStarted(TgObject):
    """ https://core.telegram.org/bots/api#videochatstarted """


@dataclass
class VideoChatEnded(TgObject):
    """ https://core.telegram.org/bots/api#videochatended """

    duration: int


@dataclass
class VideoChatParticipantsInvited(TgObject):
    """ https://core.telegram.org/bots/api#videochatparticipantsinvited """

    users: list[User]


@dataclass
class UserProfilePhotos(TgObject):
    """ https://core.telegram.org/bots/api#userprofilephotos """

    total_count: int
    photos: list[list[PhotoSize]]


@dataclass
class File(TgObject):
    """ https://core.telegram.org/bots/api#file """

    file_id: str
    file_unique_id: str
    file_size: int = None
    file_path: str = None


@dataclass
class WebAppInfo(TgObject):
    """ https://core.telegram.org/bots/api#webappinfo """

    url: str


@dataclass
class ReplyKeyboardMarkup(TgObject):
    """ https://core.telegram.org/bots/api#replykeyboardmarkup """

    keyboard: list[list[KeyboardButton]]
    resize_keyboard: bool = None
    one_time_keyboard: bool = None
    input_field_placeholder: str = None
    selective: bool = None


@dataclass
class KeyboardButton(TgObject):
    """ https://core.telegram.org/bots/api#keyboardbutton """

    text: str
    request_contact: bool = None
    request_location: bool = None
    request_poll: KeyboardButtonPollType = None
    web_app: WebAppInfo = None


@dataclass
class KeyboardButtonPollType(TgObject):
    """ https://core.telegram.org/bots/api#keyboardbuttonpolltype """

    type: str = None


@dataclass
class ReplyKeyboardRemove(TgObject):
    """ https://core.telegram.org/bots/api#replykeyboardremove """

    remove_keyboard: bool = True
    selective: bool = None


@dataclass
class InlineKeyboardMarkup(TgObject):
    """ https://core.telegram.org/bots/api#inlinekeyboardmarkup """

    inline_keyboard: list[list[InlineKeyboardButton]]


@dataclass
class InlineKeyboardButton(TgObject):
    """ https://core.telegram.org/bots/api#inlinekeyboardbutton """

    text: str
    url: str = None
    callback_data: str = None
    web_app: WebAppInfo = None
    login_url: LoginUrl = None
    switch_inline_query: str = None
    switch_inline_query_current_chat: str = None
    callback_game: CallbackGame = None
    pay: bool = None


@dataclass
class LoginUrl(TgObject):
    """ https://core.telegram.org/bots/api#loginurl """

    url: str
    forward_text: str = None
    bot_username: str = None
    request_write_access: bool = None


@dataclass
class CallbackQuery(TgObject):
    """ https://core.telegram.org/bots/api#callbackquery """

    id: str
    from_user: User
    chat_instance: str
    message: Message = None
    inline_message_id: str = None
    data: str = None
    game_short_name: str = None


@dataclass
class ForceReply(TgObject):
    """ https://core.telegram.org/bots/api#forcereply """

    force_reply: bool
    input_field_placeholder: str = None
    selective: bool = None


@dataclass
class ChatPhoto(TgObject):
    """ https://core.telegram.org/bots/api#chatphoto """

    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_file_unique_id: str


@dataclass
class ChatInviteLink(TgObject):
    """ https://core.telegram.org/bots/api#chatinvitelink """

    invite_link: str
    creator: User
    creates_join_request: bool
    is_primary: bool
    is_revoked: bool
    name: str = None
    expire_date: int = None
    member_limit: int = None
    pending_join_request_count: int = None


@dataclass
class ChatAdministratorRights(TgObject):
    """ https://core.telegram.org/bots/api#chatadministratorrights """

    is_anonymous: bool
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_messages: bool = None
    can_edit_messages: bool = None
    can_pin_messages: bool = None


# abstract
class ChatMember(TgObject):
    """ https://core.telegram.org/bots/api#chatmember """

    status: str
    user: User


@dataclass
class ChatMemberOwner(ChatMember):
    """ https://core.telegram.org/bots/api#chatmemberowner """

    user: User
    is_anonymous: bool
    custom_title: str = None
    status: str = 'creator'


@dataclass
class ChatMemberAdministrator(ChatMember):
    """ https://core.telegram.org/bots/api#chatmemberadministrator """

    user: User
    can_be_edited: bool
    is_anonymous: bool
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_messages: bool = None
    can_edit_messages: bool = None
    can_pin_messages: bool = None
    custom_title: str = None
    status: str = 'administrator'


@dataclass
class ChatMemberMember(ChatMember):
    """ https://core.telegram.org/bots/api#chatmembermember """

    user: User
    status: str = 'member'


@dataclass
class ChatMemberRestricted(ChatMember):
    """ https://core.telegram.org/bots/api#chatmemberrestricted """

    user: User
    is_member: bool
    can_change_info: bool
    can_invite_users: bool
    can_pin_messages: bool
    can_send_messages: bool
    can_send_media_messages: bool
    can_send_polls: bool
    can_send_other_messages: bool
    can_add_web_page_previews: bool
    until_date: int
    status: str = 'restricted'


@dataclass
class ChatMemberLeft(ChatMember):
    """ https://core.telegram.org/bots/api#chatmemberleft """

    user: User
    status: str = 'left'


@dataclass
class ChatMemberBanned(ChatMember):
    """ https://core.telegram.org/bots/api#chatmemberbanned """

    user: User
    until_date: int
    status: str = 'kicked'


ChatMemberT = ChatMemberAdministrator | ChatMemberOwner | ChatMemberRestricted \
              | ChatMemberBanned | ChatMemberMember | ChatMemberLeft


@dataclass
class ChatMemberUpdated(TgObject):
    """ https://core.telegram.org/bots/api#chatmemberupdated """

    chat: Chat
    from_user: User
    date: int
    old_chat_member: ChatMemberT
    new_chat_member: ChatMemberT
    invite_link: ChatInviteLink = None


@dataclass
class ChatJoinRequest(TgObject):
    """ https://core.telegram.org/bots/api#chatjoinrequest """

    chat: Chat
    from_user: User
    date: int
    bio: str = None
    invite_link: ChatInviteLink = None


@dataclass
class ChatPermissions(TgObject):
    """ https://core.telegram.org/bots/api#chatpermissions """

    can_send_messages: bool = None
    can_send_media_messages: bool = None
    can_send_polls: bool = None
    can_send_other_messages: bool = None
    can_add_web_page_previews: bool = None
    can_change_info: bool = None
    can_invite_users: bool = None
    can_pin_messages: bool = None


@dataclass
class ChatLocation(TgObject):
    """ https://core.telegram.org/bots/api#chatlocation """

    location: Location
    address: str


@dataclass
class BotCommand(TgObject):
    """ https://core.telegram.org/bots/api#botcommand """

    command: str
    description: str


# abstract
class BotCommandScope(TgObject):
    """ https://core.telegram.org/bots/api#botcommandscope """

    type: str


@dataclass
class BotCommandScopeDefault(BotCommandScope):
    """ https://core.telegram.org/bots/api#botcommandscopedefault """

    type: str = 'default'


@dataclass
class BotCommandScopeAllPrivateChats(BotCommandScope):
    """ https://core.telegram.org/bots/api#botcommandscopeallprivatechats """

    type: str = 'all_private_chats'


@dataclass
class BotCommandScopeAllGroupChats(BotCommandScope):
    """ https://core.telegram.org/bots/api#botcommandscopeallgroupchats """

    type: str = 'all_group_chats'


@dataclass
class BotCommandScopeAllChatAdministrators(BotCommandScope):
    """ https://core.telegram.org/bots/api#botcommandscopeallchatadministrators """

    type: str = 'all_chat_administrators'


@dataclass
class BotCommandScopeChat(BotCommandScope):
    """ https://core.telegram.org/bots/api#botcommandscopechat """

    chat_id: int | str
    type: str = 'chat'


@dataclass
class BotCommandScopeChatAdministrators(BotCommandScope):
    """ https://core.telegram.org/bots/api#botcommandscopechatadministrators """

    chat_id: int | str
    type: str = 'chat_administrators'


@dataclass
class BotCommandScopeChatMember(BotCommandScope):
    """ https://core.telegram.org/bots/api#botcommandscopechatmember """

    chat_id: int | str
    user_id: int
    type: str = 'chat_member'


@dataclass
class MenuButton(TgObject):
    """ https://core.telegram.org/bots/api#menubutton """


@dataclass
class MenuButtonCommands(MenuButton):
    """ https://core.telegram.org/bots/api#menubuttoncommands """

    type: str


@dataclass
class MenuButtonWebApp(MenuButton):
    """ https://core.telegram.org/bots/api#menubuttonwebapp """

    type: str
    text: str
    web_app: WebAppInfo


@dataclass
class MenuButtonDefault(MenuButton):
    """ https://core.telegram.org/bots/api#menubuttondefault """

    type: str


@dataclass
class ResponseParameters(TgObject):
    """ https://core.telegram.org/bots/api#responseparameters """

    migrate_to_chat_id: int = None
    retry_after: int = None


@dataclass
class InputMedia(TgObject):
    """ https://core.telegram.org/bots/api#inputmedia """


@dataclass
class InputMediaPhoto(InputMedia):
    """ https://core.telegram.org/bots/api#inputmediaphoto """

    media: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    type: str = 'photo'


@dataclass
class InputMediaVideo(InputMedia):
    """ https://core.telegram.org/bots/api#inputmediavideo """

    media: str
    thumb: InputFile | str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    width: int = None
    height: int = None
    duration: int = None
    supports_streaming: bool = None
    type: str = 'video'


@dataclass
class InputMediaAnimation(InputMedia):
    """ https://core.telegram.org/bots/api#inputmediaanimation """

    media: str
    thumb: InputFile | str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    width: int = None
    height: int = None
    duration: int = None
    type: str = 'animation'


@dataclass
class InputMediaAudio(InputMedia):
    """ https://core.telegram.org/bots/api#inputmediaaudio """

    media: str
    thumb: InputFile | str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    duration: int = None
    performer: str = None
    title: str = None
    type: str = 'audio'


@dataclass
class InputMediaDocument(InputMedia):
    """ https://core.telegram.org/bots/api#inputmediadocument """

    media: str
    thumb: InputFile | str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    disable_content_type_detection: bool = None
    type: str = 'document'


@dataclass
class InputFile(TgObject):
    """ https://core.telegram.org/bots/api#inputfile """

    path: str
    name: str = None


# ==> Section: https://core.telegram.org/bots/api#stickers

@dataclass
class Sticker(TgObject):
    """ https://core.telegram.org/bots/api#sticker """

    file_id: str
    file_unique_id: str
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumb: PhotoSize = None
    emoji: str = None
    set_name: str = None
    mask_position: MaskPosition = None
    file_size: int = None


@dataclass
class StickerSet(TgObject):
    """ https://core.telegram.org/bots/api#stickerset """

    name: str
    title: str
    is_animated: bool
    is_video: bool
    contains_masks: bool
    stickers: list[Sticker]
    thumb: PhotoSize = None


@dataclass
class MaskPosition(TgObject):
    """ https://core.telegram.org/bots/api#maskposition """

    point: str
    x_shift: float
    y_shift: float
    scale: float


# ==> Section: https://core.telegram.org/bots/api#inline-mode

@dataclass
class InlineQuery(TgObject):
    """ https://core.telegram.org/bots/api#inlinequery """

    id: str
    from_user: User
    query: str
    offset: str
    chat_type: str = None
    location: Location = None


@dataclass
class InlineQueryResult(TgObject):
    """ https://core.telegram.org/bots/api#inlinequeryresult """


@dataclass
class InlineQueryResultArticle(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultarticle """

    type: str
    id: str
    title: str
    input_message_content: InputMessageContent
    reply_markup: InlineKeyboardMarkup = None
    url: str = None
    hide_url: bool = None
    description: str = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


@dataclass
class InlineQueryResultPhoto(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultphoto """

    type: str
    id: str
    photo_url: str
    thumb_url: str
    photo_width: int = None
    photo_height: int = None
    title: str = None
    description: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultGif(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultgif """

    type: str
    id: str
    gif_url: str
    thumb_url: str
    gif_width: int = None
    gif_height: int = None
    gif_duration: int = None
    thumb_mime_type: str = None
    title: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultMpeg4Gif(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultmpeg4gif """

    type: str
    id: str
    mpeg4_url: str
    thumb_url: str
    mpeg4_width: int = None
    mpeg4_height: int = None
    mpeg4_duration: int = None
    thumb_mime_type: str = None
    title: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultVideo(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultvideo """

    type: str
    id: str
    video_url: str
    mime_type: str
    thumb_url: str
    title: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    video_width: int = None
    video_height: int = None
    video_duration: int = None
    description: str = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultAudio(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultaudio """

    type: str
    id: str
    audio_url: str
    title: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    performer: str = None
    audio_duration: int = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultVoice(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultvoice """

    type: str
    id: str
    voice_url: str
    title: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    voice_duration: int = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultDocument(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultdocument """

    type: str
    id: str
    title: str
    document_url: str
    mime_type: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    description: str = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


@dataclass
class InlineQueryResultLocation(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultlocation """

    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    horizontal_accuracy: float = None
    live_period: int = None
    heading: int = None
    proximity_alert_radius: int = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


@dataclass
class InlineQueryResultVenue(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultvenue """

    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: str = None
    foursquare_type: str = None
    google_place_id: str = None
    google_place_type: str = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


@dataclass
class InlineQueryResultContact(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultcontact """

    type: str
    id: str
    phone_number: str
    first_name: str
    last_name: str = None
    vcard: str = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


@dataclass
class InlineQueryResultGame(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultgame """

    type: str
    id: str
    game_short_name: str
    reply_markup: InlineKeyboardMarkup = None


@dataclass
class InlineQueryResultCachedPhoto(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultcachedphoto """

    type: str
    id: str
    photo_file_id: str
    title: str = None
    description: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultCachedGif(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultcachedgif """

    type: str
    id: str
    gif_file_id: str
    title: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultCachedMpeg4Gif(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultcachedmpeg4gif """

    type: str
    id: str
    mpeg4_file_id: str
    title: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultCachedSticker(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultcachedsticker """

    type: str
    id: str
    sticker_file_id: str
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultCachedDocument(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultcacheddocument """

    type: str
    id: str
    title: str
    document_file_id: str
    description: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultCachedVideo(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultcachedvideo """

    type: str
    id: str
    video_file_id: str
    title: str
    description: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultCachedVoice(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultcachedvoice """

    type: str
    id: str
    voice_file_id: str
    title: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InlineQueryResultCachedAudio(InlineQueryResult):
    """ https://core.telegram.org/bots/api#inlinequeryresultcachedaudio """

    type: str
    id: str
    audio_file_id: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


@dataclass
class InputMessageContent(TgObject):
    """ https://core.telegram.org/bots/api#inputmessagecontent """


@dataclass
class InputTextMessageContent(InputMessageContent):
    """ https://core.telegram.org/bots/api#inputtextmessagecontent """

    message_text: str
    parse_mode: str = None
    entities: list[MessageEntity] = None
    disable_web_page_preview: bool = None


@dataclass
class InputLocationMessageContent(InputMessageContent):
    """ https://core.telegram.org/bots/api#inputlocationmessagecontent """

    latitude: float
    longitude: float
    horizontal_accuracy: float = None
    live_period: int = None
    heading: int = None
    proximity_alert_radius: int = None


@dataclass
class InputVenueMessageContent(InputMessageContent):
    """ https://core.telegram.org/bots/api#inputvenuemessagecontent """

    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: str = None
    foursquare_type: str = None
    google_place_id: str = None
    google_place_type: str = None


@dataclass
class InputContactMessageContent(InputMessageContent):
    """ https://core.telegram.org/bots/api#inputcontactmessagecontent """

    phone_number: str
    first_name: str
    last_name: str = None
    vcard: str = None


@dataclass
class InputInvoiceMessageContent(InputMessageContent):
    """ https://core.telegram.org/bots/api#inputinvoicemessagecontent """

    title: str
    description: str
    payload: str
    provider_token: str
    currency: str
    prices: list[LabeledPrice]
    max_tip_amount: int = None
    suggested_tip_amounts: list[int] = None
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


@dataclass
class ChosenInlineResult(TgObject):
    """ https://core.telegram.org/bots/api#choseninlineresult """

    result_id: str
    from_user: User
    query: str
    location: Location = None
    inline_message_id: str = None


@dataclass
class SentWebAppMessage(TgObject):
    """ https://core.telegram.org/bots/api#sentwebappmessage """

    inline_message_id: str = None


# ==> Section: https://core.telegram.org/bots/api#payments

@dataclass
class LabeledPrice(TgObject):
    """ https://core.telegram.org/bots/api#labeledprice """

    label: str
    amount: int


@dataclass
class Invoice(TgObject):
    """ https://core.telegram.org/bots/api#invoice """

    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int


@dataclass
class ShippingAddress(TgObject):
    """ https://core.telegram.org/bots/api#shippingaddress """

    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str


@dataclass
class OrderInfo(TgObject):
    """ https://core.telegram.org/bots/api#orderinfo """

    name: str = None
    phone_number: str = None
    email: str = None
    shipping_address: ShippingAddress = None


@dataclass
class ShippingOption(TgObject):
    """ https://core.telegram.org/bots/api#shippingoption """

    id: str
    title: str
    prices: list[LabeledPrice]


@dataclass
class SuccessfulPayment(TgObject):
    """ https://core.telegram.org/bots/api#successfulpayment """

    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    shipping_option_id: str = None
    order_info: OrderInfo = None


@dataclass
class ShippingQuery(TgObject):
    """ https://core.telegram.org/bots/api#shippingquery """

    id: str
    from_user: User
    invoice_payload: str
    shipping_address: ShippingAddress


@dataclass
class PreCheckoutQuery(TgObject):
    """ https://core.telegram.org/bots/api#precheckoutquery """

    id: str
    from_user: User
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: str = None
    order_info: OrderInfo = None


# ==> Section: https://core.telegram.org/bots/api#telegram-passport

@dataclass
class PassportData(TgObject):
    """ https://core.telegram.org/bots/api#passportdata """

    data: list[EncryptedPassportElement]
    credentials: EncryptedCredentials


@dataclass
class PassportFile(TgObject):
    """ https://core.telegram.org/bots/api#passportfile """

    file_id: str
    file_unique_id: str
    file_size: int
    file_date: int


@dataclass
class EncryptedPassportElement(TgObject):
    """ https://core.telegram.org/bots/api#encryptedpassportelement """

    type: str
    hash: str
    data: str = None
    phone_number: str = None
    email: str = None
    files: list[PassportFile] = None
    front_side: PassportFile = None
    reverse_side: PassportFile = None
    selfie: PassportFile = None
    translation: list[PassportFile] = None


@dataclass
class EncryptedCredentials(TgObject):
    """ https://core.telegram.org/bots/api#encryptedcredentials """

    data: str
    hash: str
    secret: str


@dataclass
class PassportElementError(TgObject):
    """ https://core.telegram.org/bots/api#passportelementerror """


@dataclass
class PassportElementErrorDataField(PassportElementError):
    """ https://core.telegram.org/bots/api#passportelementerrordatafield """

    source: str
    type: str
    field_name: str
    data_hash: str
    message: str


@dataclass
class PassportElementErrorFrontSide(PassportElementError):
    """ https://core.telegram.org/bots/api#passportelementerrorfrontside """

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorReverseSide(PassportElementError):
    """ https://core.telegram.org/bots/api#passportelementerrorreverseside """

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorSelfie(PassportElementError):
    """ https://core.telegram.org/bots/api#passportelementerrorselfie """

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorFile(PassportElementError):
    """ https://core.telegram.org/bots/api#passportelementerrorfile """

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorFiles(PassportElementError):
    """ https://core.telegram.org/bots/api#passportelementerrorfiles """

    source: str
    type: str
    file_hashes: list[str]
    message: str


@dataclass
class PassportElementErrorTranslationFile(PassportElementError):
    """ https://core.telegram.org/bots/api#passportelementerrortranslationfile """

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorTranslationFiles(PassportElementError):
    """ https://core.telegram.org/bots/api#passportelementerrortranslationfiles """

    source: str
    type: str
    file_hashes: list[str]
    message: str


@dataclass
class PassportElementErrorUnspecified(PassportElementError):
    """ https://core.telegram.org/bots/api#passportelementerrorunspecified """

    source: str
    type: str
    element_hash: str
    message: str


# ==> Section: https://core.telegram.org/bots/api#games

@dataclass
class Game(TgObject):
    """ https://core.telegram.org/bots/api#game """

    title: str
    description: str
    photo: list[PhotoSize]
    text: str = None
    text_entities: list[MessageEntity] = None
    animation: Animation = None


@dataclass
class CallbackGame(TgObject):
    """ https://core.telegram.org/bots/api#callbackgame """

    user_id: int
    score: int
    force: bool = None
    disable_edit_message: bool = None
    chat_id: int = None
    message_id: int = None
    inline_message_id: str = None


@dataclass
class GameHighScore(TgObject):
    """ https://core.telegram.org/bots/api#gamehighscore """

    position: int
    user: User
    score: int
