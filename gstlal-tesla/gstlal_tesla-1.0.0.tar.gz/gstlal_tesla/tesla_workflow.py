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


import argparse
import os
import shutil
import sys
import yaml
from optparse import OptionGroup, OptionParser
from gstlal_tesla.config import Config
from gstlal_tesla import config as Config_utils
from gstlal_tesla.dags.generate_injections import DAG
import glob
import json
import ruamel.yaml
import subprocess

# set up command line options
def parse_command_line():
	parser = OptionParser(
		description = "Tesla script to generate injections"
	)

	group = OptionGroup(parser, "Task options", "Determine which TESLA task to perform.")
	group.add_option("--generate-injections", action="store_true", default=False, help = "Step 1: Generate lensed injections based on posterior samples of a given superthreshold event.")
	group.add_option("--injection-run", action="store_true", default=False, help = "Step 2: Generate a gstal-config file for running the injection campaign.")
	group.add_option("--generate_reduced_template_bank", action="store_true", default=False, help = "Step 3: Generate the reduced template bank.")
	group.add_option("--search-run", action="store_true", default=False, help = "Step 4: Search run.")
	group.add_option("--rerank", action="store_true", default=False, help = "Step 5: Rerank.")
	parser.add_option_group(group)

	group = OptionGroup(parser, "Datasource Options", "Various data source options.")
	group.add_option("-c", "--config", help = "Sets the path to read the configuration file from.")
	group.add_option("-v", "--verbose", help = "Be verbose.")
	parser.add_option_group(group)

	options, filenames = parser.parse_args()

	return options, filenames

options, filenames = parse_command_line()


############################################
#
# Step 1 : Generate lensed injections
#
############################################

if options.generate_injections:
	
	# Load configuration file
	config = Config.load(options.config)
	
	# Generate basic dag
	dag = DAG(config)
	dag.create_log_dir(log_dir=config.generate_injections.rundir + "/logs")

	# Create necessary folders
	if not os.path.exists(config.generate_injections.rundir + "/split_injections/"):
		os.makedirs(config.generate_injections.rundir + "/split_injections/")

	if not os.path.exists(config.generate_injections.rundir + "/tesla_generate_and_replace_injections/"):
		os.makedirs(config.generate_injections.rundir + "/tesla_generate_and_replace_injections/")

	# Generate dag
	raw_injections = dag.generate_raw_injections()
	raw_injections_no_ilwd = dag.ligolw_no_ilwdchar(raw_injections)
	list_of_split_injections = dag.gstlal_injsplitter(raw_injections_no_ilwd)
	list_of_lensed_injections = dag.tesla_generate_and_replace_injections(list_of_split_injections)
	final = dag.ligolw_add(list_of_lensed_injections)

	assert final == True, "Failed to generate dag."

	# write dag/script to disk
	dag_name = f"tesla_generate_lensed_injections_dag"
	dag.write_dag(f"{dag_name}.dag", path=config.generate_injections.rundir)
	dag.write_script(f"{dag_name}.sh", path=config.generate_injections.rundir)


####################################################
#
# Step 2 : Generate injection campaign config file
#
####################################################

def write_config(yaml_dict, output_file="injection_run.config"):
	f = open(output_file, 'w')
	for heading in yaml_dict:
		f.write("##-------------------------------\n")
		f.write("# {}\n\n".format(heading.replace("_"," ")))
		yaml.dump(Config_utils.return_normal_dict(yaml_dict[heading]), f, default_flow_style=False)
		f.write("\n")
	f.close()

