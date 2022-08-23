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
# Analyzers that process primary streams coming from respirometer and fitting the
# local oxygen changes by either linear relations or making some other analysis
# on the basis of raw oxygen trace

# This module is used through the other modules

import numpy as np

from iocbio.kinetics.calc.linreg import AnalyzerLinRegress
from iocbio.kinetics.calc.generic import Stats, XYData, AnalyzerGeneric
from iocbio.kinetics.constants import database_table_roi, database_table_experiment

from PyQt5.QtCore import pyqtSignal, QObject

class AnalyzerRespirationSignals(QObject):
    sigUpdate = pyqtSignal()

#######################################################################################
# Calculation of respiration rate from oxygen trace
class AnalyzerRespiration(AnalyzerLinRegress):
    """Analyzer used for respirometry measurements

    This is a linear regression analyzer made for analysis of
    respirometry data. It assumes that O2 concentration is stored in
    data field `o2`, takes derivative of it, and stores the results in
    table `VO2_raw`. In addition, database view is created to easily
    access average respiration rate and relate it to the events:
    `VO2_raw_events`. Note that the event names are converted into
    numbers, if possible, and stored into separate column
    `event_value` in the database. This allows to simplify secondary
    analysis, as in the kinetics experiments where respiration rate is
    related to the change in concentration of some substance.

    Parameters
    ----------
    database : iocbio.kinetics.io.db.DatabaseInterface
      Database access
    data : iocbio.kinetics.io.data.Data
      Data descriptor    
    """

    database_table = "VO2_raw"
    database_events_view = "VO2_raw_events"

    @staticmethod
    def database_schema(db):
        db.query("CREATE TABLE IF NOT EXISTS " + db.table(AnalyzerRespiration.database_table) +
                 "(data_id text PRIMARY KEY, " +
                 "rate double precision, " +
                 "FOREIGN KEY (data_id) REFERENCES " + db.table(database_table_roi) + "(data_id) ON DELETE CASCADE" +
                 ")")
        if not db.has_view(AnalyzerRespiration.database_events_view):
            db.query("CREATE VIEW " + db.table(AnalyzerRespiration.database_events_view) + " AS SELECT "
                    "r.experiment_id, rate, event_value, event_name FROM " + db.table("roi") + " r join " +
                    db.table(AnalyzerRespiration.database_table) + " v on r.data_id = v.data_id")


    def __init__(self, database, data):
        self.database_schema(database)
        AnalyzerLinRegress.__init__(self, data.x('o2'), data.y('o2').data)

        self.signals = AnalyzerRespirationSignals()
        self.database = database
        self.table_name = AnalyzerRespiration.database_table
        self.data = data
        self.axisnames = XYData("Time", "O2")
        self.axisunits = XYData("min", "umol/l")

        self.fit()

    def fit(self):
        AnalyzerLinRegress.fit(self)
        if self.database is not None:
            c = self.database
            if self.database.has_record(self.table_name, data_id=self.data.data_id):
                c.query("UPDATE " + self.database.table(self.table_name) +
                          " SET rate=:rate WHERE data_id=:data_id",
                          rate=-self.slope, data_id=self.data.data_id)
            else:
                c.query("INSERT INTO " + self.database.table(self.table_name) +
                          "(data_id, rate) VALUES(:data_id,:rate)",
                          data_id=self.data.data_id, rate=-self.slope)
        self.stats['VO2'] = Stats("Respiration rate", "umol/l/min", -self.slope)
        self.signals.sigUpdate.emit()

    def remove(self):
        c = self.database
        c.query("DELETE FROM " + self.database.table(self.table_name) +
                " WHERE data_id=:data_id",
                data_id=self.data.data_id)
        self.database = None # through errors if someone tries to do something after remove
        self.signals.sigUpdate.emit()

    def update_data(self, data):
        AnalyzerLinRegress.update_data(self, data.x('o2'), data.y('o2').data)
        self.fit()

    def update_event(self, event_name):
        ename = self.namecheck(event_name)
        try:
            evalue = float(ename)
        except:
            evalue = None
        self.data.event_name = ename
        self.data.event_value = evalue

    @staticmethod
    def namecheck(name):
        return name

    @staticmethod
    def slice(data, x0, x1):
        sdata = data.slice(x0, x1)
        events = data.config['events']
        etime = list(events.keys())
        etime.sort()
        ename = None

        for i in range(len(etime)-1):
            if etime[i] <= x0 and etime[i+1]>x0:
                ename = events[ etime[i] ]
        if ename is None and etime[-1] <= x0:
            ename = events[ etime[-1] ]

        ename = AnalyzerRespiration.namecheck(ename)
        try:
            evalue = float(ename)
        except:
            evalue = None

        sdata.event_name = ename
        sdata.event_value = evalue
        return sdata

    @staticmethod
    def auto_slicer(data):
        events = data.config['events']
        etime = list(events.keys())
        etime.sort()
        if len(etime) == 0: return []

        sliced_data = []
        def times(t0, t1):
            dt = (t1-t0)/4.0
            tm = (t0+t1)/2.0
            return tm-dt, tm+dt

        # v background
        sdata = AnalyzerRespiration.slice(data, *times(data.x('o2')[0],etime[0]))
        sdata.event_name = "VBG"
        sliced_data.append(sdata)

        for i in range(len(etime)-1):
            sliced_data.append(AnalyzerRespiration.slice(data, *times(etime[i],etime[i+1])))
        sliced_data.append(AnalyzerRespiration.slice(data,
                                                      *times(etime[-1], data.x('o2')[-1])))

        return sliced_data
