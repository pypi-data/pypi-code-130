#!/usr/bin/python3 -s
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

import time
import csv
import sys
import argparse
import numpy
from ligo.lw import ligolw
from ligo.lw import table
from ligo.lw import lsctables
from ligo.lw import utils as ligolw_utils
from ligo.lw.utils import process as ligolw_process
import lal
import lalsimulation
from lal import LIGOTimeGPS, ComputeDetAMResponse, GreenwichMeanSiderealTime, CachedDetectors
import pandas as pd
import os

#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#

#
# Calculate the antenna pattern response 
#

def compute_Fpc(detector, ra, dec, psi, t0):
    gmst = GreenwichMeanSiderealTime(LIGOTimeGPS(t0))
    return ComputeDetAMResponse(detector.response, ra, dec, psi, gmst)

#
# Calculate the effective distance from the detector to the source
#

def compute_Deff(D, inc, Fpc):
	return D*(Fpc[0]**2.0*((1+numpy.cos(inc)**2.0)/2)**2.0 + Fpc[1] ** 2.0* numpy.cos(inc) ** 2.) ** (-0.5)


#
# Compute luminosity distance from effective distance and antenna pattern response
#

def compute_D(Deff, inc, Fpc):
	return Deff * numpy.sqrt((Fpc[0]**2)*((1+numpy.cos(inc)**2)/2)**2+(Fpc[1]**2)*(numpy.cos(inc)**2))


def get_new_luminosity_distance(param_dict, focused_detector):
	temp_dict = param_dict[focused_detector]
	new_effective_distance = ( temp_dict['max_snr'] / temp_dict['min_snr'] ) * temp_dict['raw_effective_distance']
	Fpc_focused_detector = compute_Fpc(lal.CachedDetectors[lal_detector_dictionary[focused_detector]], param_dict['ra'], param_dict['dec'], param_dict['psi'], param_dict['tgps'])
	return compute_D(new_effective_distance, param_dict['inclination'], Fpc_focused_detector)


def validate_minimum_snr(param_dict, check_detector):
	temp_dict = param_dict[check_detector]
	Fpc = compute_Fpc(lal.CachedDetectors[lal_detector_dictionary[check_detector]], param_dict['ra'], param_dict['dec'], param_dict['psi'], param_dict['tgps'])
	new_effective_distance = compute_Deff(param_dict['new_luminosity_distance'], param_dict['inclination'], Fpc)
	return (temp_dict['raw_effective_distance'] / new_effective_distance) * temp_dict['max_snr'] < temp_dict['max_snr'], (temp_dict['raw_effective_distance'] / new_effective_distance) * temp_dict['max_snr']


#
# =============================================================================
#
#                                   Main
#
# =============================================================================
#	

def parse_command_line():
	parser = argparse.ArgumentParser()
	parser.add_argument('--injection-file', help='injection file in xml.gz')
	parser.add_argument('--pe-samples' ,help='PE samples of target event.')
	parser.add_argument('--o' ,help='output prefix')
	options = parser.parse_args()
	return options


startTime = time.time()

options = parse_command_line()



#
# Define the XML file handler.
#

class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
	pass

lsctables.use_in(LIGOLWContentHandler)


#
# Opening the original injection file and obtaining the original single 
# inspiral table.
# 

filename = options.injection_file
xmldoc_old = ligolw_utils.load_filename(filename,contenthandler = LIGOLWContentHandler, verbose = True)
xmldoc = ligolw.Document()
xmldoc = xmldoc_old
sim_inspiral_table=lsctables.SimInspiralTable.get_table(xmldoc)
#table.get_table(xmldoc, lsctables.SimInspiralTable.tableName)

#
# Load the posterior samples, and sort the samples in descending order of their 
# log likelihoods.
# 

df1 = pd.read_csv(options.pe_samples,header=0)
df1=df1.sort_values(by=['log_likelihood'],ascending=False)
df1=df1.head(n=10000)



#
#FIXME: Brand new way of registering detectors
# Get all the detectors if their optimal SNR exists in the samples
# Then sort. For the time being, we assume only H1, L1, V1 are present
# Later on, if K1 and A1 join the network, we might need some modification here.
#

print("Getting list of detectors...")

det = [key.split("_")[0] for key in df1.keys() if "optimal_snr" in key and "network" not in key]
det.sort()

print(det)

#
# negligible detectors (not requiring minimum SNR > 4)
#

print("Getting list of non negligible detectors...")

