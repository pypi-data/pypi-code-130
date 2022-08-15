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


class ChatInviteLink(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#chatinvitelink

	"""

	__slots__ = (
		"invite_link", "creator", "is_primary", "is_revoked", "expire_date", "member_limit",
		"creates_join_request", "name", "pending_join_request_count"
	)

	def __init__(
		self,
		invite_link: str,
		creator: User,
		is_primary: bool,
		is_revoked: bool,
		name: Optional[str] = None,
		creates_join_request: Optional[bool] = False,
		expire_date: Optional[int] = None,
		member_limit: Optional[int] = None,
		pending_join_request_count: Optional[int] = None,

		**_kwargs: Any
	):
		self.invite_link = invite_link
		self.creator = creator
		self.is_primary = is_primary
		self.is_revoked = is_revoked
		self.expire_date = expire_date
		self.member_limit = member_limit
		self.creates_join_request = creates_join_request
		self.name = name
		self.pending_join_request_count = pending_join_request_count

	@classmethod
	def de_json(cls, data: Optional[Dict] = None):
		if not data:
			return None

		data["creator"] = User.de_json(data.get("creator"))

		return cls(**data)
