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
import netCDF4
import numpy as np
import dateutil.parser
import os

from attrdict import AttrDict

from iocbio.kinetics.io.data import Data, Carrier
from .experiment_hplc import ExperimentHPLC

### Required definition for exported module ###
IocbioKineticsModule = ['reader']

def create_data(database, experiment_id=None, args=None):
    from iocbio.kinetics.handler.experiment_generic import ExperimentGeneric

    filename=getattr(args, "file_name", None)
    tmp_fname=None
    protocol=getattr(args, "protocol", None)
    if args is not None and args.hplc_no_regions is not None and int(args.hplc_no_regions):
        regions_import = False
    else:
        regions_import = True

    if experiment_id is not None:
        tmp_fname = ExperimentHPLC.get_data(database, experiment_id)

    if tmp_fname is not None:
        filename = tmp_fname
    elif filename is None or not filename.endswith(".cdf"):
        return None

    with open(filename, 'rb', buffering=0) as f:
        bdata = f.read()

    if experiment_id is None:
        experiment_id = hashlib.sha256(bdata).hexdigest()

    # do not import regions if we have dataset defined already in the database
    if ExperimentGeneric.has_record(database, experiment_id):
        regions_import = False

    with netCDF4.Dataset(filename, 'r') as f:
        var_names = set(f.variables.keys())
        # check that it has expected input
        if not {'aia_template_revision'}.issubset(set(f.ncattrs())) or \
           not {'actual_sampling_interval',
                'ordinate_values'}.issubset(var_names):
            return None

        detector_unit = f.detector_unit
        detector_name = f.detector_name
        retention_unit = f.retention_unit
        actual_sampling_interval = float(f['actual_sampling_interval'].getValue())
        values = np.array(list(f['ordinate_values']), dtype=float)
        if regions_import:
            peak_start_time = np.array(list(f['peak_start_time']), dtype=float) if 'peak_start_time' in var_names else []
            peak_end_time = np.array(list(f['peak_end_time']), dtype=float) if 'peak_end_time' in var_names else []
        else:
            peak_start_time, peak_end_time = [], []
        tstamp = dateutil.parser.parse(f.injection_date_time_stamp).strftime('%Y.%m.%d %H:%M:%S')

        # check that we use correct detector
        if not detector_name.startswith('DAD1 F, Sig=260,4'):
            print('HPLC reader: looks like this has wrong detector:', f.detector_name)
            return None

        config = AttrDict( peak_start_time = peak_start_time,
                           peak_end_time = peak_end_time,
                           experiment_title = f.experiment_title,
                           sample_name = f.sample_name,
                           sample_id = f.sample_id,
                           detector_name = detector_name,
                           events = {}
                          )

        t = np.arange(len(values)) * actual_sampling_interval

        dd = { 'signal': dict( x = t,
                               y = Carrier( detector_name, detector_unit, values ) ) }

        data = Data( experiment_id,
                     config = config,
                     type = 'HPLC AIA',
                     type_generic = 'HPLC',
                     time = tstamp,
                     name = f.experiment_title + " / " + f.sample_name + " / " + f.sample_id,
                     xname = 'Time', xunit = retention_unit,
                     xlim = (t[0], t[-1]),
                     data = dd
                    )
        data.bindata = bdata

    if not ExperimentGeneric.has_record(database, data.experiment_id):
        database.set_read_only(False)
        ExperimentHPLC.store(database, data)

    print(data)

    if tmp_fname is not None:
        os.remove(tmp_fname)
        print('Removed tmp file', tmp_fname)

    return data

