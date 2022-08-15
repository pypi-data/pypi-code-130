#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	TYPE_CHECKING,
	Optional,
	Union,
	Dict,
	Any
)

from tgsdk import TelegramEntity
from .photosize import PhotoSize

if TYPE_CHECKING:
	from tgsdk import (
		Bot,
		File
	)


class Video(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#video

	"""
	__slots__ = ("file_id", "file_unique_id", "width", "height", "duration", "thumb", "file_name", "file_type", "mime_type", "file_size", "bot")

	def __init__(
		self,
		file_id: str,
		file_unique_id: str,
		width: int,
		height: int,
		duration: int,
		thumb: Optional[PhotoSize] = None,
		file_name: Optional[str] = None,
		mime_type: Optional[str] = None,
		file_size: Optional[int] = None,

		bot: Optional["Bot"] = None,

		**_kwargs: Any
	):
		self.file_id = file_id
		self.file_unique_id = file_unique_id
		self.width = width
		self.height = height
		self.duration = duration
		self.thumb = thumb
		self.file_name = file_name
		self.mime_type = mime_type
		self.file_size = file_size

		self.bot = bot

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["Video", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["thumb"] = PhotoSize.de_json(data.get("thumb"))

		return cls(**data)

	def get_file(self, timeout: float = None, kwargs: Dict = None) -> "File":
		"""

		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.get_file(file_id=self.file_id, timeout=timeout, kwargs=kwargs)
