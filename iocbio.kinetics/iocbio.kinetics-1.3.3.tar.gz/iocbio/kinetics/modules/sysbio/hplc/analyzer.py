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

import numpy as np

from iocbio.kinetics.calc.peakarea import AnalyzerBaseline, AnalyzerPeakAreaDB
from iocbio.kinetics.calc.generic import AnalyzerGenericSignals, AnalyzerGeneric, XYData, Stats
from iocbio.kinetics.calc.composer import AnalyzerCompose
from iocbio.kinetics.constants import database_table_roi

### Module flag
IocbioKineticsModule = ['analyzer', 'database_schema']

# primary analyzers
class AnalyzerHPLCBaseline(AnalyzerBaseline):
    def __init__(self, database, data):
        AnalyzerBaseline.__init__(self, database, data, 'signal', 'hplc signal')

    @staticmethod
    def auto_slicer(data):
        p0 = data.config['peak_start_time']
        p1 = data.config['peak_end_time']
        sliced = []
        if len(p0) == len(p1):
            for i in range(len(p0)):
                dp = (p1[i]-p0[i])/10
                sliced.append(AnalyzerHPLCPeaks.slice(data, p0[i]-dp, p0[i]))
                sliced.append(AnalyzerHPLCPeaks.slice(data, p1[i], p1[i]+dp))
        return sliced


class AnalyzerHPLCPeaks(AnalyzerPeakAreaDB):
    def __init__(self, database, data):
        AnalyzerPeakAreaDB.__init__(self, database, data, 'signal', 'hplc signal')

    @staticmethod
    def auto_slicer(data):
        p0 = data.config['peak_start_time']
        p1 = data.config['peak_end_time']
        sliced = []
        if len(p0) == len(p1):
            for i in range(len(p0)):
                sliced.append(AnalyzerHPLCPeaks.slice(data, p0[i], p1[i]))
        return sliced


#######################################################
# secondary analyzers to show data from many experiments

database_series = 'hplc_series'
database_series_probe = 'hplc_series_probe'
database_calibration = 'hplc_peak_calibration'
database_peak_value = 'hplc_peak_value'
database_calibration_fit = 'hplc_calibration_fit'

