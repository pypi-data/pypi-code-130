#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import Any

from tgsdk import TelegramEntity


class WebAppData(TelegramEntity):
	__slots__ = (
		"data", "button_text"
	)

	def __init__(
		self,
		data: str,
		button_text: str,

		**_kwargs: Any
	):
		self.data = data
		self.button_text = button_text
