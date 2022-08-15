#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	Union,
	Any
)

from tgsdk import TelegramEntity
from .location import Location


class Venue(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#venue

	"""
	__slots__ = ("location", "title", "address", "foursquare_id", "foursquare_type", "google_place_id", "google_place_type")

	def __init__(
		self,
		location: Location,
		title: str,
		address: str,
		foursquare_id: Optional[str] = None,
		foursquare_type: Optional[str] = None,
		google_place_id: Optional[str] = None,
		google_place_type: Optional[str] = None,

		**_kwargs: Any
	):
		self.location = location
		self.title = title
		self.address = address
		self.foursquare_id = foursquare_id
		self.foursquare_type = foursquare_type
		self.google_place_id = google_place_id
		self.google_place_type = google_place_type

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["Venue", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["location"] = Location.de_json(data.get("location"))

		return cls(**data)
