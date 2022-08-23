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
# Analyzers that process primary streams coming from Spectrophotometer and fitting the
# local absorbance changes by linear relations

from iocbio.kinetics.calc.linreg import AnalyzerLinRegress, AnalyzerLinRegressDB
from iocbio.kinetics.calc.explin_fit import AnalyzerExpLinFit
from iocbio.kinetics.calc.generic import Stats, XYData, AnalyzerGeneric
from iocbio.kinetics.calc.mean_med_std import AnalyzerMeanMedStdDB
from iocbio.kinetics.calc.mm import AnalyzerMMDatabase
from iocbio.kinetics.constants import database_table_roi, database_table_experiment

from PyQt5.QtCore import pyqtSignal, QObject
import collections

### Module flag
IocbioKineticsModule = ['analyzer', 'database_schema']

### Implementation

class AnalyzerSpectroSignals(QObject):
    sigUpdate = pyqtSignal()


class AnalyzerSpectro(AnalyzerLinRegress):

    table_name = "spectro_dabsdt_raw"
    view_name = "spectro_dabsdt_raw_conc"

    @staticmethod
    def database_schema(db):
        db.query("CREATE TABLE IF NOT EXISTS " + db.table(AnalyzerSpectro.table_name) +
                 "(data_id text PRIMARY KEY, " +
                 "rate double precision, " +
                 "FOREIGN KEY (data_id) REFERENCES " + db.table(database_table_roi) + "(data_id) ON DELETE CASCADE" +
                 ")")
        viewname=AnalyzerSpectro.view_name
        if not db.has_view(viewname):
            db.query("CREATE VIEW " + db.table(viewname) + " AS SELECT "
                    "r.experiment_id, rate, event_value, event_name FROM " + db.table("roi") + " r join " +
                    db.table(AnalyzerSpectro.table_name) + " v on r.data_id = v.data_id")


    def __init__(self, database, data):
        self.database_schema(database)
        AnalyzerLinRegress.__init__(self, data.x('abs'), data.y('abs').data)

        self.signals = AnalyzerSpectroSignals()
        self.database = database
        self.data = data
        self.axisnames = XYData("Time", "Absorbance")
        self.axisunits = XYData("min", "")

        self.fit()

    def fit(self):
        AnalyzerLinRegress.fit(self)
        if self.slope is None or self.intercept is None:
            self.remove()
            return
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
        self.stats['Rate'] = Stats("Absorbance change rate", "Abs/min", -self.slope)
        self.signals.sigUpdate.emit()

    def remove(self):
        c = self.database
        c.query("DELETE FROM " + self.database.table(self.table_name) +
                " WHERE data_id=:data_id",
                data_id=self.data.data_id)
        self.signals.sigUpdate.emit()

    def update_data(self, data):
        AnalyzerLinRegress.update_data(self, data.x('abs'), data.y('abs').data)
        self.fit()

    def update_event(self, event_name):
        ename = AnalyzerSpectro.namecheck(event_name)
        try:
            evalue = float(ename)
        except:
            evalue = None
        self.data.event_name = ename
        self.data.event_value = evalue

    @staticmethod
    def namecheck(name):
        if name in ["CM"]:
            return "V0"
        return name

    @staticmethod
    def slice(data, x0, x1):
        sdata = data.slice(x0, x1)
        xref = (x0+x1)/2.0
        ename = None
        for _,e in data.config['events_slice'].items():
            if e['time'][0] <= xref and e['time'][1]>xref:
                ename = e['name']
                break

        try:
            evalue = float(ename)
        except:
            evalue = None

        sdata.event_name = ename
        sdata.event_value = evalue
        return sdata

    @staticmethod
    def auto_slicer(data):
        events = data.config['events_slice']

        sliced_data = []
        def times(t0, t1):
            dt = (t1-t0)/4.0
            tm = (t0+t1)/2.0
            return tm-dt, tm+dt

        for _, i in events.items():
            sliced_data.append(AnalyzerSpectro.slice(data, *times(i['time'][0],i['time'][1])))

        return sliced_data


