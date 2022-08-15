#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import Any

from tgsdk import TelegramEntity


class LabeledPrice(TelegramEntity):
	"""
	https://core.telegram.org/bots/api/#labeledprice

	"""

	__slots__ = ("label", "amount")

	def __init__(
		self,
		label: str,
		amount: int,

		**_kwargs: Any
	):
		self.label = label
		self.amount = amount
