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

import iocbio.db.db as iocdb


class DatabaseInterface(iocdb.DatabaseInterface):
    """Database interface and helper functions"""

    current_schema_version = "2"
    settings_compname = "iocbio"
    settings_appname = "kinetics"

    def __init__(self):
        iocdb.DatabaseInterface.__init__(self, self.settings_compname, self.settings_appname)

    def schema(self):
        """Check the present schema version, create if missing and return the version of current schema"""

        version = self.schema_version()
        if version is None:
            self.schema_set_version(DatabaseInterface.settings_appname, DatabaseInterface.current_schema_version)
            version = self.schema_version()

        if version == DatabaseInterface.current_schema_version:
            pass
        else:
            raise RuntimeError("This version (%s) of database schema is not supported" % version)

    @staticmethod
    def get_database():
        return iocdb.DatabaseInterface.get_database(DatabaseInterface.settings_compname, DatabaseInterface.settings_appname)

    @staticmethod
    def remove_login(username = None):
        """Remove all saved login information"""
        iocdb.DatabaseInterface.remove_login(DatabaseInterface.settings_compname, DatabaseInterface.settings_appname, username)

    @staticmethod
    def settings():
        return iocdb.DatabaseInterface.settings(DatabaseInterface.settings_compname, DatabaseInterface.settings_appname)