if options.injection_run:
		
	# Load configuration file
	config = Config.load(options.config)
	
	if options.verbose:
		print("Now generating GstLAL configuration file for injection campaign version %s..."%config.injection_run_version)

	# Create necessary folders
	if not os.path.exists(config.injection_run.backup_dir):
		os.makedirs(config.injection_run.backup_dir)

	if not os.path.exists(config.injection_run.rundir):
		os.makedirs(config.injection_run.rundir)

	# Copy over the injection file
	assert config.injection_run.lensed_injection_file != None, "Cannot find lensed injection file. Please check."
	os.system('cp {} {}'.format(config.injection_run.lensed_injection_file, config.injection_run.backup_dir))
		
	# Load injection run config file
	if "config" in config.injection_run.keys():
		config.injection_run.config_file = None
		config.injection_run.config_dict = config.injection_run.config
		config.injection_run.config_dict.filtering_options.filter.injections['lensed'] = Config_utils.dotdict({"file": os.path.basename(config.injection_run.lensed_injection_file), "range": "0:1000"})
		print("Warning: This is a manual configuration file. Make sure the banks, mass-model, and inspiral_dtdphi_pdf are present.")

	elif "default_config" in config.injection_run.keys():
		if config.injection_run.default_config.pipeline and config.injection_run.default_config.epoch:
			try:
				config.injection_run.config_file = glob.glob(config.tesla_dir + "/resources/" + config.injection_run.default_config.pipeline + "_resources/" + config.injection_run.default_config.epoch + "/default_setting.yml")[0]
			except:
				config.injection_run.config_file = glob.glob(config.tesla_dir + "/resources/" + config.injection_run.default_config.pipeline + "_resources/default/default_setting.yml")[0]
			config.injection_run.config_dict = Config_utils.dotdict(Config_utils.replace_keys(yaml.safe_load(open(config.injection_run.config_file))))
		
		config.injection_run.config_dict.general_options.instruments = config.ifos
		config.injection_run.config_dict.general_options.min_instruments = config.min_ifos

		# Copy over the banks, mass-model and inspiral_dtdphi files first
		os.system('cp -r {} {}'.format(os.path.dirname(config.injection_run.config_file) + "/{bank,mass_model,inspiral_dtdphi_pdf}", config.injection_run.backup_dir))

		# Update config dict if modify-config is present:
		if config.injection_run.default_config.injection_only:
			assert "analysis_dir" in config.injection_run.default_config.keys(), "Please provide the full analysis directory for the injection-only run."
			assert config.injection_run.default_config.analysis_dir != None, "Please provide the full analysis directory for the injection-only run."
			config.injection_run.config_dict.data_product_options.data.analysis_dir = config.injection_run.default_config.analysis_dir

		# Update the search times
		if config.injection_run.start_time and config.injection_run.end_time:
			config.injection_run.config_dict.general_options.start = config.injection_run.start_time
			config.injection_run.config_dict.general_options.stop = config.injection_run.stop_time
		elif config.injection_run.epoch and config.injection_run.chunk:
			try:
				time_data = yaml.safe_load(open(config.tesla_dir + "/resources/chunk_times.yml"))
			except FileNotFoundError:
				raise FileNotFoundError("TESLA is mising an important resouce file. Please check.")
			else:
				config.injection_run.config_dict.general_options.start = time_data[config.injection_run.epoch]["chunk%s"%config.injection_run.chunk]['start']
				config.injection_run.config_dict.general_options.stop = time_data[config.injection_run.epoch]["chunk%s"%config.injection_run.chunk]['end']
		
		if config.injection_run.modify_config:
			# Update the data-product-options
			if config.injection_run.modify_config.data_product_options:
				try: 
					config.injection_run.modify_config.data_product_options.data.template_bank
				except AttributeError:
					print("Nothing to replace for data product options. For future reference please leave data-product-options empty.")
				else:
					if config.injection_run.modify_config.data_product_options.data.template_bank.drop:
						for bank in config.injection_run.modify_config.data_product_options.data.template_bank.drop:
							config.injection_run.config_dict.data_product_options.data.template_bank.pop(bank, None)
							config.injection_run.config_dict.svd_bank_options.svd.sub_banks.pop(bank, None)
							try:
								config.injection_run.config_dict.prior_options.prior.dtdphi.pop(bank, None)
							except AttributeError:
								print("No inspiral dtdphi_files are present in the default config.")

						switch = True
						if config.injection_run.modify_config.data_product_options.data.template_bank.add:
							for bank in config.injection_run.modify_config.data_product_options.data.template_bank.add:
								os.system('cp {} {}'.format(config.injection_run.modify_config.data_product_options.data.template_bank.add[bank], config.injection_run.backup_dir + "/bank"))
								config.injection_run.config_dict.data_product_options.data.template_bank.replace({bank: "banks/" + os.path.dirname(config.injection_run.modify_config.data_product_options.data.template_bank.add[bank])})
						
								# Add new sub-bank information
								sub_bank_dict = config.injection_run.modify_config.svd_bank_options.svd.sub_banks.add[bank]
								assert sub_bank_dict != None, "You must provide the sub-bank svd info for the new bank."
								config.injection_run.config_dict.svd_bank_options.svd.sub_banks[bank] = Config_utils.dotdict(sub_bank_dict)

								# Add new mass model information
								if switch:
									mass_model_file = config.injection_run.modify_config.prior_options.prior.mass_model
									assert mass_model_file != None, "You must provide a new mass model file since you have replaced the template bank!"
									os.system('cp {} {}'.format(mass_model_file, config.injection_run.backup_dir + "/mass_model"))
									config.injection_run.config_dict.prior_options.prior.mass_model = "mass_model/" + os.path.basename(mass_model_file)

			# Update the data-source-options
			if config.injection_run.modify_config.data_source_options:
				if config.injection_run.modify_config.data_source_options.source.replace:
					for key in dict(config.injection_run.modify_config.data_source_options.source.replace).keys():
						config.injection_run.config_dict.data_source_options.source[key] = Config_utils.dotdict(config.injection_run.modify_config.data_source_options.source.replace[key])
					
				if config.injection_run.modify_config.data_source_options.source.add:
					for key in config.injection_run.modify_config.data_source_options.source.add.keys():
						config.injection_run.config_dict.data_source_options.source[key] = config.injection_run.modify_config.data_source_options.source.add[key]
						if key == "frame_cache":
							config.injection_run.config_dict.data_source_options.source.pop("data_find_server", None)

			# Replace the segments-options by an empty dict unless specified
			if config.injection_run.modify_config.segments_options:
				config.injection_run.config_dict.segments_options = Config_utils.dotdict(config.injection_run.modify_config.segments_options)
			else:
				config.injection_run.config_dict.segments_options = Config_utils.dotdict({"segments" : {"backend": None, "vetoes": {"category" : None}}})

			# Update the psd-options:
			if config.injection_run.modify_config.psd_options:
				if config.injection_run.modify_config.psd_options.replace:
					for key in config.injection_run.modify_config.psd_options.replace:
						config.injection_run.config_dict.psd_options.psd[key] = config.injection_run.modify_config.psd_options.replace[key]
				
			# Update the filtering-options:
			if config.injection_run.modify_config.filtering_options:
				# First add in the lensed injections
				config.injection_run.config_dict.filtering_options.filter.injections['lensed'] = Config_utils.dotdict({"file": os.path.basename(config.injection_run.lensed_injection_file), "range": "0:1000"})
				
				# Then add in otehr injections:
				for key in config.injection_run.modify_config.filtering_options.filter.injections:
					if key != "lensed":
						config.injection_run.config_dict.filtering_options.filter.injections[key] = Config_utils.dotdict(config.injection_run.modify_config.injection_options.filter.injetions[key])

			# Add in injection-options if present
			if config.injection_run.modify_config.injection_options:
				if config.injection_run.modify_config.injection_options.include_extra_injections:
					config.injection_run.config_dict.injection_options['injections'] = Config_utils.dotdict(config.injection_run.modify_config.injection_options.injections)
				else:
					config.injection_run.config_dict.pop("injection_options", None)
			else:
				config.injection_run.config_dict.pop("injection_options", None)

			# Update prior-options
			if config.injection_run.modify_config.prior_options:
				if config.injection_run.modify_config.prior_options.prior.dtdphi:
					if config.injection_run.modify_config.prior_options.prior.dtdphi.add:
						for key in config.injection_run.modify_config.prior_options.prior.dtdphi.add:
							temp_dict = Config_utils.return_to_normal_dict(config.injection_run.config_dict.prior_options.prior)
							dtdphi_file = config.injection_run.modify_config.prior_options.prior.dtdphi.add[key]
							if not os.path.exists(config.injection_run.backup_dir + "/inspiral_dtdphi_pdf/" + key):
								os.makedirs(config.injection_run.backup_dir + "/inspiral_dtdphi_pdf/" + key)
								os.system('cp {} {}'.format(dtdphi_file, config.injection_run.backup_dir + "/inspiral_dtdphi_pdf/" + key + "/"))
							if "dtdphi" not in temp_dict.keys():
								temp_dict['dtdphi'] = {}
							temp_dict['dtdphi'][key] = "inspiral_dtdphi_pdf/" + key + "/" + os.path.basename(dtdphi_file)
							config.injection_run.config_dict.prior_options.prior = Config_utils.dotdict(temp_dict)
			
			# Update ranking-options
			if config.injection_run.modify_config.ranking_options:
				if config.injection_run.modify_config.ranking_options.rank.ranking_stat_samples:
					config.injection_run.config_dict.ranking_options.rank.ranking_stat_samples = config.injection_run.modify_config.ranking_options.rank.ranking_stat_samples

			# Update summary options
			if config.injection_run.modify_config.summary_options:
				assert config.injection_run.modify_config.summary_options.summary.webdir != None, "You must input a valid webdir"
				config.injection_run.config_dict.summary_options.summary.webdir = config.injection_run.modify_config.summary_options.summary.webdir
			
			# Update condor-options
			config.injection_run.config_dict.condor_options.condor = Config_utils.dotdict({"accounting_group" : config.condor.accounting_group,
												"profile" : config.condor.profile,
												"singularity_image": config.condor.singularity_image,
												"accounting_group_user": config.condor.submit['accounting_group_user'],
												})

	write_config(config.injection_run.config_dict, output_file=config.injection_run.backup_dir + "/injection_run_" + config.injection_run_version + ".yml")


