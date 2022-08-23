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

import argparse
import sys
import numpy
from ligo.lw import ligolw
from ligo.lw import table
from ligo.lw import lsctables
from ligo.lw import utils as ligolw_utils
from ligo.lw import types
import copy
import sqlite3

#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#

def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='sqlite database')
    parser.add_argument('--bank', default = 'gstlal_bank_O3.xml.gz', help='combined template bank of the injection run')
    parser.add_argument('-o', "--output", default = 'lensed_bank.xml.gz', help='output filename')
    options = parser.parse_args()
    return options

options = parse_command_line()

#
# =============================================================================
#
#                                   Main
#
# =============================================================================
#


#
# Define the XML file handler.
#

class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
	pass

lsctables.use_in(LIGOLWContentHandler)

conn = sqlite3.connect(options.database)
cursor = conn.cursor()
array = numpy.array(cursor.execute('SELECT DISTINCT a.Gamma0 FROM sngl_inspiral AS a JOIN coinc_event_map AS b ON (b.event_id = a.event_id) JOIN coinc_inspiral AS c ON (c.coinc_event_id = b.coinc_event_id) where c.combined_far <= ?;', (3.86e-7,)).fetchall())

array = numpy.sort(array, axis=None)
print("Number of found injections = {}".format(len(array)))

xmldoc_old = ligolw_utils.load_filename(options.bank,contenthandler = LIGOLWContentHandler, verbose = True)
xmldoc= ligolw.Document()
xmldoc=xmldoc_old
sngl_inspiral_table=lsctables.table.get_table(xmldoc, lsctables.SnglInspiralTable.tableName)

#
# Temporary new single inspiral tables to stored the retained templates.
#

sngl_inspiral_table2=lsctables.New(lsctables.SnglInspiralTable)
sngl_inspiral_table3=lsctables.New(lsctables.SnglInspiralTable)

i=0
while i<len(array):
	print("Now working on template %s"%(i))
	count = 0
	done = False
	k=0
	while done==False:
		if(int(array[i])==sngl_inspiral_table[k].Gamma0):
			n = copy.deepcopy(sngl_inspiral_table[k])
			sngl_inspiral_table3.append(sngl_inspiral_table[k])
			sngl_inspiral_table2.append(n)
			print("Added one template. Number of templates in RTB is {}.".format(i))
			count=count+1
			done = True
			i = i+1
		k = k+1
	

#
# We then detach the original sngl_inspiral table from the template bank, and 
# append the temporary table to it. 
#

xmldoc.childNodes[0].childNodes[0].parentNode = None
xmldoc.childNodes[0].childNodes[0] = sngl_inspiral_table2
sngl_inspiral_table2.parentNode = xmldoc.childNodes[0]
xmldoc.childNodes[0]._verifyChildren(0)

#
# Finally, we save the result into a new template bank .xml.gz file as the
# reduced template bank.
#


ligolw_utils.write_filename(xmldoc, options.o, gz = True, verbose = True)
xmldoc.unlink()
