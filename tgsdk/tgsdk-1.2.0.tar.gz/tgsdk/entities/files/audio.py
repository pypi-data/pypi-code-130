#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	TYPE_CHECKING,
	Optional,
	Dict,
	Union,
	Any
)

from tgsdk import PhotoSize
from tgsdk import TelegramEntity

if TYPE_CHECKING:
	from tgsdk import (
		Bot,
		File
	)


class Audio(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#audio

	"""
	__slots__ = ("file_id", "file_unique_id", "duration", "performer", "title", "file_name", "mime_type", "file_size", "thumb", "bot")

	def __init__(
		self,
		file_id: str,
		file_unique_id: str,
		duration: int,
		performer: Optional[str] = None,
		title: Optional[str] = None,
		file_name: Optional[str] = None,
		mime_type: Optional[str] = None,
		file_size: Optional[int] = None,
		thumb: Optional[PhotoSize] = None,

		bot: Optional["Bot"] = None,

		**_kwargs: Any
	):
		self.file_id = file_id
		self.file_unique_id = file_unique_id
		self.duration = duration
		self.performer = performer
		self.title = title
		self.file_name = file_name
		self.mime_type = mime_type
		self.file_size = file_size
		self.thumb = thumb
		self.bot = bot

	def get_file(self, timeout: float = None, kwargs: Dict = None) -> "File":
		"""

		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.get_file(file_id=self.file_id, timeout=timeout, kwargs=kwargs)

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["Audio", None]:
		if not data:
			return None

		data["thumb"] = PhotoSize.de_json(data.get("thumb"))

		return cls(**data)
