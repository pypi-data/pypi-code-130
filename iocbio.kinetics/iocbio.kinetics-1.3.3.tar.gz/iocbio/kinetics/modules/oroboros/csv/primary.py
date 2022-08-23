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

from iocbio.kinetics.calc.respiration import AnalyzerRespiration

IocbioKineticsModule = ["analyzer", "database_schema"]

# Module API
def analyzer(database, data):
    Analyzer = {}
    if data.type == "Oroboros 2K CSV experiment":
        # as a key, we define type of ROI used later in secondary analyzers as well
        Analyzer['default'] = AnalyzerRespiration
    # only primary analyzer is returned this time
    return Analyzer, None, None

def database_schema(db):
    AnalyzerRespiration.database_schema(db)
