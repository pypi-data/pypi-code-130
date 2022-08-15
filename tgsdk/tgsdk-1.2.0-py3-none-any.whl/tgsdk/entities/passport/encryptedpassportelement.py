#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	Union,
	List,
	Any
)

from tgsdk import (
	PassportFile,
	TelegramEntity
)


class EncryptedPassportElement(TelegramEntity):
	__slots__ = ("type", "data", "phone_number", "email", "files", "front_side", "reverse_side", "selfie", "translation", "hash")

	def __init__(
		self,
		type: str,
		data: Optional[str] = None,
		phone_number: Optional[str] = None,
		email: Optional[str] = None,
		files: Optional[List[PassportFile]] = None,
		front_side: Optional[PassportFile] = None,
		reverse_side: Optional[PassportFile] = None,
		selfie: Optional[PassportFile] = None,
		translation: Optional[List[PassportFile]] = None,
		hash: Optional[str] = None,

		**_kwargs: Any
	):
		self.type = type
		self.data = data
		self.phone_number = phone_number
		self.email = email
		self.files = files
		self.front_side = front_side
		self.reverse_side = reverse_side
		self.selfie = selfie
		self.translation = translation
		self.hash = hash

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["EncryptedPassportElement", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["files"] = PassportFile.de_list(data.get("files"))
		data["front_side"] = PassportFile.de_json(data.get("front_side"))
		data["reverse_side"] = PassportFile.de_json(data.get("reverse_side"))
		data["selfie"] = PassportFile.de_json(data.get("selfie"))
		data["translation"] = PassportFile.de_list(data.get("translation"))

		return cls(**data)