class AnalyzerSpectroCytOx(AnalyzerExpLinFit):

    table_name = 'spectro_cytox'

    @staticmethod
    def database_schema(db):
        db.query("CREATE TABLE IF NOT EXISTS " + db.table(AnalyzerSpectroCytOx.table_name) +
                 "(data_id text PRIMARY KEY, " +
                 "exponential_amplitude double precision, rate_constant double precision, " +
                 "linear_offset double precision, linear_slope double precision, " +
                 "FOREIGN KEY (data_id) REFERENCES " + db.table(database_table_roi) + "(data_id) ON DELETE CASCADE" +
                 ")")

    def __init__(self, database, data):
        self.database_schema(database)
        AnalyzerExpLinFit.__init__(self, data.x('abs'), data.y('abs').data)

        self.signals = AnalyzerSpectroSignals()
        self.database = database
        self.data = data

        self.axisnames = XYData("Time", "Absorbance")
        self.axisunits = XYData("min", "")

        self.fit()

    def fit(self):
        AnalyzerExpLinFit.fit(self)
        if self.database is not None:
            c = self.database
            if self.database.has_record(self.table_name, data_id=self.data.data_id):
                c.query("UPDATE " + self.database.table(self.table_name) +
                        " SET exponential_amplitude=:exponential_amplitude, rate_constant=:rate_constant, " +
                        "linear_offset=:linear_offset, linear_slope=:linear_slope WHERE data_id=:data_id",
                        exponential_amplitude=self.exponential_amplitude,
                        rate_constant=self.rate_constant,
                        linear_offset=self.linear_offset,
                        linear_slope=self.linear_slope,
                        data_id=self.data.data_id)
            else:
                c.query("INSERT INTO " + self.database.table(self.table_name) +
                        " (data_id, exponential_amplitude, rate_constant, linear_offset, linear_slope) " +
                        " VALUES(:data_id, :exponential_amplitude, :rate_constant, :linear_offset, :linear_slope)",
                        exponential_amplitude=self.exponential_amplitude,
                        rate_constant=self.rate_constant,
                        linear_offset=self.linear_offset,
                        linear_slope=self.linear_slope,
                        data_id=self.data.data_id)

        self.signals.sigUpdate.emit()

    def remove(self):
        c = self.database
        c.query("DELETE FROM " + self.database.table(self.table_name) +
                " WHERE data_id=:data_id",
                data_id=self.data.data_id)
        self.database = None # through errors if someone tries to do something after remove
        self.signals.sigUpdate.emit()

    def update_data(self, data):
        AnalyzerExpLinFit.update_data(self, data.x('abs'), data.y('abs').data)
        self.fit()

    def update_event(self, event_name):
        self.data.event_name = event_name
        self.data.event_value = 0

    @staticmethod
    def slice(data, x0, x1):
        sdata = data.slice(x0, x1)
        return sdata

    @staticmethod
    def auto_slicer(data):
        return []
        # x = data.x('abs')
        # l = len(x)
        # x0, x1 = data.x('abs')[int(0.2*l)], data.x('abs')[int(0.8*l)]
        # sliced_data = [AnalyzerSpectroCytOx.slice(data, x0, x1)]
        # return sliced_data


#############################################################################

class AnalyzerSpectroTrace(AnalyzerLinRegressDB):

    def __init__(self, database, data):
        AnalyzerLinRegressDB.__init__(self, database=database, data=data, channel='abs')
        self.axisnames = XYData("Time", "Absorbance")
        self.axisunits = XYData("min", "")
        self.fit()

    def fit(self):
        AnalyzerLinRegressDB.fit(self)
        self.stats['Rate'] = Stats("Absorbance change rate", "Abs/min", -self.slope)
        self.signals.sigUpdate.emit()

############################################################################

class AnalyzerSpectroMM_ATParg(AnalyzerMMDatabase):
    def __init__(self, database, data):
        AnalyzerMMDatabase.__init__(self, database,
                                    "spectro_dabsdt_mm_raw",
                                    AnalyzerSpectro.view_name,
                                    data.experiment_id)
        self.axisnames = XYData("ATP", "dAbs/dt")
        self.axisunits = XYData("mM or possibly other", "1/min")

############################################################################

class AnalyzerSpectroAA3(AnalyzerMeanMedStdDB):
    database_table = "spectro_aa3_raw"
    view_name = "spectro_aa3_raw_peak"

    @staticmethod
    def database_schema(db):
        AnalyzerMeanMedStdDB.database_schema(db, AnalyzerSpectroAA3.database_table)

        viewname=AnalyzerSpectroAA3.view_name
        if not db.has_view(viewname):
            db.query("CREATE VIEW " + db.table(viewname) + " AS SELECT "
                     """r1.experiment_id, ksar1.mean - ksar2.mean AS aa3_peak
                     from %s ksar1
                     join %s r1 on ksar1.data_id = r1.data_id
                     join %s r2 on r1.experiment_id = r2.experiment_id
                     join %s ksar2 on ksar2.data_id = r2.data_id
                     where
                     r1.event_name = 'Peak'
                     and r2.event_name = 'Reference'""" % ( db.table(AnalyzerSpectroAA3.database_table),
                                                            db.table(database_table_roi),
                                                            db.table(database_table_roi),
                                                            db.table(AnalyzerSpectroAA3.database_table) ) )

    def __init__(self, database, data):
        AnalyzerMeanMedStdDB.__init__(self, database, data, AnalyzerSpectroAA3.database_table, "AA3")
        self.axisnames = XYData("Wavelength", "Absorbance")
        self.axisunits = XYData("nm", "Abs")
        self.fit()

    @staticmethod
    def slice(data, x0, x1, name = None):
        sdata = data.slice(x0, x1)
        sdata.event_name = name
        sdata.event_value = None
        return sdata


