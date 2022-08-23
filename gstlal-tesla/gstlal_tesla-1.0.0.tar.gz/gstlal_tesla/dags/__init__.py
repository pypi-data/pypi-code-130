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


from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
import os
import re
from typing import List, Optional, Tuple, Union

import htcondor
from htcondor import dags
import pluggy

from gstlal import plugins


_PROTECTED_CONDOR_VARS = {"input", "output", "rootdir"}


class DAG(dags.DAG):
	_has_layers = False

	def __init__(self, config, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = config
		self._node_layers = {}
		self._layers = {}
		self._provides = {}

		# register layers to DAG if needed
		if not self._has_layers:
			for layer_name, layer in self._get_registered_layers().items():
				self.register_layer(layer_name)(layer)

	def attach(self, layer):
		key = layer.name
		if key in self._layers:
			return KeyError(f"{key} layer already added to DAG")
		self._layers[layer.name] = layer

		# determine parent-child relationships and connect accordingly
		all_edges = defaultdict(set)
		if layer.has_dependencies:
			# determine edges
			for child_idx, node in enumerate(layer.nodes):
				for input_ in node.requires:
					if input_ in self._provides:
						parent_name, parent_idx = self._provides[input_]
						all_edges[parent_name].add((parent_idx, child_idx))

			if not all_edges:
				self._node_layers[key] = self.layer(**layer.config())

			# determine edge type and connect
			for num, (parent, edges) in enumerate(all_edges.items()):
				edge = self._get_edge_type(parent, layer.name, all_edges[parent])
				if num == 0:
					self._node_layers[key] = self._node_layers[parent].child_layer(
						**layer.config(),
						edge=edge
					)
				else:
					self._node_layers[key].add_parents(self._node_layers[parent], edge=edge)

		else:
			self._node_layers[key] = self.layer(**layer.config())

		# register any data products the layer provides
		for idx, node in enumerate(layer.nodes):
			for output in node.provides:
				self._provides[output] = (key, idx)

	def create_log_dir(self, log_dir="logs"):
		os.makedirs(log_dir, exist_ok=True)

	def write_dag(self, filename, path=None, **kwargs):
		write_dag(self, dag_file_name=filename, dag_dir=path, **kwargs)

	def write_script(self, filename, path=None, formatter=None):
		if path:
			filename = os.path.join(path, filename)
		if not formatter:
			formatter = HexFormatter()

		# write script
		with open(filename, "w") as f:
			# traverse DAG in breadth-first order
			for layer in self.walk(dags.WalkOrder("BREADTH")):
				# grab relevant submit args, format $(arg) to {arg}
				executable = layer.submit_description['executable']
				args = layer.submit_description['arguments']
				args = re.sub(r"\$\(((\w+?))\)", r"{\1}", args)

				# evaluate vars for each node in layer, write to disk
				for idx, node_vars in enumerate(layer.vars):
					node_name = formatter.generate(layer.name, idx)
					print(f"# Job {node_name}", file=f)
					print(executable + " " + args.format(**node_vars) + "\n", file=f)

	@classmethod
	def register_layer(cls, layer_name):
		"""Register a layer to the DAG, making it callable.
		"""
		def register(func):
			def wrapped(self, *args, **kwargs):
				return func(self.config, self, *args, **kwargs)
			setattr(cls, layer_name, wrapped)
		return register

	def _get_edge_type(self, parent_name, child_name, edges):
		parent = self._layers[parent_name]
		child = self._layers[child_name]
		edges = sorted(list(edges))

		# check special cases, defaulting to explicit edge connections via indices
		if len(edges) == (len(parent.nodes) + len(child.nodes)):
			return dags.ManyToMany()

		elif (len(parent.nodes) == len(child.nodes)
				and all([parent_idx == child_idx for parent_idx, child_idx in edges])):
			return dags.OneToOne()

		else:
			return EdgeConnector(edges)

	@classmethod
	def _get_registered_layers(cls):
		"""Get all registered DAG layers.
		"""
		# set up plugin manager
		manager = pluggy.PluginManager("gstlal")
		manager.add_hookspecs(plugins)

		# load layers
		from gstlal.dags.layers import io, psd
		manager.register(io)
		manager.register(psd)

		# add all registered plugins to registry
		registered = {}
		for plugin_name in manager.hook.layers():
			for name, layer in plugin_name.items():
				registered[name] = layer

		return registered


class HexFormatter(dags.SimpleFormatter):
	"""A hex-based node formatter that produces names like LayerName_000C.

	"""
	def __init__(self, offset: int = 0):
		self.separator = "."
		self.index_format = "{:05X}"
		self.offset = offset

	def parse(self, node_name: str) -> Tuple[str, int]:
		layer, index = node_name.split(self.separator)
		index = int(index, 16)
		return layer, index - self.offset


class EdgeConnector(dags.BaseEdge):
	"""This edge connects individual nodes in layers given an explicit mapping.

	"""
	def __init__(self, indices):
		self.indices = indices

	def get_edges(self, parent, child, join_factory):
		for parent_idx, child_idx in self.indices:
			yield (parent_idx,), (child_idx,)


def write_dag(dag, dag_dir=None, formatter=None, **kwargs):
	if not formatter:
		formatter = HexFormatter()
	if not dag_dir:
		dag_dir = os.getcwd()
	return htcondor.dags.write_dag(dag, dag_dir, node_name_formatter=formatter, **kwargs)


@dataclass
class Argument:
	"""Defines a command-line argument (positional).

	This provides some extra functionality over defining command line
	argument explicitly, in addition to some extra parameters which
	sets how condor interprets how to handle them within the DAG
	and within submit descriptions.

	Parameters
	----------
	name
		The option name. Since this is a positional argument, it is not
		used explicitly in the command, but is needed to define
		variable names within jobs.
	argument
		The positional argument value(s) used in a command.
	track
		Whether to track files defined here and used externally within
		jobs to determine parent-child relationships when nodes specify
		this option as an input or output. On by default.
	remap
		Whether to allow remapping of output files being transferred.
		If set, output files will be moved to their target directories
		after files are transferred back. This is done to avoid issues
		where the target directories are available on the submit node
		but not on the exectute node. On by default.
	suppress
		Whether to hide this option. Used externally within jobs to
		determine whether to define job arguments. This is typically used
		when you want to track file I/O used by a job but isn't directly
		specified in their commands. Off by default.
	suppress_with_remap
		Same as suppress but allowing transfer remaps to still occur.
		Used when you want to track file output which is not directly
		specified in their command but whose file locations changed
		compared to their inputs. Off by default.

	Examples
	________
	>>> Argument("command", "run").vars()
	'run'

	>>> files = ["input_1.txt", "input_2.txt"]
	>>> Argument("input-files", files).vars()
	'input_1.txt input_2.txt'

	"""
	name: str
	argument: Union[int, float, str, List]
	track: Optional[bool] = True
	remap: Optional[bool] = True
	suppress: Optional[bool] = False
	suppress_with_remap: Optional[bool] = False

	def __post_init__(self):
		# check against list of protected condor names/characters,
		# rename condor variables name to avoid issues
		self.condor_name = self.name.replace("-", "_")
		if self.condor_name in _PROTECTED_CONDOR_VARS:
			self.condor_name += "_"

		if isinstance(self.argument, str) or not isinstance(self.argument, Iterable):
			self.argument = [self.argument]
		self.argument = [str(arg) for arg in self.argument]

		# set options that control other options
		if self.suppress:
			self.remap = False
		elif self.suppress_with_remap:
			self.suppress = True

	@property
	def arg_basename(self):
		return [os.path.basename(arg) for arg in self.argument]

	def vars(self, basename=False):
		if callable(basename):
			# if basename is a function, determine whether the argument's
			# basename should be used based on calling basename(argument)
			args = []
			for arg in self.argument:
				if basename(arg):
					args.append(os.path.basename(arg))
				else:
					args.append(arg)
			return " ".join(args)
		elif basename:
			return " ".join(self.arg_basename)
		else:
			return " ".join(self.argument)

	def files(self, basename=False):
		return ",".join(self.arg_basename) if basename else ",".join(self.argument)

	def remaps(self):
		return ";".join([f"{base}={arg}" for base, arg in zip(self.arg_basename, self.argument) if base != arg])


@dataclass
class Option:
	"""Defines a command-line option (long form).

	This provides some extra functionality over defining command line
	options explicitly, in addition to some extra parameters which
	sets how condor interprets how to handle them within the DAG
	and within submit descriptions.

	Parameters
	----------
	name
		The option name to be used in a command.
	argument
		The argument value(s) used in a command.
	track
		Whether to track files defined here and used externally within
		jobs to determine parent-child relationships when nodes specify
		this option as an input or output. On by default.
	remap
		Whether to allow remapping of output files being transferred.
		If set, output files will be moved to their target directories
		after files are transferred back. This is done to avoid issues
		where the target directories are available on the submit node
		but not on the exectute node. On by default.
	suppress
		Whether to hide this option. Used externally within jobs to
		determine whether to define job arguments. This is typically used
		when you want to track file I/O used by a job but isn't directly
		specified in their commands. Off by default.
	suppress_with_remap
		Same as suppress but allowing transfer remaps to still occur.
		Used when you want to track file output which is not directly
		specified in their command but whose file locations changed
		compared to their inputs. Off by default.

	Examples
	________
	>>> Option("verbose").vars()
	'--verbose'

	>>> Option("input-type", "file").vars()
	'--input-type file'

	>>> Option("ifos", ["H1", "L1", "V1"]).vars()
	'--ifos H1 --ifos L1 --ifos V1'

	"""
	name: str
	argument: Optional[Union[int, float, str, List]] = None
	track: Optional[bool] = True
	remap: Optional[bool] = True
	suppress: Optional[bool] = False
	suppress_with_remap: Optional[bool] = False

	def __post_init__(self):
		# check against list of protected condor names/characters,
		# rename condor variables name to avoid issues
		self.condor_name = self.name.replace("-", "_")
		if self.condor_name in _PROTECTED_CONDOR_VARS:
			self.condor_name += "_"

		if self.argument is not None:
			if isinstance(self.argument, str) or not isinstance(self.argument, Iterable):
				self.argument = [self.argument]
			self.argument = [str(arg) for arg in self.argument]

		# set options that control other options
		if self.suppress:
			self.remap = False
		elif self.suppress_with_remap:
			self.suppress = True

	@property
	def arg_basename(self):
		return [os.path.basename(arg) for arg in self.argument]

	def vars(self, basename=False):
		if self.argument is None:
			return f"--{self.name}"
		elif callable(basename):
			# if basename is a function, determine whether the argument's
			# basename should be used based on calling basename(argument)
			args = []
			for arg in self.argument:
				if basename(arg):
					args.append(f"--{self.name} {os.path.basename(arg)}")
				else:
					args.append(f"--{self.name} {arg}")
			return " ".join(args)
		elif basename:
			return " ".join([f"--{self.name} {arg}" for arg in self.arg_basename])
		else:
			return " ".join([f"--{self.name} {arg}" for arg in self.argument])

	def files(self, basename=False):
		return ",".join(self.arg_basename) if basename else ",".join(self.argument)

	def remaps(self):
		return ";".join([f"{base}={arg}" for base, arg in zip(self.arg_basename, self.argument) if base != arg])
