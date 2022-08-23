# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2019-2020
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  This file is part of project: IOCBIO Kinetics
#

import hashlib
import csv
from iocbio.kinetics.handler.experiment_generic import ExperimentGeneric
from iocbio.kinetics.io.data import Data, Carrier
from .experiment import ExperimentO2k
from iocbio.kinetics.constants import database_table_experiment
import os.path
import re
import array as arr
import numpy
import collections

IocbioKineticsModule = ["reader","args"]

def args(parser):
    parser.add(name='o2k_chamber', help='The selection of the Chamber of Interest: A or B')
    parser.add(name="date_time", help = "The date of the experiment in the format of YYYY-MM-DD HH:MM")
    return '''Oroboros 2K Protocols:
------------------
VO2 generic - Generic Respiration Rate Experiment
'''

def mergeevent(name, text):
    if name and text: return "%s %s" % (name, text)
    if name: return name
    return text

def reader( txt , o2kchamber):
    text = csv.DictReader(txt.splitlines())

    e=collections.defaultdict(list)

    for row in text:
        for k in row.keys():
            try:
                e[k].append(float(row[k]))
            except:
                if k == "Event Name" or k == "Chamber" or k == "Event Text":
                    e[k].append(row[k])
                else:
                    e[k].append(None)

    events = {}

    time = e["Time [min]"]

    # O2K calls chambers 4A and 4B. Name here accordingly
    o2kInd = '4%s' % o2kchamber

    # compose x,y pairs for the data we are interested in
    dkeys = {
        "o2": dict(name = "O2 concentration", unit = "µM", key = o2kInd + ": O2 concentration [µM]"),
        "vo2": dict(name = "O2 flow per cells", unit = "pmol/(s*Mill)",
                    key = o2kInd + ": O2 flow per cells [pmol/(s*Mill)]"),
        "Amp": dict(name = "Amp", unit = "µM", key = o2kInd + ": Amp [µM]"),
        "Amp slope": dict(name = "Amp slope", unit = "pmol/(s*Mill)", key = o2kInd + ": Amp slope [pmol/(s*mL)]"),
        "Block temp": dict(name = "Block temp", unit = "C", key = "4: Block temp. [°C]"),
        "Peltier power": dict(name = "Peltier power", unit = "%", key = "4: Peltier power [%]"),
        "pX": dict(name = "Potentiometric raw signal", unit = "V", key = o2kInd + ": pX [1]"),
        "pX slope": dict(name = "Potentometric raw signal slope", unit = "pX*10^-3/s",
                         key = o2kInd + ": pX slope [pX*10^-3/s]"),
        "Room temp": dict(name = "Room temperature", unit = "C", key = "4: Room temp. [°C]"),
        "Temp. ext. channel": dict(name = "Temperature through external channel", unit = "C",
                                   key = "4: Temp. ext. channel [°C]")
    }

    E = {}
    for K,V in dkeys.items():
        x, y = [], []
        k = V['key']
        for i in range(len(e[k])):
            if e[k][i] is not None:
                x.append(time[i])
                y.append(e[k][i])
        print(K, k, len(x), len(y))
        E[K] = dict(x = numpy.array(x),
                    y = Carrier(V['name'], V['unit'], numpy.array(y)))

    print(E.keys())

    eventname = e["Event Name"]
    eventtext = e["Event Text"]
    chamber = e["Chamber"]

    for i in range(len(chamber)):
        if o2kchamber == "A":
            if chamber[i] == "Left" or chamber[i] == "Both":
                events[time[i]] = mergeevent(eventname[i], eventtext[i])
        elif o2kchamber == "B" :
            if chamber[i] == "Right" or chamber[i] == "Both":
                events[time[i]] = mergeevent(eventname[i], eventtext[i])

    return E, dict(events = events), (time[0], time[-1])

def create_data(database, experiment_id = None, args= None):
    filename=getattr(args, "file_name", None)
    o2kchamber = getattr(args, "o2k_chamber", None)
    date = getattr(args, "date_time", None)
    fulltxt = None

    if experiment_id is not None:
        fulltxt, name, o2kchamber, date = ExperimentO2k.get_fulltxt(database, experiment_id)

    if fulltxt is None and \
       filename is not None and o2kchamber is not None and \
       filename.find("csv") != -1:
        if date is None:
            print("Please specify date and time using 'date-time' argument as Oroboros CSV export does not contain this information")
            return None
        head, cname = os.path.split(filename)
        name = cname + "-" + o2kchamber
        fulltxt = open(filename, encoding = "ISO-8859-1").read()

    if fulltxt is None: return None

    dd, conf, xlim = reader(fulltxt, o2kchamber)

    if experiment_id is None:
        expid = "Oroboros 2K CSV - %s - %s" % (o2kchamber, hashlib.sha256(fulltxt.encode("utf-8")).hexdigest())
    else:
        expid = experiment_id

    data = Data( expid,
                 config = conf,
                 type = "Oroboros 2K CSV experiment",
                 type_generic = "VO2 generic",
                 time = date,
                 name = name,
                 xname = "Time",
                 xunit = "min",
                 xlim = xlim,
                 data = dd)

    if not ExperimentGeneric.has_record(database, data.experiment_id):
        database.set_read_only(False)
        ExperimentO2k.store(database, data, fulltxt, name, filename, date, o2kchamber)

    return data
