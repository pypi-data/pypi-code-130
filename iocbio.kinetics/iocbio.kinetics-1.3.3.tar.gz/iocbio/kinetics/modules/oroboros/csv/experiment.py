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

from iocbio.kinetics.handler.experiment_generic import ExperimentGeneric
from iocbio.kinetics.constants import database_table_experiment

IocbioKineticsModule = ["database_info", "database_schema"]

class ExperimentO2k(ExperimentGeneric):
    
    database_table = "oroboros_csv"

    @staticmethod
    def database_schema(db):
        db.query("CREATE TABLE IF NOT EXISTS " + db.table(ExperimentO2k.database_table) +
                 "(experiment_id text PRIMARY KEY,"
                 " rawdata text,"
                 " filename text,"
                 " title text,"
                 " o2kchamber text,"
                 "name text,"
                 "date text," +
                 "FOREIGN KEY (experiment_id) REFERENCES " + db.table(database_table_experiment) + "(experiment_id) ON DELETE CASCADE" +
                 ")")

    def get_fulltxt(database, experiment_id):
        experiment_id = experiment_id
        if ExperimentGeneric.hardware(database, experiment_id) != "Oroboros 2K CSV":
            return None, None, None, None
        print("Loading raw data for experiment:", experiment_id)
        for q in database.query("SELECT rawdata, name, o2kchamber, date FROM " + database.table(ExperimentO2k.database_table) +
                                " WHERE experiment_id=:experiment_id",
                                experiment_id=experiment_id):
            return q.rawdata, q.name , q.o2kchamber, q.date
        return None, None, None, None

    def store(database, data, fulltxt, name, filename, date, o2kchamber):
        experiment_id = data.experiment_id

        ExperimentGeneric.store(database,experiment_id, time=data.time,
                                type_generic = data.type_generic,
                                type_specific = data.type, hardware= "Oroboros 2K CSV")

        c = database

        if not database.has_record(ExperimentO2k.database_table, experiment_id = experiment_id):
            c.query("INSERT INTO " + database.table(ExperimentO2k.database_table) +
                   "(experiment_id, rawdata, filename, name, title, date, o2kchamber) " +
                   "VALUES(:experiment_id,:ftxt,:finame, :fname,:exptitle,:exptime,:expchamber)",
                   experiment_id=experiment_id,
                   ftxt=fulltxt,
                   finame= filename,
                   fname= name,
                   exptitle="Oroboros 2K experiment",
                   exptime = date,
                   expchamber = o2kchamber )


# database info api
def database_info(database):
    return "SELECT name from %s s where s.experiment_id=e.experiment_id" % database.table(ExperimentO2k.database_table)

# definition of database_schema function
def database_schema(db):
    # just in case if our experiment is the first one, make general if needed
    ExperimentGeneric.database_schema(db)
    # create table for our experiment
    ExperimentO2k.database_schema(db)
