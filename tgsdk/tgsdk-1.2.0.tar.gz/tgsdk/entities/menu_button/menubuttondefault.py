#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Any
)

from tgsdk import MenuButton


class MenuButtonDefault(MenuButton):
	"""
	https://core.telegram.org/bots/api#menubuttondefault

	"""
	__slots__ = (
		"type",
	)

	def __init__(
		self,
		type: Optional[str] = "default",

		**_kwargs: Any
	):
		self.type = type
