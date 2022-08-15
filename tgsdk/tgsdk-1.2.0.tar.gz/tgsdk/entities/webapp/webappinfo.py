#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import Any

from tgsdk import TelegramEntity


class WebAppInfo(TelegramEntity):
	__slots__ = (
		"url",
	)

	def __init__(
		self,
		url: str,

		**_kwargs: Any
	):
		self.url = url
		if not self.url:
			raise AttributeError("Menu button web app URL '' is invalid: URL host is empty")
