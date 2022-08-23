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
import PyQt5.QtCore

from scipy.interpolate import interp1d

from .mean_med_std import AnalyzerMeanMedStdDB, AnalyzerMeanMedStd
from .generic import AnalyzerGenericSignals, AnalyzerGeneric, XYData, Stats
from iocbio.kinetics.constants import database_table_roi
from PyQt5.QtCore import pyqtSignal

# signal used to communicate between baseline and peakarea objects
baselineSignal = AnalyzerGenericSignals()

class AnalyzerBaseline(AnalyzerMeanMedStd):
    """Baseline estimator used by AnalyzerPeakAreaDB

    This class is used in combination with AnalyzerPeakAreaDB to
    estimate area of the peak under the measurements. See
    AnalyzerPeakAreaDB for details.

    Parameters
    ----------
    database : iocbio.kinetics.io.db.DatabaseInterface
      Database access
    data : iocbio.kinetics.io.data.Data
      Data descriptor
    channel : str
      Name of the channel to use when accessing the data as in
      self.data.x(channel)
    peaks_id : str
      Unique ID matching peaks_id used by corresponding AnalyzerPeakAreaDB.

    """

    database_table = 'peakarea_baseline'

    _baseline = {}
    _current_experiment = ''

    def __init__(self, database, data, channel, peaks_id):
        AnalyzerMeanMedStd.__init__(self, data.x(channel), data.y(channel).data)
        if AnalyzerBaseline._current_experiment != data.experiment_id:
            AnalyzerBaseline._baseline = {}
            AnalyzerBaseline._current_experiment = data.experiment_id
        self.data = data
        self.data_id = data.data_id        
        self.channel = channel
        self.peaks_id = peaks_id
        self.axisnames = XYData(data.xname, data.y(channel).name)
        self.axisunits = XYData(data.xunit, data.y(channel).unit)
        self.signals = AnalyzerGenericSignals()
        self.signals.sigUpdate.connect(baselineSignal.sigUpdate, type=PyQt5.QtCore.Qt.QueuedConnection)
        self.fit()

    def fit(self):
        AnalyzerMeanMedStd.fit(self)
        b = AnalyzerBaseline._baseline.get(self.peaks_id, {})
        if len(self.experiment.x) < 1:
            print('Empty baseline ROI detected, skipping changes')
            return
        if len(self.experiment.x) > 1:
            x = (self.experiment.x[0] + self.experiment.x[1])/2
        else:
            x = self.experiment.x[0]
        b[self.data_id] = [ x, self.stats['mean'].value ]
        AnalyzerBaseline._baseline[self.peaks_id] = b
        self.signals.sigUpdate.emit()

    def remove(self):
        b = AnalyzerBaseline._baseline.get(self.peaks_id, {})
        if self.data_id in b:
            del b[self.data_id]
        AnalyzerBaseline._baseline[self.peaks_id] = b
        self.signals.sigUpdate.emit()

    def update_data(self, data):
        """Updata data from current ROI"""
        AnalyzerMeanMedStd.update_data(self, data.x(self.channel), data.y(self.channel).data)
        self.fit()

    def update_event(self, event_name):
        pass

    @staticmethod
    def slice(data, x0, x1):
        sdata = data.slice(x0, x1)
        return sdata

    @staticmethod
    def auto_slicer(data):
        return []

    @staticmethod
    def baseline(peaks_id, x):
        b = [i for _, i in AnalyzerBaseline._baseline.get(peaks_id, {}).items()]
        if len(b) == 0:
            return 0.0*np.ones(x.shape)
        elif len(b) == 1:
            return 0.0*np.ones(x.shape) + b[0][1]
        b.sort()
        b = np.array(b)
        f = interp1d(b[:,0], b[:,1], fill_value="extrapolate")
        return f(x)


