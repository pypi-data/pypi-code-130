from .layer1 import ContextLayer1
from ..objects import PhotoSize, Document, Animation, Video, Audio


class ContextLayer2(ContextLayer1):

    @property
    def user_id(self) -> int | None:
        """ Message.user.id | CallbackQuery.user.id """
        value = None

        if user := self.user:
            value = user.id

        return value

    @property
    def query_data(self) -> str | None:
        """ CallbackQuery.data """

        value = None

        if callback_query := self.callback_query:
            value = callback_query.data

        return value

    @property
    def text(self) -> str | None:
        """ Message.text | ChannelPost.text | CallbackQuery.message.text """
        value = None

        if message := self.message:
            value = message.text

        return value

    @property
    def caption(self) -> str | None:
        """ Message.caption | ChannelPost.caption | CallbackQuery.message.caption """
        value = None

        if message := self.message:
            value = message.caption

        return value

    @property
    def photo(self) -> PhotoSize | None:
        """ Message.photo[-1] | ChannelPost.photo[-1] | CallbackQuery.message.photo[-1] """
        if message := self.message:
            if photo := message.photo:
                return photo[-1]

    @property
    def document(self) -> Document | None:
        """ Message.document | ChannelPost.document | CallbackQuery.message.document """
        if message := self.message:
            return message.document

    @property
    def animation(self) -> Animation | None:
        """ Message.animation | ChannelPost.animation | CallbackQuery.message.animation """
        if message := self.message:
            return message.animation

    @property
    def video(self) -> Video | None:
        """ Message.video | ChannelPost.video | CallbackQuery.message.video """
        if message := self.message:
            return message.video

    @property
    def audio(self) -> Audio | None:
        """ Message.audio | ChannelPost.audio | CallbackQuery.message.audio """
        if message := self.message:
            return message.audio

    @property
    def file_id(self) -> str | None:
        """
        Message.photo[-1].file_id | ChannelPost.photo[-1].file_id | CallbackQuery.message.photo[-1].file_id |
        Message.document.file_id | ChannelPost.document.file_id | CallbackQuery.message.document.file_id
        Message.animation.file_id | ChannelPost.animation.file_id | CallbackQuery.message.animation.file_id
        Message.video.file_id | ChannelPost.video.file_id | CallbackQuery.message.video.file_id
        Message.audio.file_id | ChannelPost.audio.file_id | CallbackQuery.message.audio.file_id
        """
        if photo := self.photo:
            return photo.file_id
        if document := self.document:
            return document.file_id
        if animation := self.animation:
            return animation.file_id
        if video := self.video:
            return video.file_id
        if audio := self.audio:
            return audio.file_id

    @property
    def chat_id(self) -> int | None:
        """ Message.chat.id | ChannelPost.chat.id | CallbackQuery.chat.id """
        value = None

        if chat := self.chat:
            value = chat.id

        return value

    @property
    def chat_type(self) -> int | None:
        """ Message.chat.type | ChannelPost.chat.type | CallbackQuery.chat.type """
        value = None

        if chat := self.chat:
            value = chat.type

        return value

    @property
    def callback_query_id(self) -> str | None:
        """ CallbackQuery.id """
        value = None

        if callback_query := self.callback_query:
            value = callback_query.id

        return value

    @property
    def message_id(self) -> int | None:
        """ Message.id | ChannelPost.id | CallbackQuery.message.id """
        value = None

        if message := self.message:
            value = message.message_id

        return value

    @property
    def media_group_id(self) -> str | None:
        """ Message.media_group_id | ChannelPost.media_group_id | CallbackQuery.message.media_group_id """
        value = None

        if message := self.message:
            value = message.media_group_id

        return value