####################################################
#
# Step 3 : Generate reduced template bank
#
####################################################

if options.generate_reduced_template_bank:
		
	# Load configuration file
	config = Config.load(options.config)

	# First do sanity checks: Have the injection run been completed?
	try:
		database = glob.glob(config.injection_run.rundir + "/rank/triggers/*/*ALL*sqlite")[0]
	except IndexError:
		raise IndexError("Cannot find injection database from injection run. Please confirm if the run has completed.") from None
	
	# Create necessary folders
	if not os.path.exists(config.generate_reduced_bank.rundir):
		os.makedirs(config.generate_reduced_bank.rundir)

	os.system('cp {} {}'.format(database, config.generate_reduced_bank.rundir))

	if not os.path.exists(config.generate_reduced_bank.rundir + "/sub-banks"):
		os.makedirs(config.generate_reduced_bank.rundir + "/sub-banks")

	import gstlal.config.inspiral
	inspiral_config = gstlal.config.inspiral.Config.load(config.injection_run.rundir + "/injection_run_" + config.injection_run_version + ".yml")

	for index, bank in enumerate(list(inspiral_config.data.template_bank.keys())):
		os.system("tesla_generate_reduced_bank --database {} --bank {} --output {}".format(config.generate_reduced_bank.rundir + "/" + os.path.basename(database), config.injection_run.rundir + "/" + inspiral_config.data.template_bank[bank], config.generate_reduced_bank.rundir + "/sub-banks/" + "lensed_bank_%s.xml.gz"%index))

	# Combine files to get final lensed bank
	banks = glob.glob(config.generate_reduced_bank.rundir + "/sub-banks/" + "lensed_bank*.xml.gz")

	task = "ligolw_add "

	for bank in banks:
		task += bank + " "

	task += "--output {}_lensed_bank.xml.gz".format(config.generate_reduced_bank.rundir + "/" + config.target_event)

	os.system(task)


