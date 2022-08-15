#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import Any

from tgsdk import PassportElementError


class PassportElementErrorDataField(PassportElementError):
	"""
	https://core.telegram.org/bots/api#passportelementerrordatafield

	"""
	__slots__ = (
		"source", "type", "field_name", "data_hash", "message"
	)

	def __init__(
		self,
		source: str,
		type: str,
		field_name: str,
		data_hash: str,
		message: str,

		**_kwargs: Any
	):
		self.source = source
		self.type = type
		self.field_name = field_name
		self.data_hash = data_hash
		self.message = message
