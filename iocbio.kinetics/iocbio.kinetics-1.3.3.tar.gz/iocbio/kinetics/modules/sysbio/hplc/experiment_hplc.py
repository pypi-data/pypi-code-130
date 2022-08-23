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

import base64
import tempfile
import os

from iocbio.kinetics.handler.experiment_generic import ExperimentGeneric
from iocbio.kinetics.constants import database_table_experiment

### Module flag
IocbioKineticsModule = ['args', 'database_schema', 'database_info', 'database_processor']

### Implementation

class ExperimentHPLC(ExperimentGeneric):
    """General description of experiment performed on HPLC"""

    database_table = "hplc"

    @staticmethod
    def database_schema(db):
        db.query("CREATE TABLE IF NOT EXISTS " + db.table(ExperimentHPLC.database_table) +
                 "(experiment_id text PRIMARY KEY, experiment_title text, " +
                 "sample_name text, sample_id text, detector_name text, " +
                 "bdata text, " +
                 "FOREIGN KEY (experiment_id) REFERENCES " + db.table(database_table_experiment) + "(experiment_id) ON DELETE CASCADE" +
                 ")")

    @staticmethod
    def get_data(db, experiment_id):
        for q in db.query('SELECT bdata FROM ' + db.table(ExperimentHPLC.database_table) +
                          ' WHERE experiment_id=:eid', eid = experiment_id):
            b = base64.b64decode(q.bdata)
            f, fname = tempfile.mkstemp()
            f = os.fdopen(f, mode='wb')
            f.write(b)
            f.close()
            return fname
        return None

    @staticmethod
    def store(database, data):
        ExperimentGeneric.database_schema(database)
        ExperimentHPLC.database_schema(database)

        experiment_id = data.experiment_id

        ExperimentGeneric.store(database, experiment_id, time=data.time,
                                type_generic=data.type_generic,
                                type_specific=data.type, hardware="HPLC AIA")

        if not database.has_record(ExperimentHPLC.database_table,
                                   experiment_id = experiment_id):
            database.query("INSERT INTO " + database.table(ExperimentHPLC.database_table) +
                           "(experiment_id, experiment_title, sample_name, sample_id, detector_name, bdata) " +
                           "VALUES(:experiment_id,:title,:sname,:sid,:detect,:bdata)",
                           experiment_id=experiment_id,
                           title=data.config.experiment_title,
                           sname=data.config.sample_name,
                           sid=data.config.sample_id,
                           detect=data.config.detector_name,
                           bdata = base64.b64encode(data.bindata).decode('utf-8'))


def database_info(database):
    return "SELECT experiment_title || ' / ' || sample_name || ' / ' || sample_id as title " + \
        "from %s s where s.experiment_id=e.experiment_id" % database.table(ExperimentHPLC.database_table)

def database_schema(db):
    ExperimentHPLC.database_schema(db)

def args(parser):
    parser.add(name='hplc_series_id', help='HPLC: ID of the measurement series')
    parser.add(name='hplc_probe_name', help='HPLC: Probe name')
    parser.add(name='hplc_no_regions', help='HPLC: Set to 1 to skip importing regions defined in the experimental file')
    return ''

def database_process(database, data, args):
    if args.hplc_series_id is not None and data is not None:
        if database.read_only:
            print('Cannot set HPLC record data. Add --rw to program options')
        else:
            database_table = database.table("hplc_series_probe")
            name = args.hplc_probe_name if args.hplc_probe_name is not None else ''
            database.query("INSERT INTO " + database_table +
                           " (series, probe, name) " +
                           "VALUES(:series, :experiment, :name)",
                           series = args.hplc_series_id,
                           experiment = data.experiment_id,
                           name = name)