class AnalyzerSpectroAA3Peak(AnalyzerSpectroAA3):
    @staticmethod
    def slice(data, x0, x1):
        return AnalyzerSpectroAA3.slice(data, x0, x1, 'Peak')

    @staticmethod
    def auto_slicer(data):
        return [ AnalyzerSpectroAA3Peak.slice(data, 603, 607) ]

class AnalyzerSpectroAA3Reference(AnalyzerSpectroAA3):
    @staticmethod
    def slice(data, x0, x1):
        return AnalyzerSpectroAA3.slice(data, x0, x1, 'Reference')

    @staticmethod
    def auto_slicer(data):
        return [ AnalyzerSpectroAA3Reference.slice(data, 628, 640) ]

class AnalyzerSpectroAA3OverallPlot(AnalyzerGeneric):
    def __init__(self, database, data, event_name):
        AnalyzerGeneric.__init__(self, [], [])
        self.signals = AnalyzerSpectroSignals()
        self.database = database
        self.data = data
        self.event_name = event_name
        self.axisnames = XYData("Scan number", "Mean")
        self.axisunits = XYData("-", "Abs")
        self.calc = XYData([], [])
        self.update()

    def update(self):
        values = collections.defaultdict(list)
        d = self.data._data['prep reduced']['individual']
        dx = d['x']
        dy = d['y']
        for row in self.database.query("SELECT x0, x1, event_name FROM "+
                                       self.database.table(database_table_roi) +
                                       " WHERE experiment_id=:eid", eid = self.data.experiment_id ):
            x0, x1 = row.x0, row.x1
            for i in range(dx.shape[1]):
                v = 0.0
                c = 0
                for j in range(dx.shape[0]):
                    if dx[j,i] >= x0 and dx[j,i] <= x1:
                        v += dy[j,i]
                        c += 1
                values[ row.event_name ].append(v / c)

        xx, yy = [], []
        if 'Peak' in values and 'Reference' in values:
            p = values['Peak']
            r = values['Reference']
            for i in range(len(p)):
                xx.append(i)
                yy.append(p[i] - r[i])

        self.experiment = XYData(xx, yy)
        self.signals.sigUpdate.emit()

class AnalyzerSpectroAA3OverallStats(AnalyzerGeneric):
    def __init__(self, database, data):
        AnalyzerGeneric.__init__(self, [], [])
        self.signals = AnalyzerSpectroSignals()
        self.database = database
        self.data = data
        self.update()

    def update(self):
        # calc the difference
        for row in self.database.query("SELECT aa3_peak FROM " +
                                       self.database.table(AnalyzerSpectroAA3.view_name) +
                                       " WHERE experiment_id=:eid",
                                       eid = self.data.experiment_id):
            self.stats['AA3 peak'] = Stats("AA3 peak", "Abs", row.aa3_peak)
        self.signals.sigUpdate.emit()


#####################
#### ModuleAPI ######

def analyzer(database, data):
    titration_types = {
        'Thermo Evo 600 AK activity F': 'ak_activity_forward',
        'Thermo Evo 600 AK activity R': 'ak_activity_reverse',
        'Thermo Evo 600 ATPase activity': 'atpase_activity',
        'Thermo Evo 600 CK activity': 'ck_activity',
        'Thermo Evo 600 CK activity F': 'ck_activity',
        'Thermo Evo 600 CK activity R': 'ck_activity',
        'Thermo Evo 600 PK activity': 'pk_activity',
        'Thermo Evo 600 HK activity': 'hk_activity',
        }

    Analyzer = None
    overall = None
    stats = None
    if data.type in titration_types:
        Analyzer = { 'default': AnalyzerSpectro }
    elif data.type == "Thermo Evo 600 Spectro CytOx":
        Analyzer = { 'default': AnalyzerSpectroCytOx }
    elif data.type == "Thermo Evo 600 Spectro Trace":
        Analyzer = { 'default': AnalyzerSpectroTrace }
    elif data.type == "Thermo Evo 600 AA3":
        Analyzer = { 'AA3 Peak': AnalyzerSpectroAA3Peak,
                     'AA3 Reference': AnalyzerSpectroAA3Reference }
        overall = { 'AA3 Peak': AnalyzerSpectroAA3OverallPlot(database, data, 'Peak'),
                    'AA3 Reference': AnalyzerSpectroAA3OverallPlot(database, data, 'Reference') }
        stats = [ AnalyzerSpectroAA3OverallStats(database, data) ]
    else:
        return None, None, None

    if data.type in ['Thermo Evo 600 ATPase activity', 'Thermo Evo 600 PK activity']:
        overall = dict(default = AnalyzerSpectroMM_ATParg(database, data))

    return Analyzer, overall, stats


def database_schema(db):
    AnalyzerSpectro.database_schema(db)
    AnalyzerSpectroCytOx.database_schema(db)
    AnalyzerSpectroAA3.database_schema(db)
