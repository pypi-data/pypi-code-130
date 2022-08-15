#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import Any

from tgsdk import PassportElementError


class PassportElementErrorFile(PassportElementError):
	"""
	https://core.telegram.org/bots/api#passportelementerrorfile

	"""
	__slots__ = (
		"source", "type", "file_hash", "message"
	)

	def __init__(
		self,
		source: str,
		type: str,
		file_hash: str,
		message: str,

		**_kwargs: Any
	):
		self.source = source
		self.type = type
		self.file_hash = file_hash
		self.message = message
