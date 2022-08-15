#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	Union,
	Any
)

from tgsdk import (
	ShippingAddress,
	TelegramEntity
)


class OrderInfo(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#orderinfo

	"""

	__slots__ = ("name", "phone_number", "email", "shipping_address")

	def __init__(
		self,
		name: Optional[str] = None,
		phone_number: Optional[str] = None,
		email: Optional[str] = None,
		shipping_address: Optional[ShippingAddress] = None,

		**_kwargs: Any
	):
		self.name = name
		self.phone_number = phone_number
		self.email = email
		self.shipping_address = shipping_address

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["OrderInfo", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["shipping_address"] = ShippingAddress.de_json(data.get("shipping_address"))

		return cls(**data)
