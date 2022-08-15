#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Any,
	List,
	Optional
)

from tgsdk import TelegramEntity


class WebhookInfo(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#webhookinfo

	"""

	__slots__ = (
		"url", "has_custom_certificate", "pending_update_count", "ip_address",
		"last_error_date", "last_error_message", "last_synchronization_error_date", "max_connections", "allowed_updates"
	)

	def __init__(
		self,
		url: str,
		has_custom_certificate: bool,
		pending_update_count: int,
		ip_address: Optional[str] = None,
		last_error_date: Optional[int] = None,
		last_error_message: Optional[str] = None,
		last_synchronization_error_date: Optional[int] = None,
		max_connections: Optional[int] = None,
		allowed_updates: Optional[List[str]] = None,

		**_kwargs: Any
	):
		self.url = url
		self.has_custom_certificate = has_custom_certificate
		self.pending_update_count = pending_update_count

		self.ip_address = ip_address
		self.last_error_date = last_error_date
		self.last_error_message = last_error_message
		self.last_synchronization_error_date = last_synchronization_error_date
		self.max_connections = max_connections
		self.allowed_updates = allowed_updates

	def is_url_equal(self, url: str) -> bool:
		return self.url == url

	def is_domain_equal(self, domain: str) -> bool:
		return domain in self.url
