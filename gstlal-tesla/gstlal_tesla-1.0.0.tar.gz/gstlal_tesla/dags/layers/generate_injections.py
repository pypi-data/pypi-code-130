#!/usr/bin/env python3
#
# Copyright (C) 2022  Alvin Li (kli7@caltech.edu), Juno Chan (clchan@link.cuhk.edu.hk)
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


from collections.abc import Mapping
import itertools
import os
from typing import Iterable

import numpy

from lal import rate
from lal.utils import CacheEntry
from ligo.segments import segment

from gstlal import plugins
from gstlal.datafind import DataType, DataCache
from gstlal.dags import Argument, Option
from gstlal.dags import util as dagutil
from gstlal.dags.layers import Layer, Node


DEFAULT_SPLIT_INJECTION_TIME = 20000
DEFAULT_MAX_FILES = 500

def generate_raw_injections_layer(config, dag):
	layer = Layer(
		executable="/usr/bin/lalapps_inspinj",
		name="lalapps_inspinj",
		requirements={
			"request_cpus": 1,
			"request_memory": 4000,
			"request_disk": "2GB",
			**config.condor.submit
		},
		transfer_files=config.condor.transfer_files,
	)

	arguments = [
			Option("gps-start-time", config.generate_injections.start_time),
			Option("gps-end-time", config.generate_injections.end_time),
			Option("enable-spin"),
			Option("aligned"),
			Option("i-distr", "uniform"),
			Option("l-distr", "random"),
			Option("t-distr", "uniform"),
			Option("dchirp-distr", "uniform"),
			Option("min-distance", 10000),
			Option("max-distance", 400000),
			Option("time-step", 32),
			Option("time-interval", 1),
			Option("taper-injection", "startend"),
		]

	default_settings = {
			"bns":
				{
				"min-mass1": 1.0,
				"max-mass1": 3.0,
				"min-mass2": 1.0,
				"max-mass2": 3.0,
				"min-spin1": 0,
				"max-spin1": 0.05,
				"min-spin2": 0,
				"max-spin2": 0.05,
				"m-distr": "componentMass",
				"waveform": "SpinTaylorT4threePointFivePN",
				"f-lower": 14.0,
				},
			"bbh":
				{
				"min-mass1": 5.0,
				"max-mass1": 50.0,
				"min-mass2": 5.0,
				"max-mass2": 50.0,
				"min-spin1": 0,
				"max-spin1": 0.99,
				"min-spin2": 0,
				"max-spin2": 0.99,
				"m-distr": "componentMass",
				"waveform": "SEOBNRv4pseudoFourPN",
				"f-lower": 14.0,
				},
			"imbh":
				{
				"min-mass1": 1.0,
				"max-mass1": 300.0,
				"min-mass2": 1.0,
				"max-mass2": 300.0,
				"min-spin1": 0,
				"max-spin1": 0.99,
				"min-spin2": 0,
				"max-spin2": 0.99,
				"m-distr": "componentMass",
				"waveform": "IMRPhenomDpseudoFourPN",
				"f-lower": 9.0,
				},
			}

	# Add injection type specific options
	for key in default_settings['bns']:
		if getattr(config.generate_injections,key) is None:
			arguments.append(Option(key, default_settings[config.generate_injections.injection_type][key]))
		else:
			arguments.append(Option(key, getattr(config.generate_injections,key)))
	
	layer += Node(
		arguments = arguments,
		outputs = [
			Option("output", config.generate_injections.rundir + "/" + config.generate_injections.injection_type + "_ilwd.xml"),
		],
	)

	dag.attach(layer)

	return config.generate_injections.rundir + "/" + config.generate_injections.injection_type + "_ilwd.xml"	

