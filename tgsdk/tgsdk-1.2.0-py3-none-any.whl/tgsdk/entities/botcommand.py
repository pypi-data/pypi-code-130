#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import Any

from tgsdk import TelegramEntity


class BotCommand(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#botcommand

	"""
	__slots__ = ("command", "description")

	def __init__(
		self,
		command: str,
		description: str,

		**_kwargs: Any
	):
		self.command = command
		self.description = description