negligible_det = ["V1", "K1"]
non_negligible_det = [detector for detector in det if detector not in negligible_det]

print(non_negligible_det)

#
# Set the flag of whether the event is a single detector event or not
#

print("Determining if this is a single detector event...")

single_det_event = False if len(det)>1 and len(non_negligible_det)>1 else True

print("Single detector event: {}.".format(single_det_event))

# First cut in single_detector_event: Drop all samples with non-negligible detector SNR <= 4
if single_det_event:
	df1 = df1[df1[non_negligible_det[0] + "_optimal_snr"] > 4]



#
# We now start to replace original injections by simulated lensed injections.
# The following while loop runs until the original table is re-filled up.
#

k = 0
j = 0

#
# Initiate SNRs
#

lal_detector_dictionary = {
			"H1": lal.LALDetectorIndexLHODIFF,
			"L1": lal.LALDetectorIndexLLODIFF,
			"V1": lal.LALDetectorIndexVIRGODIFF,
			"G1": lal.LALDetectorIndexGEO600DIFF,
			"T1": lal.LALDetectorIndexTAMA300DIFF,
			"K1": lal.LALDetectorIndexKAGRADIFF,
			"I1": lal.LALDetectorIndexLIODIFF,
			"E1": lal.LALDetectorIndexE1DIFF,
			"E2": lal.LALDetectorIndexE2DIFF,
			"E3": lal.LALDetectorIndexE3DIFF,
			}

def initiate_dict(det, row):
	param_dict = {}
	param_dict['raw_luminosity_distance'] = float(row['luminosity_distance'])
	param_dict['ra'] = float(row['ra'])
	param_dict['dec'] = float(row['dec'])
	param_dict['tgps'] = float(row['geocent_time'])
	param_dict['inclination'] = float(row['theta_jn'])
	param_dict['psi'] = float(row['psi'])
	for detector in det:
		temp_dict = {}
		temp_dict['min_snr'] = 4.0 if float(row[detector + "_optimal_snr"]) > 4. else float(row[detector + "_optimal_snr"])
		temp_dict['max_snr'] = float(row[detector + "_optimal_snr"])
		temp_dict['raw_effective_distance'] = compute_Deff(param_dict['raw_luminosity_distance'], param_dict['inclination'], compute_Fpc(lal.CachedDetectors[lal_detector_dictionary[detector]], param_dict['ra'], param_dict['dec'], param_dict['psi'], param_dict['tgps']))
		param_dict[detector] = temp_dict
	return param_dict

