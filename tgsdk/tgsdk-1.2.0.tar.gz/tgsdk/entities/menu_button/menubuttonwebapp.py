#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Any
)

from tgsdk import (
	MenuButton,
	WebAppInfo
)


class MenuButtonWebApp(MenuButton):
	"""
	https://core.telegram.org/bots/api#menubuttonwebapp

	"""
	__slots__ = (
		"type", "text", "web_app"
	)

	def __init__(
		self,
		text: str,
		web_app: WebAppInfo,
		type: Optional[str] = "web_app",

		**_kwargs: Any
	):
		self.type = type
		self.text = text
		self.web_app = web_app