class AnalyzerHPLCOverallOneType(AnalyzerGeneric):
    def __init__(self, database, series_id, roi_tag_name, is_calibration, calibration_series):
        AnalyzerGeneric.__init__(self, [], [])
        self.db = database
        self.series = series_id
        self.tag = roi_tag_name if roi_tag_name is not None else ''
        self.is_calibration = is_calibration
        self.calibration_series = None
        self.signals = AnalyzerGenericSignals()

        if calibration_series is not None:
            # ensure that we have calibration available for this tag
            for q in self.db.query("select 1 from " +
                                   self.db.table(database_calibration_fit) +
                                   " where series_id=:series and tag=:tag",
                                   series = calibration_series, tag = self.tag):
                self.calibration_series = calibration_series

        self.update()

    def _update_calibration(self):
        a = []
        v = []
        for q in self.db.query("select a.area, cp.value from " +
                               self.db.table(database_series) + " s join " +
                               self.db.table(database_series_probe) + " p on p.series = s.id join " +
                               self.db.table(database_table_roi) + " roi on roi.experiment_id = p.probe join " +
                               self.db.table(database_calibration) + " cp on cp.roi = roi.data_id join " +
                               self.db.table(AnalyzerHPLCPeaks.database_table) + " a on a.data_id = roi.data_id " +
                               "where s.id=:series and roi.event_name = :tag order by a.area",
                               series = self.series, tag = self.tag):
            a.append(q.area)
            v.append(q.value)
        self.axisnames = XYData('Area', self.tag + " value")
        self.axisunits = XYData('area', 'value')
        AnalyzerGeneric.update_data(self, np.array(a), np.array(v))

        self.calc = XYData([], [])
        for q in self.db.query("select slope, intercept, r2 from " +
                               self.db.table(database_calibration_fit) +
                               " where series_id=:series and tag=:tag",
                               series = self.series, tag = self.tag):
            x = np.array([0, a[-1]])
            self.calc = XYData(x, x*q.slope + q.intercept)
            self.stats['slope'] = Stats("Slope", "value/area", q.slope)
            self.stats['intercept'] = Stats("Intercept", "value", q.intercept)
            self.stats['r2'] = Stats("r2", "", q.r2)

    def _update_peak(self):
        data = []
        if self.calibration_series is not None:
            for q in self.db.query("select khsp.name, kp.value from " +
                                   self.db.table(database_peak_value) + " kp " +
                                   "join " + self.db.table(database_table_roi) + " roi on roi.data_id = kp.data_id " +
                                   "join " + self.db.table(database_series_probe) +
                                   " khsp on khsp.probe = roi.experiment_id where " +
                                   "khsp.success and khsp.series=:series and roi.event_name=:tag",
                                   series = self.series, tag = self.tag):
                data.append((q.name, q.value))
            yunit = 'value'
        else:
            for q in self.db.query("select khsp.name, kp.area from " +
                                   self.db.table(AnalyzerHPLCPeaks.database_table) + " kp " +
                                   "join " + self.db.table(database_table_roi) + " roi on roi.data_id = kp.data_id " +
                                   "join " + self.db.table(database_series_probe) +
                                   " khsp on khsp.probe = roi.experiment_id where " +
                                   "khsp.success and khsp.series=:series and roi.event_name=:tag",
                                   series = self.series, tag = self.tag):
                data.append((q.name, q.area))
            yunit = 'area'

        isnumeric = True
        for v in data:
            try:
                _ = float(v[0])
            except:
                isnumeric = False

        if isnumeric:
            data = [ (float(v[0]), v[1]) for v in data ]
        data.sort()
        key, val = [], []
        for i in range(len(data)):
            v = data[i]
            key.append(v[0] if isnumeric else i)
            val.append(v[1])

        self.axisnames = XYData('Probe name', self.tag)
        self.axisunits = XYData('#', yunit)
        AnalyzerGeneric.update_data(self, np.array(key), np.array(val))

    def update(self):
        if self.is_calibration:
            self.db.query("select refresh_kinetics_hplc_calibration_fit()")
            self._update_calibration()
        else:
            self._update_peak()

        self.signals.sigUpdate.emit()


class AnalyzerHPLCOverall(AnalyzerCompose):

    def __init__(self, database, data):
        AnalyzerCompose.__init__(self)
        self.db = database
        self.experiment_id = data.experiment_id
        self.series = None
        for q in self.db.query('select series from ' +
                               self.db.table(database_series_probe) +
                               ' where probe=:expid',
                               expid = self.experiment_id):
            self.series = q.series

        self.is_calibration = False
        self.calibration_series = None
        if self.series is not None:
            for q in self.db.query('select id, calibration from ' + self.db.table(database_series) +
                                   ' s where s.id=:series',
                                   series = self.series):
                self.is_calibration = (q.id == q.calibration)
                self.calibration_series = q.calibration
            self.check_types()

    def check_types(self):
        sql = "select distinct roi.event_name from " + \
            self.db.table(database_series_probe) + " p join " + \
            self.db.table(database_table_roi) + " roi on roi.experiment_id = p.probe " + \
            "where p.series=:series and roi.type = 'signal'"
        types = [q.event_name for q in self.db.query(sql, series=self.series)]
        for t in types:
            if t not in self.list_analyzers():
                self.add_analyzer(t, AnalyzerHPLCOverallOneType(self.db, self.series, t, self.is_calibration, self.calibration_series))
        for t in self.list_analyzers():
            if t not in types:
                self.remove_analyzer(t)

    def update(self):
        if not self.db.read_only:
            self.check_types()
            AnalyzerCompose.update(self)


#####################
#### ModuleAPI ######

def analyzer(database, data):
    if data.type != 'HPLC AIA':
        return None, None, None

    Analyzer = {
        'signal': AnalyzerHPLCPeaks,
        'baseline': AnalyzerHPLCBaseline
    }

    a = AnalyzerHPLCOverall(database, data)
    overall = { 'signal': a }
    stats = [ a ]

    return Analyzer, overall, stats

def database_schema(db):
    AnalyzerHPLCPeaks.database_schema(db)
