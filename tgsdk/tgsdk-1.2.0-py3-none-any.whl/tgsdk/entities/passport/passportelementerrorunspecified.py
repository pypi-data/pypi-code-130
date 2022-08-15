#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import Any

from tgsdk import PassportElementError


class PassportElementErrorUnspecified(PassportElementError):
	"""
	https://core.telegram.org/bots/api#passportelementerrorunspecified

	"""
	__slots__ = (
		"source", "type", "element_hash", "message"
	)

	def __init__(
		self,
		source: str,
		type: str,
		element_hash: str,
		message: str,

		**_kwargs: Any
	):
		self.source = source
		self.type = type
		self.element_hash = element_hash
		self.message = message
