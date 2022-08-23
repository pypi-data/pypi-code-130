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
eoDR file name definition.

"""

import copy
import os
from datetime import datetime
from collections import OrderedDict


from geopathfinder.file_naming import SmartFilename


class EODRFilename(SmartFilename):

    """
    eoDataReaders file name definition using SmartFilename class.
    """

    fields_def = OrderedDict([
        ('counter', {'len': 5}),
        ('id', {'len': 12}),
        ('dt_1', {'len': 15}),
        ('dt_2', {'len': 15}),
        ('file_num', {}),
        ('band', {})
    ])
    pad = "-"
    delimiter = "_"

    def __init__(self, fields, ext='.vrt', convert=False, compact=False):
        """
        Constructor of eoDRFilename class.

        Parameters
        ----------
        fields: dict
            Dictionary specifying the different parts of the filename.
        ext: str, optional
            Extension of the filename (default is '.vrt' for GDAL VRT files)
        convert: bool, optional
            If true, decoding is applied to parts of the filename, where such an operation is available (default is False).
        """
        self.dt_format = "%Y%m%dT%H%M%S"

        fields_def_ext = copy.deepcopy(EODRFilename.fields_def)
        fields_def_ext['counter']['decoder'] = lambda x: self.decode_counter(x)
        fields_def_ext['counter']['encoder'] = lambda x: self.encode_counter(x)
        fields_def_ext['dt_1']['decoder'] = lambda x: self.decode_datetime(x)
        fields_def_ext['dt_1']['encoder'] = lambda x: self.encode_datetime(x)
        fields_def_ext['dt_2']['decoder'] = lambda x: self.decode_datetime(x)
        fields_def_ext['dt_2']['encoder'] = lambda x: self.encode_datetime(x)
        fields_def_ext['file_num']['decoder'] = lambda x: int(x)
        fields_def_ext['file_num']['encoder'] = lambda x: str(x)
        fields_def_ext['band']['encoder'] = lambda x: str(x)

        fields_def_keys = list(fields_def_ext.keys())
        for key in fields.keys():
            if key not in fields_def_keys:
                fields_def_ext[key] = {}

        super(EODRFilename, self).__init__(fields, fields_def_ext, delimiter=EODRFilename.delimiter,
                                           pad=EODRFilename.pad, ext=ext, convert=convert, compact=compact)

    @classmethod
    def from_filename(cls, filename_str, convert=False, compact=False):
        """
        Converts a filename given as a string into an EODRFilename class object.

        Parameters
        ----------
        filename_str : str
            Filename without any paths (e.g., "00001_123456------_20181220T232333_---------------_2_B5_34_aug.vrt").
        convert: bool, optional
            If true, decoding is applied to parts of the filename, where such an operation is available (default is False).

        Returns
        -------
        EODRFilename
            Class representing an EODR filename.
        """

        fn_parts = os.path.splitext(os.path.basename(filename_str))[0].split(EODRFilename.delimiter)
        fields_def_ext = copy.deepcopy(EODRFilename.fields_def)
        fields_def_ext['file_num']['len'] = len(fn_parts[4])
        fields_def_ext['band']['len'] = len(fn_parts[5])  # get length of the band in the filename
        # if the filename consists of more than 4 parts, additional "dimensions" are added to the fields dictionary
        if len(fn_parts) > 6:
            for i, fn_part in enumerate(fn_parts[6:]):
                key = 'd' + str(i + 1)
                fields_def_ext[key] = {'len': len(fn_part)}

        return super().from_filename(filename_str, fields_def_ext, pad=EODRFilename.pad,
                                     delimiter=EODRFilename.delimiter, convert=convert, compact=compact)

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
            if "-" not in self['dt_1']:
                return self.decode_datetime(self['dt_1'])
            else:
                return None
        except TypeError:
            return None

    @property
    def etime(self):
        """"
        End time.

        Returns
        -------
        datetime.datetime
            End time.
        """
        try:
            if "-" not in self['dt_2']:
                return self.decode_datetime(self['dt_2'])
            else:
                return None
        except TypeError:
            return None

    def decode_datetime(self, string):
        """
        Decodes a string into a datetime object. The format is given by the class.

        Parameters
        ----------
        string: str, object
            String needed to be decoded to a datetime object.

        Returns
        -------
        datetime.datetime, object
            Original object or datetime object parsed from the given string.
        """
        if isinstance(string, str):
            return datetime.strptime(string, self.dt_format)
        else:
            return string

    def encode_datetime(self, time_obj):
        """
        Encodes a datetime object into a string. The format is given by the class.

        Parameters
        ----------
        time_obj: datetime.datetime, object
            Datetime object needed to be encoded to a string.

        Returns
        -------
        str, object
            Original object or str object parsed from the given datetime object.
        """
        if isinstance(time_obj, datetime):
            return time_obj.strftime(self.dt_format)
        else:
            return time_obj

    def decode_counter(self, string):
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

    def encode_counter(self, file_counter):
        """
        Encodes a file counter into a string.

        Parameters
        ----------
        file_counter: int
            Integer needed to be encoded to a string.

        Returns
        -------
        str, object
            Original object or str object parsed from the given integer.
        """

        if isinstance(file_counter, int):
            return "{:05d}".format(file_counter)
        else:
            return file_counter

if __name__ == '__main__':
    pass