while k < len(sim_inspiral_table):
	print("Currently working on row {} of sim_inspiral table...".format(k))
	repeat=False
	m = 0
	current = k

	#
	# For the current original injection, for each posterior sample, we
	# calculate the effective distances based on the sample parameters
	# (Distances, RA, DEC, snrs, time). We set the maximum SNR as the
	# SNRs reported in the sample and the minimum snr to be 4 (except for VIRGO). 
	# The following loop runs until...
	# (1) A suitable posterior sample has been found, or 
	# (2) All the samples have been processed.
	#

	for index, row in df1.iterrows():
		print("Looping through sample number {}.".format(index))
		param_dict = initiate_dict(det, row)
		
		# Update the time with the current row time
		param_dict['tgps'] = sim_inspiral_table[k].geocent_end_time + sim_inspiral_table[k].geocent_end_time_ns*1.0e-9

		accept = False
		check = False

		#
		# For the current posterior sample, based on the fact that D_eff = k/SNR,
		# where k is a proportionality constant, we re-evaluate the new SNR of the
		# other detectors given that the first detector SNR is 4, based on the sky
		# location of the original injection. If the new detector SNR is smaller
		# than 4, we increase the first detector SNR in steps of 0.1, and repeat
		# the whole process until...
		# (1) the minimum new detector SNR >=4, or
		# (2) the minimum first detector SNR becomes larger or equals to the maximum
		#     SNR, in which we will skip the current posterior sample and continue
		#     the above loop.
		# This step ensures that the injection will have an optimal SNR >= 4 in at
		# least two detectors.

		
		# First deal with "single" detector events
		if single_det_event:

			# Check if the event is really single-detector
			assert len(non_negligible_det)==1, "More than one non-negligible detectors. This is not a single detector event."

			focused_detector = non_negligible_det[0]
			
			# Stop and exit immediately if the minimum SNR is larger than the maximum SNR. Something is wrong if this happens.
			assert param_dict[focused_detector][min_snr] < param_dict[focused_detector][max_snr], "Minimum SNR of non-negligible detector > maximum SNR. Error."

			# Now check to see if the new minimum SNR in each detector is smaller than the original SNR.
			param_dict['new_luminosity_distance'] = get_new_luminosity_distance(param_dict, focused_detector)
			
			other_detector = [detector for detector in det if detector != focused_detector]

			for detector in other_detector:
				validate, _ = validate_minimum_snr(param_dict, detector)
				if validate:
					check=True
				else:
					check=False
			#
			# Terminate the loop and substitute injections directly if all requirements are met
			# Also remove the sample from the list to avoid repeated substitution.
			#
			if check:
				chosen=index
				break
		
		# Now deal with multi-detector events
		else:
			# First register all the information of the non-negligible detectors
			major_detector_dict = {}
			for detector in non_negligible_det:
				major_detector_dict[detector] = param_dict[detector]
			
			# Choose the detector with either the second LARGEST (if more than two detectors) or 
			# LOWEST maximum SNR (only two detectors) as the focused detector.
			focused_detector = sorted(major_detector_dict.items(), key = lambda x: x[1].get("max_snr"))[-2][0]
			
			# Discard the sample if the focused detector minimum SNR < 4.
			if major_detector_dict[focused_detector]['min_snr'] < 4:
				df1.drop(index, inplace=True)
				continue

			accept = False
			immediate_stop = False
			while accept == False:
				trigger_counter = 1
				
				param_dict['new_luminosity_distance'] = get_new_luminosity_distance(param_dict, focused_detector)
				
				for detector in det:
					if detector != focused_detector:
						validate, new_min_snr = validate_minimum_snr(param_dict, detector)
						if validate:
							param_dict[detector]['min_snr'] = new_min_snr
							if new_min_snr >= 4.:
								trigger_counter += 1
						else:
							immediate_stop = True
							break
				if immediate_stop:
					break
	
				if trigger_counter > 1:
					check = True
					accept = True
				else:
					param_dict[focused_detector]['min_snr'] += 0.1
			
			if check:
				chosen=index
				break

	#
	# Using the minimum SNR we found for the focused detector, we then create 10
	# simulated lensed injections with SNR in each detector being equally spaced
	# between the maximum and minimum values inclusively, and replace up to 10
	# rows of the original single inspiral table by these injections.
	#
	
	if check:
		l = 0
		while l < 10:
			step = (param_dict[focused_detector]['max_snr'] - param_dict[focused_detector]['min_snr']) / 9.

			if k < len(sim_inspiral_table):
				sim_inspiral_table[k].mass1 = float(row['mass_1'])
				sim_inspiral_table[k].mass2 = float(row['mass_2'])
				sim_inspiral_table[k].mchirp = float(row['chirp_mass'])
				sim_inspiral_table[k].longitude = param_dict['ra']
				sim_inspiral_table[k].latitude = param_dict['dec']
				sim_inspiral_table[k].inclination = param_dict['inclination']
				sim_inspiral_table[k].polarization = param_dict['psi']
				sim_inspiral_table[k].coa_phase = float(row['phase'])
				
				param_dict[focused_detector]['min_snr'] = param_dict[focused_detector]['min_snr'] + step * l
				param_dict['new_luminosity_distance'] = get_new_luminosity_distance(param_dict, focused_detector)
				sim_inspiral_table[k].distance = param_dict['new_luminosity_distance']

				if 'spin_1x' in df1:
					sim_inspiral_table[k].spin1x = float(row['spin_1x'])
					sim_inspiral_table[k].spin1y = float(row['spin_1y'])
					sim_inspiral_table[k].spin1z = float(row['spin_1z'])
					sim_inspiral_table[k].spin2x = float(row['spin_2x'])
					sim_inspiral_table[k].spin2y = float(row['spin_2y'])
					sim_inspiral_table[k].spin2z = float(row['spin_2z'])
				else:
					sim_inspiral_table[k].spin1z = float(row['a_1'])
					sim_inspiral_table[k].spin2z = float(row['a_2'])
			else:
				break
			k = k + 1
			l = l + 1
		df1.drop(chosen, inplace=True)
	
	else:
		del(sim_inspiral_table[k])

# 
# Save the resulting modified injection file.
# 
#cwd = os.getcwd() + "/"

output_file = options.o + ".xml.gz"
ligolw_utils.write_filename(xmldoc, output_file)
xmldoc.unlink()

executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))
