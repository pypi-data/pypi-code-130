#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Union,
	Optional,
	Any
)

from tgsdk import TelegramEntity


class Contact(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#contact

	"""
	__slots__ = ("phone_number", "first_name", "user_id", "last_name", "vcard")

	def __init__(
		self,
		phone_number: str,
		first_name: str,
		user_id: Optional[Union[str, int]] = None,
		last_name: Optional[str] = None,
		vcard: Optional[str] = None,

		**_kwargs: Any
	):
		self.phone_number = phone_number
		self.first_name = first_name
		self.user_id = user_id
		self.last_name = last_name
		self.vcard = vcard