####################################################
#
# Step 4 : Search Runs
#
####################################################

if options.search_run:

	# Load configuration file
	config = Config.load(options.config)

	if not os.path.exists(config.search_run.basedir):
		os.makedirs(config.search_run.basedir)

	sample_config = yaml.safe_load(open(config.injection_run.rundir + "/injection_run_" + config.injection_run_version + ".yml"))
	config_dict = {}
	config_dict['general_options'] = {}
	for key in ["instruments", "min_instruments", "start", "stop"]:
		config_dict['general_options'][key] = sample_config[key]

	config_dict["data_product_options"] = {}
	config_dict["data_product_options"]["data"] = sample_config["data"]

	config_dict["data_source_options"] = {}
	config_dict["data_source_options"]["source"] = sample_config["source"]

	config_dict["segments_options"] = {}
	config_dict["segments_options"]["segments"] = sample_config["segments"]

	config_dict["psd_options"] = {}
	config_dict["psd_options"]['psd'] = sample_config["psd"]

	config_dict["svd_bank_options"] = {}
	config_dict["svd_bank_options"]["svd"] = sample_config["svd"]

	config_dict["filtering_options"] = {}
	config_dict["filtering_options"]["filter"] = sample_config["filter"]

	config_dict["prior_options"] = {}
	config_dict["prior_options"]["prior"] = sample_config["prior"]

	config_dict["ranking_options"] = {}
	config_dict["ranking_options"]["rank"] = sample_config["rank"]

	config_dict['summary_options'] = {}
	config_dict['summary_options']['summary'] = sample_config['summary']

	config_dict['condor_options'] = {}
	config_dict['condor_options']['condor'] = sample_config['condor']

	config_dict = Config_utils.dotdict(config_dict)
	
	banks = list(config_dict.data_product_options.data.template_bank.keys())
	drop_bank = []
	keep_bank = []
	for bank in banks:
		if "bbh" not in bank:
			drop_bank.append(bank)
			config_dict.data_product_options.data.template_bank.pop(bank, None)
			config_dict.svd_bank_options.svd.sub_banks.pop(bank, None)
			if config_dict.prior_options.prior.dtdphi:
				config_dict.prior_options.prior.dtdphi.pop(bank, None)
		else:
			keep_bank.append(bank)
		
	if len(keep_bank)>1:
		copy_bank = keep_bank.copy()
		for index, bank in enumerate(copy_bank):
			if index==0:
				keep_bank = [bank]
				config_dict.data_product_options.data.template_bank.pop(bank, None)
				config_dict.svd_bank_options.svd.sub_banks.pop(bank, None)
			else:
				drop_bank.append(bank)
				config_dict.data_product_options.data.template_bank.pop(bank, None)
				config_dict.svd_bank_options.svd.sub_banks.pop(bank, None)
				if config_dict.prior_options.prior.dtdphi:
					config_dict.prior_options.prior.dtdphi.pop(bank, None)

		
	config_dict.data_product_options.template_bank = Config_utils.dotdict({"{}_lensed_bank".format(config.target_event) : "bank/{}_lensed_bank.xml.gz".format(config.target_event)})

	num_template = subprocess.getoutput("ligolw_print {}_lensed_bank.xml.gz -t sngl_inspiral | wc -l".format(config.generate_reduced_bank.rundir + "/" + config.target_event))

	config_dict.svd_bank_options.svd.sub_banks = Config_utils.dotdict({"{}_lensed_bank".format(config.target_event) : {
															"f_low" : 15.0,
															"num_banks" : 1,
															"num_chi_bins" : 1,
															"num_split_templates": num_template,
															"overlap" : 50,
															"samples_min": 512,
															"sort-by" : "mchirp",
															},
										})

	if config_dict.prior_options.prior.dtdphi:
		config_dict.prior_options.prior.dtdphi = Config_utils.dotdict({"{}_lensed_bank".format(config.target_event) : config_dict.prior_options.prior.dtdphi[keep_bank[0]]})


	def create_serach_run(config, config_dict, target_dir="./", filename_prefix=None):
		if not os.path.exists(target_dir):
			os.makedirs(target_dir)

		if not os.path.exists(target_dir + "/run/"):
			os.makedirs(target_dir + "/run/")

		os.system('cp -r {} {}'.format(config.injection_run.backup_dir + "/{bank,mass_model,inspiral_dtdphi_pdf}", target_dir))
		os.system('cp -r {} {}'.format("{}_lensed_bank.xml.gz".format(config.generate_reduced_bank.rundir + "/" + config.target_event), target_dir))

		config_dict.general_options.start = config.search_run.start_time 
		config_dict.general_options.start = config.search_run.end_time
		
		if filename_prefix == None:
			filename = output_file=target_dir + "{}_{}.yml".format(config.search_run.start_time, config.search_run.end_time)

		write_config(config_dict, output_file=target_dir + "{}.yml".format(filename_prefix))
	
	if config.search_run.start_time and config.search_run.end_time:
		target_dir = config.search_run.basedir + "/{}_{}/".format(config.search_run.start_time, config.search_run.end_time)
		create_serach_run(config, config_dict, target_dir)

	elif config.search_run.epoch and config.search_run.start_chunk and config.search_run.end_chunk:
		for chunk in numpy.linspace(config.search_run.start_chunk, config.search_run.end_chunk, 1, dtype=int):
			try:
				time_data = yaml.safe_load(open(config.tesla_dir + "/resources/chunk_times.yml"))
			except FileNotFoundError:
				raise FileNotFoundError("TESLA is mising an important resouce file. Please check.")
			else:
				config.search_run.start_time = time_data[config.search_run.epoch]["chunk%s"%chunk]['start']
				config.search_run.end_time = time_data[config.search_run.epoch]["chunk%s"%chunk]['end']
	
			target_dir = config.search_run.basedir + "/" + config.search_run.epoch + "_chunk" + str(chunk) + "/"
			create_serach_run(config, config_dict, target_dir, config.search_run.epoch + "_chunk" + str(chunk))