def ligolw_no_ilwdchar_layer(config, dag, raw_injection):
	layer = Layer(
		"ligolw_no_ilwdchar",
		requirements={
			"request_cpus": 1,
			"request_memory": 4000,
			"request_disk": "2GB",
			**config.condor.submit
		},
		transfer_files=config.condor.transfer_files,
	)

	layer += Node(
		inputs = [
			Argument("input", raw_injection),
		],
		outputs = [
			Option("output", config.generate_injections.rundir + "/" + config.generate_injections.injection_type + "no_ilwd.xml", suppress=True),
			],
	)

	dag.attach(layer)

	return raw_injection


def gstlal_injsplitter_layer(config, dag, raw_injection):
	layer = Layer(
		"gstlal_injsplitter",
		requirements={
			"request_cpus": 1,
			"request_memory": 4000,
			"request_disk": "2GB",
			**config.condor.submit
		},
		transfer_files=config.condor.transfer_files,
	)

	arguments = [
			Option("output-path", config.generate_injections.rundir + "/split_injections"),
			Option("nsplit", config.generate_injections.split_num),
		]

	
	# Dummy for storing injection files	
	split_injection_cache = DataCache.generate(
			DataType.INJECTIONS,
			config.ifo_combos,
			)

	list_of_split_injections = [config.generate_injections.rundir + "/split_injections/H1K1L1V1-%04d_GSTLAL_SPLIT_INJECTIONS_INJSPLITTER-0-0.xml"%num for num in range(config.generate_injections.split_num)]

	layer += Node(
		arguments = arguments,
		inputs = [
			Argument("injections", raw_injection),
			Argument("injections-ghost", config.generate_injections.rundir + "/" + config.generate_injections.injection_type + "no_ilwd.xml", suppress = True),
		],
		outputs = [Option("split-injection-%s"%num, split_injection, suppress=True) for num, split_injection in enumerate(list_of_split_injections)],
	)

	dag.attach(layer)

	return list_of_split_injections

def tesla_generate_and_replace_injections_layer(config, dag, list_of_split_injections):
	layer = Layer(
		"tesla_generate_and_replace_injections",
		requirements={
			"request_cpus": 1,
			"request_memory": 4000,
			"request_disk": "2GB",
			**config.condor.submit
		},
		transfer_files=config.condor.transfer_files,
	)

	arguments = [
			Option("pe-samples", config.generate_injections.pe_samples),
		]

	list_of_lensed_injections = []
	
	# Add nodes for all split injections:
	for num, split_injection in enumerate(list_of_split_injections):
		arguments = [
			Option("pe-samples", config.generate_injections.pe_samples),
		]
	
		output_filename = config.generate_injections.rundir + "/tesla_generate_and_replace_injections/" + config.target_event + "_lensed_injections_%04d"%num
		list_of_lensed_injections.append(output_filename + ".xml.gz")

		layer += Node(
			arguments = arguments,
			inputs = [
				Option("injection-file", split_injection),
			],
			outputs = [
				Option("o", output_filename),
				Argument("output_file", output_filename + ".xml.gz", suppress = True),
			],
		)
	
	dag.attach(layer)
	return list_of_lensed_injections

def ligolw_add_layer(config, dag, list_of_lensed_injections):
	layer = Layer(
		"ligolw_add",
		requirements={
			"request_cpus": 1,
			"request_memory": 4000,
			"request_disk": "2GB",
			**config.condor.submit
		},
		transfer_files=config.condor.transfer_files,
	)
	
	layer += Node(
			arguments = [
				Option("output", config.generate_injections.rundir + "/" + config.target_event + "_lensed_injections.xml.gz"),
			],
			inputs = [
				Argument("lensed_injection_files", list_of_lensed_injections)
			],
		)
	
	dag.attach(layer)
	return True


@plugins.register
def layers():
	return {
		"generate_raw_injections": generate_raw_injections_layer,
		"ligolw_no_ilwdchar": ligolw_no_ilwdchar_layer,
		"gstlal_injsplitter": gstlal_injsplitter_layer,
		"tesla_generate_and_replace_injections": tesla_generate_and_replace_injections_layer,
		"ligolw_add": ligolw_add_layer,
	}
