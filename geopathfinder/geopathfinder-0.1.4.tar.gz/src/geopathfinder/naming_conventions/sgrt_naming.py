# Copyright (c) 2018, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
SGRT folder and file name definition.

"""

import os
import copy

import datetime as dt
from datetime import datetime
from collections import OrderedDict

from geopathfinder.folder_naming import build_smarttree
from geopathfinder.folder_naming import create_smartpath
from geopathfinder.file_naming import SmartFilename


# Please add here new sensors if they follow the SGRT naming convention.
allowed_sensor_dirs = ['Sentinel-1_CSAR',
                       'SCATSAR',
                       'METOP_ASCAT',
                       'Envisat_ASAR']


class SgrtFilename(SmartFilename):

    """
    SGRT file name definition using SmartFilename class.
    """

    fields_def = OrderedDict([
        ('pflag', {'len': 1, 'delim': ''}),
        ('dtime_1', {'len': 8}),
        ('dtime_2', {'len': 8}),
        ('var_name', {'len': 9}),
        ('mission_id', {'len': 2, 'delim': ''}),
        ('spacecraft_id', {'len': 1, 'delim': ''}),
        ('mode_id', {'len': 2, 'delim': ''}),
        ('product_type', {'len': 3, 'delim': ''}),
        ('res_class', {'len': 1, 'delim': ''}),
        ('level', {'len': 1, 'delim': ''}),
        ('pol', {'len': 2, 'delim': ''}),
        ('orbit_direction', {'len': 1}),
        ('relative_orbit', {'len': 3}),
        ('workflow_id', {'len': 5}),
        ('grid_name', {'len': 6}),
        ('tile_name', {'len': 10})
    ])
    pad = "-"
    delimiter = "_"

    def __init__(self, fields, ext=".tif", convert=False, compact=False):
        """
        Constructor of SgrtFilename class.

        Parameters
        ----------
        fields: dict
            Dictionary specifying the different parts of the filename.
        convert: bool, optional
            If true, decoding is applied to parts of the filename, where such an operation is available (default is False).
        """

        self.date_format = "%Y%m%d"
        self.time_format = "%H%M%S"
        fields = fields.copy()

        if 'dtime_2' not in fields.keys():
            self.single_date = True
            apply_dtime_2 = False
        else:
            self.single_date = False
            apply_dtime_2 = True

            if isinstance(fields['dtime_2'], str):
                if fields['dtime_2'].endswith('--'):
                    self.single_date = True
            else:
                if isinstance(fields['dtime_2'], dt.time) or (fields['dtime_2'].year < 1950):
                    self.single_date = True

        if 'dtime_1' in fields.keys():
            if self.single_date:
                date = self.encode_date(fields['dtime_1'])
                if apply_dtime_2:
                    time = self.encode_time(fields['dtime_2'])
                else:
                    time = self.encode_time(fields['dtime_1'])
                fields['dtime_1'] = date
                fields['dtime_2'] = time
            else:
                fields['dtime_1'] = self.encode_date(fields['dtime_1'])
                fields['dtime_2'] = self.encode_date(fields['dtime_2'])

        fields_def_ext = copy.deepcopy(SgrtFilename.fields_def)
        fields_def_ext['dtime_1']['decoder'] = lambda x: self.decode_date(x)
        fields_def_ext['dtime_1']['encoder'] = lambda x: self.encode_date(x)
        fields_def_ext['dtime_2']['decoder'] = lambda x: self.decode_time(x)
        fields_def_ext['dtime_2']['encoder'] = lambda x: self.encode_time(x)
        fields_def_ext['relative_orbit']['decoder'] = lambda x: self.decode_rel_orbit(x)
        fields_def_ext['relative_orbit']['encoder'] = lambda x: self.encode_rel_orbit(x)

        super(SgrtFilename, self).__init__(fields, fields_def_ext, ext=ext, pad=SgrtFilename.pad,
                                           delimiter=SgrtFilename.delimiter, convert=convert, compact=compact)

    @classmethod
    def from_filename(cls, filename_str, convert=False, compact=False):
        """
        Converts a filename given as a string into an SgrtFilename class object.

        Parameters
        ----------
        filename_str : str
            Filename without any paths (e.g., "M20170725_165004--_SIG0-----_S1BIWGRDH1VVA_146_A0104_EU500M_E048N012T6.tif").
        convert: bool, optional
            If true, decoding is applied to parts of the filename, where such an operation is available (default is False).

        Returns
        -------
        SgrtFilename
            Class representing an SGRT filename.
        """

        return super().from_filename(filename_str, SgrtFilename.fields_def, pad=SgrtFilename.pad,
                                     delimiter=SgrtFilename.delimiter, convert=convert, compact=compact)

    @property
    def stime(self):
        """
        Start time.

        Returns
        -------
        datetime.datetime
            Start time.
        """
        try:
            return datetime.combine(self["dtime_1"], self["dtime_2"]) if self.single_date else self["dtime_1"]
        except TypeError:
            return None

    @property
    def etime(self):
        """
        End time.

        Returns
        -------
        datetime.datetime
            End time.
        """
        try:
            return datetime.combine(self["dtime_1"], self["dtime_2"]) if self.single_date else self["dtime_2"]
        except TypeError:
            return None

    @property
    def time(self):
        """
        Unified time.

        Returns
        -------
        datetime.datetime
            Unified time.
        """
        try:
            if self.single_date:
                return self.stime
            else:
                return self.stime + (self.etime - self.stime) / 2
        except TypeError:
            return None

    @property
    def product_id(self):
        """
        Builds product id from other filename attributes (e.g. 'S1AIWGRDH').

        Returns
        -------
        product_id: str
            Product id consisting of mission id (e.g., 'S1'), spacecraft id (e.g., 'A'), mode id (e.g., 'IW'),
            product type (e.g., 'GRD') and resolution class (e.g., 'H').
        """
        try:
            product_id = "".join([self["mission_id"], self["spacecraft_id"], self["mode_id"], self["product_type"], self["res_class"]])
        except TypeError:
            product_id = None

        return product_id

    @property
    def ftile(self):
        """
        Builds the full tile name from other filename attributes (e.g. 'EU010M_E048N015T1').

        Returns
        -------
        ftile: str
            Full tile name consisting of grid name (e.g., 'EU10M') and tile name (e.g., 'E048N015T1').
        """
        try:
            ftile = "_".join([self["grid_name"], self["tile_name"]])
        except TypeError:
            ftile = None
        return ftile

    def decode_date(self, string):
        """
        Decodes a string into a datetime.date object. The format is given by the class.

        Parameters
        ----------
        string: str, object
            String needed to be decoded to a datetime.date object.

        Returns
        -------
        datetime.date, object
            Original object or datetime.date object parsed from the given string.
        """
        if isinstance(string, str):
            return datetime.strptime(string, self.date_format).date()
        else:
            return string

    def decode_time(self, string):
        """
        Decodes a string into a datetime.time/datetime.date object. The format is given by the class and the conversion
        follows the 'single_date' setting.

        Parameters
        ----------
        string: str, object
            String needed to be decoded to a datetime.time/datetime.date object.

        Returns
        -------
        datetime.date, datetime.time, object
            Original object, datetime.date or datetime.time object parsed from the given string.
        """
        if isinstance(string, str):
            if self.single_date:
                return datetime.time(datetime.strptime(string, self.time_format))
            else:
                return self.decode_date(string)
        else:
            return string

    def decode_rel_orbit(self, string):
        """
        Decodes a string into an integer.

        Parameters
        ----------
        string: str, object
            String needed to be decoded to an integer.

        Returns
        -------
        int, object
            Original object or integer object parsed from the given string.
        """
        if isinstance(string, str):
            return int(string)
        else:
            return string

    def encode_date(self, time_obj):
        """
        Encodes a datetime.datetime/datetime.date object into a string. The format is given by the class.

        Parameters
        ----------
        time_obj: datetime.datetime, datetime.date or object
            Datetime object needed to be encoded to a string.

        Returns
        -------
        str, object
            Original object or str object parsed from the given datetime object.
        """
        if isinstance(time_obj, (dt.datetime, dt.date, dt.time)):
            return time_obj.strftime(self.date_format)
        else:
            return time_obj

    def encode_time(self, time_obj):
        """
        Encodes a datetime.datetime/datetime.date object into a string. The format is given by the class.

        Parameters
        ----------
        time_obj: datetime.datetime, datetime.date or object
            Datetime object needed to be encoded to a string.

        Returns
        -------
        str, object
            Original object or str object parsed from the given datetime object.
        """
        if isinstance(time_obj, (dt.datetime, dt.time, dt.date)):
            if self.single_date:
                return time_obj.strftime(self.time_format)
            else:
                return time_obj.strftime(self.date_format)
        else:
            return time_obj

    def encode_rel_orbit(self, relative_orbit):
        """
        Encodes a relative orbit number into a string.

        Parameters
        ----------
        relative_orbit: int or object
            Integer needed to be encoded to a string.

        Returns
        -------
        str, object
            Original object or str object parsed from the given integer.
        """
        if isinstance(relative_orbit, int):
            return "{:03d}".format(relative_orbit)
        else:
            return relative_orbit


def sgrt_path(root, mode=None, group=None, datalog=None,
              product=None, wflow=None, grid=None, tile=None, var=None,
              qlook=True, make_dir=False):
    """
    Realisation of the full SGRT folder naming convention, yielding a single
    SmartPath.

    Parameters
    ----------
    root : str
        root directory of the path. must contain satellite sensor at toplevel.
        e.g. "R:\Datapool_processed\Sentinel-1_CSAR"
    mode : str
        e.g "IWGRDH"
    group : str, optional
        "preprocessed" or "parameters" or "products"
    datalog : str, optional
        must be "datasets" or "logfiles"
    product : str
        e.g. "ssm"
    wflow : str
        e.g. "C1003"
    grid : str
        e.g. "EQUI7_EU500M"
    tile : str
        e.g. "E048N012T6"
    var : str
        e.g. "ssm"
    qlook : bool
        if the quicklook subdir should be integrated
    make_dir : bool
        if the directory should be created on the filesystem

    Returns
    -------
    SmartPath
        Object for the path
    """

    # check the sensor folder name
    if root.split(os.sep)[-1] not in allowed_sensor_dirs:
        raise ValueError('Wrong input for "root"!')

    # define the datalog folder name
    if datalog is None:
        if isinstance(wflow, str):
            datalog = 'datasets'
    elif datalog == 'logfiles':
        product = None
        wflow = None
        grid = None
        tile = None
        var = None
        qlook = False
    elif datalog == 'datasets':
        pass
    else:
        raise ValueError('Wrong input for "datalog" level!')


    # define the group folder name
    if group is None:
        if wflow.startswith('A'):
            group = 'preprocessed'
        elif wflow.startswith('B'):
            group = 'parameters'
        elif wflow.startswith('C'):
            group = 'products'
        else:
            raise ValueError('Wrong input for "wflow" level!')


    # defining the folder levels
    levels = [mode, group,
              datalog, product, wflow, grid,
              tile,  var, 'qlooks']

    # defining the hierarchy
    hierarchy = ['mode', 'group',
                 'datalog', 'product', 'wflow', 'grid',
                 'tile', 'var', 'qlook']

    if qlook is False:
        levels.remove('qlooks')
        hierarchy.remove('qlook')

    return create_smartpath(root, hierarchy=hierarchy, levels=levels,
                     make_dir=make_dir)


def sgrt_tree(root, target_level=None, register_file_pattern=None,
              subset_level=None, subset_pattern=None, subset_unique=False):

    """
    Realisation of the full SGRT folder naming convention, yielding a
    SmartTree(), reflecting all subfolders as SmartPath()

    Parameters
    ----------
    root : str
        top level directory of the SGRT dataset, which is the sensor name in
        the SGRT naming convention.
        E.g.: "R:\Datapool_processed\Sentinel-1_CSAR"
    target_level : str, optional
        Can speed up things: Level name of target tree-depth.
        The SmartTree is only built from directories reaching this level,
        and only built down to this level. If not set, all directories are
        built down to deepest depth.
    register_file_pattern : str tuple, optional
        strings defining search pattern for file search for file_register
        e.g. ('C1003', 'E048N012T6').
        No asterisk is needed ('*')!
        Sequence of strings in given tuple is crucial!
        Be careful: If the tree is large, this can take a while!
    subset_level : str tuple, optional
        Name of level in tree's hierarchy where the subset should be applied
        e.g. ('tile').
        Default level is ('grid')
    subset_pattern : str tuple, optional
        Strings defining search pattern for subset_level, meaning only paths
        matching this pattern at "subset_level" will be included in the SmartTree().
        Default pattern is ('EQUI7').
        e.g. ('EQUI7', '500M'), or ('500M'). No asterisk is needed ('*')!
        Sequence of strings in given tuple is crucial!
    subset_unique : bool, optional
        defines of the subset will deliver...
            True: just one single subtree that matches uniquely the subset_pattern,
                  and which is rebased to the subset_level.
            False: all subtrees that match the subset_pattern (Default).

    Returns
    -------
    SmartTree
        Object for the SGRT tree.
    """

    # defining the hierarchy
    hierarchy = ['mode', 'group','datalog',
                 'product', 'wflow', 'grid',
                 'tile', 'var', 'qlook']

    # Check for allowed directory topnames for "root".
    if root.split(os.sep)[-1] in allowed_sensor_dirs:
        sgrt_tree = build_smarttree(root, hierarchy,
                                    target_level=target_level,
                                    register_file_pattern=register_file_pattern)
    else:
        raise ValueError('Root-directory "{}" does is '
                         'not a valid SGRT folder!'.format(root))

    # limit the tree to a subtree with all paths that match the subset_pattern at subset_level
    if subset_level is not None and not subset_unique:
        sgrt_tree = sgrt_tree.get_subtree_matching(subset_level, subset_pattern,
                                                   register_file_pattern=register_file_pattern)

    # limit the tree to a single, unique, small subtree that matches the subset_pattern at subset_level,
    # which is re-rooted to that level.
    elif subset_level is not None:
        sgrt_tree = sgrt_tree.get_subtree_unique_rebased(subset_level, subset_pattern,
                                                         register_file_pattern=register_file_pattern)

    return sgrt_tree


if __name__ == '__main__':
    pass
