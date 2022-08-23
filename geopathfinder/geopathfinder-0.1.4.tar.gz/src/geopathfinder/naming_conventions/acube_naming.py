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
ACube file name definition.

"""

import copy

import datetime as dt
from datetime import datetime
from collections import OrderedDict
from geopathfinder.file_naming import SmartFilename


class ACubeFilename(SmartFilename):

    """
    ACube file name definition using SmartFilename class.
    """

    fields_def = OrderedDict([
        ('var_name', {'len': 9}),
        ('algorithm', {'len': 7}),
        ('sat_name', {'len': 3}),
        ('product', {'len': 7, 'delim': ''}),
        ('pol', {'len': 2, 'delim': ''}),
        ('direction', {'len': 1}),
        ('dtime_1', {'len': 8}),
        ('dtime_2', {'len': 8}),
        ('grid_name', {'len': 6}),
        ('tile_name', {'len': 10})])
    pad = "-"
    delimiter = "_"

    def __init__(self, fields, ext=".tif", convert=False, compact=False):
        """
        Constructor of ACube Filename class.

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

        fields_def_ext = copy.deepcopy(ACubeFilename.fields_def)
        fields_def_ext['dtime_1']['decoder'] = lambda x: self.decode_date(x)
        fields_def_ext['dtime_1']['encoder'] = lambda x: self.encode_date(x)
        fields_def_ext['dtime_2']['decoder'] = lambda x: self.decode_time(x)
        fields_def_ext['dtime_2']['encoder'] = lambda x: self.encode_time(x)

        super(ACubeFilename, self).__init__(fields, fields_def_ext, ext=ext, pad=ACubeFilename.pad,
                                            delimiter=ACubeFilename.delimiter, convert=convert, compact=compact)

    @classmethod
    def from_filename(cls, filename_str, convert=False, compact=False):
        """
        Converts a filename given as a string into an ACubeFilename class object.

        Parameters
        ----------
        filename_str : str
            Filename without any paths (e.g., "SIG0-----_SGRTA01_S1A_IWGRDH1VHD_20160126_054245--_EU010M_E043N016T1.tif").
        convert: bool, optional
            If true, decoding is applied to parts of the filename, where such an operation is available (default is False).

        Returns
        -------
        ACubeFilename
            Class representing an ACube file name.
        """

        return super().from_filename(filename_str, ACubeFilename.fields_def, pad=ACubeFilename.pad,
                                     delimiter=ACubeFilename.delimiter, convert=convert, compact=compact)

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

if __name__ == '__main__':
    pass
