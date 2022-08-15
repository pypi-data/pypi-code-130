#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Any
)

from .replymarkup import ReplyMarkup


class ReplyKeyboardRemove(ReplyMarkup):
	__slots__ = ("remove_keyboard", "selective")

	def __init__(
		self,
		selective: Optional[bool] = False,

		**_kwargs: Any
	):
		self.remove_keyboard = True

		self.selective = selective
