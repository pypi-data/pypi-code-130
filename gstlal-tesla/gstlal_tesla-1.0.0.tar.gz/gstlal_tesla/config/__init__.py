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


import itertools
import getpass
import os
import glob

import yaml

from lal import LIGOTimeGPS
from ligo.lw import utils as ligolw_utils
from ligo.lw.utils import segments as ligolw_segments
from ligo.segments import segment, segmentlist, segmentlistdict

from gstlal import segments
from gstlal.dags import profiles

import re


class Config:
	"""
	Hold configuration used for analyzes.
	"""
	def __init__(self, **kwargs):
		# normalize options
		kwargs = replace_keys(kwargs)

		# basic analysis options
		self.target_event = kwargs.get("event_id", "S190408an")
		self.rootdir = kwargs.get("analysis_dir", os.getcwd())
		self.generate_injections_version = kwargs.get("generate_injections_version", "ProdF1")
		self.injection_run_version = kwargs.get("injection_run_version", "ProdF1")
		self.reduced_bank_version = kwargs.get("reduced_bank_version", "ProdF1")
		self.search_run_version = kwargs.get("search_run_version", "ProdF1")
		self.rerank_version = kwargs.get("rerank_version", "ProdF1")
		self.tesla_dir = kwargs.get("tesla_dir", None)

		# get instrument combinations
		if isinstance(kwargs["instruments"], list):
			self.ifos = kwargs["instruments"]
		else:
			self.ifos = self.to_ifo_list(kwargs["instruments"])
		self.min_ifos = kwargs.get("min_instruments", 1)
		self.all_ifos = frozenset(self.ifos)
		
		self.ifo_combos = []
		for n_ifos in range(self.min_ifos, len(self.ifos) + 1):
			for combo in itertools.combinations(self.ifos, n_ifos):
				self.ifo_combos.append(frozenset(combo))

		# section-specific options
		if "generate_injections" in kwargs:
			self.generate_injections= dotdict(replace_keys(kwargs["generate_injections"][self.generate_injections_version]))
			self.generate_injections.backup_dir = self.generate_injections.get("backup_dir", self.rootdir + "generate_injection_" + self.generate_injections_version + "/")
			self.generate_injections.rundir = self.generate_injections.get("rundir", self.rootdir + "generate_injection_" + self.generate_injections_version + "/run/")
			self.generate_injections.split_num = self.generate_injections.get("split_num", 100)
			
			self.generate_injections.pe_samples = self.generate_injections.get("PE_samples", None)
			if self.tesla_dir is not None:
				try: 
					self.generate_injections.pe_samples = glob.glob(self.tesla_dir + "/resources/PE_samples/posterior_samples_" + self.target_event + ".csv")[0]
				except IndexError:
					self.generate_injections.pe_samples = None
			assert self.generate_injections.pe_samples != None, "Path to PE samples is None. Please check and correct your config file."

			self.generate_injections.split_num = self.generate_injections.get("split_num", 100)

		if "injection_run" in kwargs:
			self.injection_run = dotdict(replace_keys(kwargs["injection_run"][self.injection_run_version]))
			self.injection_run.backup_dir = self.injection_run.get("backup_dir", self.rootdir + "injection_run_" + self.injection_run_version + "/")
			self.injection_run.rundir = self.injection_run.get("rundir", self.rootdir + "injection_run_" + self.injection_run_version + "/run/")
			try:
				self.injection_run.lensed_injection_file = glob.glob(self.generate_injections.rundir + self.target_event + "_lensed_injections.xml.gz")[0]
			except IndexError:
				self.injection_run.lensed_injection_file = None

			# Initiate by-standing key
			self.injection_run.config_file = None
			self.injection_run.config_dict = None	
		
		if "generate_reduced_bank" in kwargs:
			self.generate_reduced_bank = dotdict(replace_keys(kwargs["generate_reduced_bank"][self.reduced_bank_version]))
			self.generate_reduced_bank.rundir = self.generate_reduced_bank.get("rundir", self.rootdir + "generate_reduced_bank_" + self.reduced_bank_version + "/")

		if "search_run" in kwargs:
			self.search_run = dotdict(replace_keys(kwargs["search_run"][self.search_run_version]))
			self.search_run.basedir = self.search_run.get("basedir", self.rootdir + "search_run_" + self.search_run_version + "/")
			
		if "rerank" in kwargs:
			self.rerank = dotdict(replace_keys(kwargs["rerank"][self.rerank_version]))
			self.rerank.rundir = self.rerank.get("rundir", self.rootdir + "rerank_" + self.rerank_version + "/")
			self.rerank.search_run_list = []
			# Get all the search run directories
			for version in self.rerank.search_run:
				search_run_basedir = self.rootdir + "search_run_" + version + "/"

				# Search for all the folders provided by the user.
				if self.rerank.search_run[version].folders:
					for folder in self.rerank.search_run[version].folders:
						try:
							self.rerank.search_run_list.append(glob.glob(search_run_basedir + "/" + folder)[0])
						except IndexError:
							if self.rerank.search_run[version].force:
								print("Folder {} not found. Skipping...".format(folder))
							else:
								raise IndexError("Folder {} not found. Please check.".format(folder))

				# If epoch and specific chunks are listed
				if self.rerank.search_run[version].epoch and self.rerank.search_run[version].chunks:
					for chunk in self.rerank.search_run[version].chunks:
						try:
							self.rerank.search_run_list.append(glob.glob(search_run_basedir + "/" + self.rerank.search_run[version].epoch + "_chunk" + str(chunk))[0])
						except IndexError:
							if self.rerank.search_run[version].force:
								print("Folder {} not found. Skipping...".format(self.rerank.search_run[version].epoch + "_chunk" + str(chunk)))
							else:
								raise IndexError("Folder {} not found. Please check.".format(self.rerank.search_run[version].epoch + "_chunk" + str(chunk)))

				# If epoch and start_chunk and end_chunk
				if self.rerank.search_run[version].epoch and self.rerank.search_run[version].start_chunk and self.rerank.search_run[version].end_chunk:
					for chunk in numpy.linspace(self.rerank.search_run[version].start_chunk, self.rerank.search_run[version].end_chunk, 1, dtype=int):
						try:
							self.rerank.search_run_list.append(glob.glob(search_run_basedir + "/" + self.rerank.search_run[version].epoch + "_chunk" + str(chunk))[0])
						except IndexError:
							if self.rerank.search_run[version].force:
								print("Folder {} not found. Skipping...".format(self.rerank.search_run[version].epoch + "_chunk" + str(chunk)))
							else:
								raise IndexError("Folder {} not found. Please check.".format(self.rerank.search_run[version].epoch + "_chunk" + str(chunk)))
				
				# Sort the list of search run directories
				self.rerank.search_run_list = sorted(self.rerank.search_run_list, key=lambda x : int(re.sub("[^0-9]", "",os.path.basename(x).split("_")[-1])))

		# condor options
		self.condor = dotdict(replace_keys(kwargs["condor"]))
		self.x509_proxy = kwargs.get("x509_proxy", None)

		# file transfer installed by default
		if self.condor.transfer_files is None:
			self.condor.transfer_files = True

		self.condor.submit = self.create_condor_submit_options(
			self.condor,
			x509_proxy=self.x509_proxy,
		)

		# validate config
		self.validate()

	def create_condor_submit_options(self, condor_config, x509_proxy=False):
		if "accounting_group_user" in condor_config:
			accounting_group_user = condor_config["accounting_group_user"]
		else:
			accounting_group_user = getpass.getuser()

		submit_opts = {
			"want_graceful_removal": "True",
			"kill_sig": "15",
			"accounting_group": condor_config["accounting_group"],
			"accounting_group_user": accounting_group_user,
		}
		requirements = []

		# load site profile
		profile = profiles.load_profile(condor_config["profile"])
		assert profile["scheduler"] == "condor", "only scheduler=condor is allowed currently"

		# add profile-specific options
		if "directives" in profile:
			submit_opts.update(profile["directives"])
		if "requirements" in profile:
			requirements.extend(profile["requirements"])

		# singularity-specific options
		if "singularity_image" in condor_config:
			singularity_image = condor_config["singularity_image"]
			requirements.append("(HAS_SINGULARITY=?=True)")
			submit_opts['+SingularityImage'] = f'"{singularity_image}"'
			submit_opts['transfer_executable'] = False
			submit_opts['getenv'] = False
			if x509_proxy:
				submit_opts['x509userproxy'] = x509_proxy
				submit_opts['use_x509userproxy'] = True
			if not self.condor.transfer_files:
				# set the job's working directory to be the same as the current
				# working directory to match the behavior of vanilla jobs
				if "environment" in submit_opts:
					env_opts = submit_opts["environment"].strip('"')
					submit_opts["environment"] = f'"{env_opts} SINGULARITY_PWD={self.rootdir}"'
				else:
					submit_opts["environment"] = f'"SINGULARITY_PWD={self.rootdir}"'
		else:
			submit_opts['getenv'] = True

		# add config-specific options
		if "directives" in condor_config:
			submit_opts.update(condor_config["directives"])
		if "requirements" in condor_config:
			requirements.extend(condor_config["requirements"])

		# condor requirements
		submit_opts['requirements'] = " && ".join(requirements)

		return submit_opts

	def validate(self):
		"""
		Validate configuration settings.
		"""
		pass

	@classmethod
	def load(cls, path):
		"""
		Load configuration from a file given a file path.
		"""
		with open(path, "r") as f:
			return cls(**yaml.safe_load(f))

	@staticmethod
	def to_ifo_list(ifos):
		return [ifos[2*n:2*n+2] for n in range(len(ifos) // 2)]

class dotdict(dict):
	"""
	A dictionary supporting dot notation.

	Implementation from https://gist.github.com/miku/dc6d06ed894bc23dfd5a364b7def5ed8.

	"""
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for k, v in self.items():
			if isinstance(v, dict):
				self[k] = dotdict(v)

def return_normal_dict(dotdict):
	final = {}
	for k, v in dotdict.items():
		if isinstance(v, dict):
			final[k] = return_normal_dict(v)
		else:
			final[k] = v
	return final

def replace_keys(dict_):
	out = dict(dict_)
	for k, v in out.items():
		if isinstance(v, dict):
			out[k] = replace_keys(v)
	return {k.replace("-", "_"): v for k, v in out.items()}
