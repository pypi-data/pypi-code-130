#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	Any
)

from tgsdk import TelegramEntity
from tgsdk import User
from tgsdk.utils import constants


class ChatMember(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#chatmember

	"""

	__slots__ = (
		"user", "status", "custom_title", "is_anonymous", "can_be_edited", "can_post_messages", "can_edit_messages", "can_delete_messages",
		"can_restrict_members", "can_promote_members", "can_change_info", "can_invite_users", "can_pin_messages", "is_member", "can_send_messages",
		"can_send_media_messages", "can_send_polls", "can_send_other_messages", "can_add_web_page_previews", "until_date", "can_manage_voice_chats",
		"can_manage_chat", "can_manage_video_chats",
	)

	CHAT_MEMBER_CREATOR = constants.CHAT_MEMBER_CREATOR  # type: str
	CHAT_MEMBER_ADMINISTRATOR = constants.CHAT_MEMBER_ADMINISTRATOR  # type: str
	CHAT_MEMBER_MEMBER = constants.CHAT_MEMBER_MEMBER  # type: str
	CHAT_MEMBER_LEFT = constants.CHAT_MEMBER_LEFT  # type: str
	CHAT_MEMBER_KICKED = constants.CHAT_MEMBER_KICKED  # type: str
	CHAT_MEMBER_RESTRICTED = constants.CHAT_MEMBER_RESTRICTED  # type: str

	def __init__(
		self,
		user: User,
		status: str,
		custom_title: Optional[str] = None,
		is_anonymous: Optional[bool] = None,
		can_be_edited: Optional[bool] = None,
		can_manage_chat: Optional[bool] = None,
		can_post_messages: Optional[bool] = None,
		can_edit_messages: Optional[bool] = None,
		can_delete_messages: Optional[bool] = None,
		can_manage_voice_chats: Optional[bool] = None,
		can_restrict_members: Optional[bool] = None,
		can_promote_members: Optional[bool] = None,
		can_change_info: Optional[bool] = None,
		can_invite_users: Optional[bool] = None,
		can_pin_messages: Optional[bool] = None,
		is_member: Optional[bool] = None,
		can_send_messages: Optional[bool] = None,
		can_send_media_messages: Optional[bool] = None,
		can_send_polls: Optional[bool] = None,
		can_send_other_messages: Optional[bool] = None,
		can_add_web_page_previews: Optional[bool] = None,
		can_manage_video_chats: Optional[bool] = None,
		until_date: Optional[int] = None,

		**_kwargs: Any
	):
		self.user = user
		self.status = status
		self.custom_title = custom_title
		self.is_anonymous = is_anonymous
		self.can_be_edited = can_be_edited
		self.can_manage_chat = can_manage_chat
		self.can_post_messages = can_post_messages
		self.can_edit_messages = can_edit_messages
		self.can_delete_messages = can_delete_messages
		self.can_manage_voice_chats = can_manage_voice_chats
		self.can_restrict_members = can_restrict_members
		self.can_promote_members = can_promote_members
		self.can_change_info = can_change_info
		self.can_invite_users = can_invite_users
		self.can_pin_messages = can_pin_messages
		self.is_member = is_member
		self.can_send_messages = can_send_messages
		self.can_send_media_messages = can_send_media_messages
		self.can_send_polls = can_send_polls
		self.can_send_other_messages = can_send_other_messages
		self.can_add_web_page_previews = can_add_web_page_previews
		self.can_manage_video_chats = can_manage_video_chats
		self.until_date = until_date

	@classmethod
	def de_json(cls, data: Optional[Dict] = None):
		if not data:
			return None

		data["user"] = User.de_json(data.get("user"))

		return cls(**data)
