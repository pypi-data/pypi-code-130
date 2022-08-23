# Copyright (C) 2020  Patrick Godwin (patrick.godwin@ligo.org)
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import json
import os

from ligo.segments import segment

from gstlal.config import Config as BaseConfig
from gstlal.config import dotdict, replace_keys


class Config(BaseConfig):
	"""
	Hold configuration used for inspiral-specific analyzes.
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# section-specific options
		self.svd = dotdict(replace_keys(kwargs["svd"]))
		self.filter = dotdict(replace_keys(kwargs["filter"]))
		self.prior = dotdict(replace_keys(kwargs["prior"]))
		self.rank = dotdict(replace_keys(kwargs["rank"]))
		if "upload" in kwargs:
			self.upload = dotdict(replace_keys(kwargs["upload"]))
		if "pastro" in kwargs:
			self.pastro = dotdict(replace_keys(kwargs["pastro"]))
		if "metrics" in kwargs:
			self.metrics = dotdict(replace_keys(kwargs["metrics"]))
		if "services" in kwargs:
			self.services = dotdict(replace_keys(kwargs["services"]))
		if "summary" in kwargs:
			self.summary = dotdict(replace_keys(kwargs["summary"]))

		# set up analysis directories
		if not self.data.analysis_dir:
			self.data.analysis_dir = os.getcwd()
		if not self.data.rerank_dir:
			self.data.rerank_dir = self.data.analysis_dir

	def setup(self):
		"""
		Set up binning, load relevant analysis files.
		"""
		super().setup()

		# load manifest
		self.load_svd_manifest(self.svd.manifest)

		# calculate start pad for filtering
		max_duration = max(svd_bin["max_dur"] for svd_bin in self.svd.stats.bins.values())
		self.filter.start_pad = 16 * self.psd.fft_length + max_duration

		# create time bins
		if self.span != segment(0, 0):
			self.create_time_bins(start_pad=self.filter.start_pad)

	def load_svd_manifest(self, manifest_file):
		with open(manifest_file, "r") as f:
			svd_stats = dotdict(replace_keys(json.load(f)))

		# load default config for sub banks if available
		if "sub_banks" in self.svd:
			reduced_config = self.svd.copy()
			reduced_config.pop("sub_banks")
			for sub_bank, props in self.svd.sub_banks.items():
				self.svd.sub_banks[sub_bank] = dotdict(replace_keys({**reduced_config, **props}))

		# define svd bins, metadata
		self.svd.bins = svd_stats.bins.keys()
		self.svd.stats = svd_stats
