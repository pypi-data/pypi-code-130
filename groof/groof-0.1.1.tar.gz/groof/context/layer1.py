from .layer0 import ContextLayer0
from ..objects import Message, User, Chat, CallbackQuery, ChatMemberUpdated, ChatMemberT


class ContextLayer1(ContextLayer0):

    @property
    def message(self) -> Message | None:
        """ Message | ChannelPost | CallbackQuery.message """
        value = None

        if update := self.update:
            value = update.message or update.channel_post

            if value is None:
                if callback_query := self.callback_query:
                    value = callback_query.message

        return value

    @property
    def callback_query(self) -> CallbackQuery | None:
        """ CallbackQuery """
        value = None

        if update := self.update:
            value = update.callback_query

        return value

    @property
    def chat_member_updated(self) -> ChatMemberUpdated | None:
        """ MyChatMember | ChatMember """
        value = None

        if update := self.update:
            value = update.my_chat_member or update.chat_member

        return value

    @property
    def chat(self) -> Chat | None:
        """
        Message.chat | ChannelPost.chat | CallbackQuery.chat |
        MyChatMember.chat | ChatMember.chat
        """

        value = None

        if message := self.message:
            value = message.chat
        if chat_member_updated := self.chat_member_updated:
            value = chat_member_updated.chat

        return value

    @property
    def user(self) -> User | None:
        """ Message.user | CallbackQuery.user| MyChatMember.user | ChatMember.user """
        value = None

        if update := self.update:
            if message := update.message:
                value = message.from_user
            elif callback_query := update.callback_query:
                value = callback_query.from_user
            elif chat_member_updated := self.chat_member_updated:
                value = chat_member_updated.from_user

        return value

    @property
    def new_chat_member(self) -> ChatMemberT | None:
        """ MyChatMember.new_chat_member | ChatMember.new_chat_member """
        value = None

        if chat_member_updated := self.chat_member_updated:
            value = chat_member_updated.new_chat_member

        return value

    @property
    def old_chat_member(self) -> ChatMemberT | None:
        """ MyChatMember.old_chat_member | ChatMember.old_chat_member """
        value = None

        if chat_member_updated := self.chat_member_updated:
            value = chat_member_updated.old_chat_member

        return value
