#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Any
)

from tgsdk import (
	TelegramEntity,
	KeyboardButtonPollType,
	WebAppInfo
)


class KeyboardButton(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#keyboardbutton

	"""
	__slots__ = (
		"text", "request_contact", "request_location",
		"request_poll", "web_app"
	)

	def __init__(
		self,
		text: str,
		request_contact: Optional[bool] = None,
		request_location: Optional[bool] = None,
		request_poll: Optional[KeyboardButtonPollType] = None,
		web_app: Optional[WebAppInfo] = None,

		**_kwargs: Any
	):
		self.text = text
		self.request_contact = request_contact
		self.request_location = request_location
		self.request_poll = request_poll
		self.web_app = web_app