class AnalyzerPeakAreaDB(AnalyzerGeneric):
    """Analyzer calculating the area under the measured signal

    This analyzer allows to find area within region of interest after
    subtracting the baseline marked by regions of interest through
    AnalyzerBaseline. For that, corresponding peaks_id should match
    for AnalyzerBaseline and AnalyzerPeakAreaDB.

    Calculated areas are stored in the table `peakarea`.

    To use this analyzer, set the primary analyzers to include this
    and AnalyzerBaseline as primary for different ROI types. For
    example:

    Analyzer = {
        'signal': AnalyzerHPLCPeaks,
        'baseline': AnalyzerHPLCBaseline
    }

    where AnalyzerHPLCPeaks and AnalyzerHPLCBaseline are derived
    classes that specify data channel used in the analysis.

    During the fit, the analyzer calculates ares, adds it to the
    statistics shown to the user, and records it in the database. As a
    calculated fit, it shows baseline used for finding the area.

    Parameters
    ----------
    database : iocbio.kinetics.io.db.DatabaseInterface
      Database access
    data : iocbio.kinetics.io.data.Data
      Data descriptor
    channel : str
      Name of the channel to use when accessing the data as in
      self.data.x(channel)
    peaks_id : str
      Unique ID matching peaks_id used by corresponding AnalyzerBaseline.

    """

    database_table = 'peakarea'

    @staticmethod
    def database_schema(db):
        db.query("CREATE TABLE IF NOT EXISTS " + db.table(AnalyzerPeakAreaDB.database_table) +
                 "(data_id text not null PRIMARY KEY, " +
                 "area double precision not null, " +
                 "FOREIGN KEY (data_id) REFERENCES " + db.table(database_table_roi) + "(data_id) ON DELETE CASCADE)")


    def __init__(self, database, data, channel, peaks_id):
        AnalyzerPeakAreaDB.database_schema(database)
        AnalyzerGeneric.__init__(self, data.x(channel), data.y(channel).data)

        self.signals = AnalyzerGenericSignals()
        self.database = database
        self.data = data
        self.data_id = data.data_id
        self.axisnames = XYData(data.xname, data.y(channel).name)
        self.axisunits = XYData(data.xunit, data.y(channel).unit)
        self.channel = channel
        self.peaks_id = peaks_id

        baselineSignal.sigUpdate.connect(self.fit)
        self.fit()

    def fit(self):
        """Fit the experimental data and store the results in the database"""
        y = AnalyzerBaseline.baseline(self.peaks_id, self.experiment.x)
        self.calc = XYData(self.experiment.x, y) # show baseline on the plot
        area = float(np.trapz(self.experiment.y - y, x=self.experiment.x))
        self.stats["area"] = Stats("area", "%s x %s" % (self.axisunits.y, self.axisunits.x), area)

        c = self.database
        if c.has_record(self.database_table, data_id=self.data_id):
            c.query("UPDATE " + c.table(self.database_table) +
                    " SET area=:area WHERE data_id=:data_id",
                    area=self.stats['area'].value,
                    data_id=self.data_id)
        else:
            c.query("INSERT INTO " + c.table(self.database_table) +
                    "(data_id, area) VALUES(:data_id,:area)",
                    area=self.stats['area'].value,
                    data_id=self.data_id)

        self.signals.sigUpdate.emit()

    def remove(self):
        """Remove data from current ROI from the database"""
        c = self.database
        c.query("DELETE FROM " + self.database.table(self.database_table) +
                " WHERE data_id=:data_id",
                data_id=self.data.data_id)
        self.database = None # through errors if someone tries to do something after remove
        self.signals.sigUpdate.emit()

    def update_data(self, data):
        """Updata data from current ROI"""
        AnalyzerGeneric.update_data(self, data.x(self.channel), data.y(self.channel).data)
        self.fit()

    def update_event(self, event_name):
        self.data.event_name = event_name
        try:
            evalue = float(event_name)
        except:
            evalue = None
        self.data.event_value = evalue

    @staticmethod
    def slice(data, x0, x1):
        sdata = data.slice(x0, x1)
        return sdata

    @staticmethod
    def auto_slicer(data):
        return []