####################################################
#
# Step 5 : Rerank preparations
#
####################################################

if options.rerank:
	
	# Load configuration file
	config = Config.load(options.config)

	# Make the rerank directory
	if not os.path.exists(config.rerank.rundir):
		os.makedirs(config.rerank.rundir)

	assert config.rerank.search_run_list != [], "No runs to rerank. Please check."

	# Copy over the necessary files
	main_folder = ["reference_psd", "median_psd", "filter", "*config*yml"]
	
	for folder in main_folder:
		os.system("cp -r {} {}".format(folder, config.rerank.rundir + "/"))

	if len(config.rerank.search_run_list)>1:
		median_psd = glob.glob(config.rerank.rundir + "/median_psd/*/*xml.gz")
		for rundir in config.rerank.search_run_list[1:]:
			os.system("rsync -av {}/reference_psd/ {}".format(rundir, config.rerank.rundir + "/reference_psd/"))
			os.system("rsync -av {}/filter/ {}".format(rundir, config.rerank.rundir + "/filter/"))
			median_psd.append(glob.glob(rundir + "/median_psd/*/*xml.gz")[0])

	from lal.utils import CacheEntry
	final_file = CacheEntry(median_psd[0])
	for other_psd in median_psd[1:]:
		temp = CacheEntry(other_psd)
		final_file.segment.__add__(temp.segment)
	final_median_psd_name = final_file.url

	task = "gstlal_median_psd --output " + glob.glob(config.rerank.rundir + "/median_psd/*")[0] + "/" + final_median_psd_name
	for psd in median_psd:
		task = task + " " + psd

	os.system(task)

	for psd in glob.glob(config.rerank.rundir + "/median_psd/*/*"):
		if final_median_psd_name not in psd:
			os.system("rm {}".format(psd))

	if config.rerank.dtdphi or config.rerank.mass_model:
		sample_config = yaml.safe_load(open(glob.glob(config.rerank.rundir + "*yml")[0]))
		config_dict = {}
		config_dict['general_options'] = {}
		for key in ["instruments", "min_instruments", "start", "stop"]:
			config_dict['general_options'][key] = sample_config[key]
	
		config_dict["data_product_options"] = {}
		config_dict["data_product_options"]["data"] = sample_config["data"]

		config_dict["data_source_options"] = {}
		config_dict["data_source_options"]["source"] = sample_config["source"]

		config_dict["segments_options"] = {}
		config_dict["segments_options"]["segments"] = sample_config["segments"]

		config_dict["psd_options"] = {}
		config_dict["psd_options"]['psd'] = sample_config["psd"]
	
		config_dict["svd_bank_options"] = {}
		config_dict["svd_bank_options"]["svd"] = sample_config["svd"]
	
		config_dict["filtering_options"] = {}
		config_dict["filtering_options"]["filter"] = sample_config["filter"]

		config_dict["prior_options"] = {}
		config_dict["prior_options"]["prior"] = sample_config["prior"]
	
		config_dict["ranking_options"] = {}
		config_dict["ranking_options"]["rank"] = sample_config["rank"]
	
		config_dict['summary_options'] = {}
		config_dict['summary_options']['summary'] = sample_config['summary']
	
		config_dict['condor_options'] = {}
		config_dict['condor_options']['condor'] = sample_config['condor']
	
		config_dict = Config_utils.dotdict(config_dict)
			
		if config.rerank.dtdphi:
			config_dict.prior_options.dtdphi[list(config_dict.prior_options.dtdphi.keys())[0]] = config.rerank.dtdphi

		if config.rerank.mass_model:
			onfig_dict.prior_options.mass_model = config.rerank.mass_model

		write_config(config_dict, output_file=glob.glob(config.rerank.rundir + "*yml")[0])
