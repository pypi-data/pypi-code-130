#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Any
)

from tgsdk import TelegramEntity


# if TYPE_CHECKING:
# 	from tgsdk import Bot


class File(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#file

	"""

	__slots__ = ("file_id", "file_unique_id", "file_size", "file_path")

	def __init__(
		self,
		file_id: str,
		file_unique_id: str,
		file_size: Optional[int] = None,
		file_path: Optional[str] = None,
		# bot: "Bot" = None,

		**_kwargs: Any
	):
		self.file_id = file_id
		self.file_unique_id = file_unique_id
		self.file_size = file_size
		self.file_path = file_path
# self.bot = bot
