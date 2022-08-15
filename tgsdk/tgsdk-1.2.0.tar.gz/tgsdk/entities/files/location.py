#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Any
)

from tgsdk import TelegramEntity


class Location(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#location

	"""
	__slots__ = ("latitude", "longitude", "horizontal_accuracy", "live_period", "heading", "proximity_alert_radius")

	def __init__(
		self,
		latitude: float,
		longitude: float,
		horizontal_accuracy: Optional[float] = None,
		live_period: Optional[int] = None,
		heading: Optional[int] = None,
		proximity_alert_radius: Optional[int] = None,

		**_kwargs: Any
	):
		self.latitude = float(latitude)
		self.longitude = float(longitude)
		self.horizontal_accuracy = float(horizontal_accuracy) if horizontal_accuracy else None
		self.live_period = int(live_period) if live_period else None
		self.heading = int(heading) if heading else None
		self.proximity_alert_radius = int(proximity_alert_radius) if proximity_alert_radius else None
