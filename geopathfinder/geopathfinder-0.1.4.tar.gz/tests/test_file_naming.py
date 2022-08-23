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

import unittest
from collections import OrderedDict

from geopathfinder.file_naming import SmartFilename


def decode_int(string):
    if isinstance(string, str):
        return int(string)
    else:
        return string


def encode_int(num):
    if isinstance(num, int):
        return str(num)
    else:
        return num


class TestSmartFilename(unittest.TestCase):

    def setUp(self):
        self.fields_def = OrderedDict([('pflag', {'len': 1}),
                                       ('dtime_1', {'len': 14})])

    def test_build_filename_wihout_ext(self):
        """
        Test building file naming without extension.
        """
        fields = {'pflag': 'M', 'dtime_1': '20180101120000'}
        smrtf = SmartFilename(fields, self.fields_def)

        self.assertEqual(str(smrtf), 'M_20180101120000')

    def test_build_filename_with_ext(self):
        """
        Test building file naming with extension.
        """
        fields = {'pflag': 'M', 'dtime_1': '20180101120000'}
        smrtf = SmartFilename(fields, self.fields_def, ext='.tif')

        self.assertEqual(str(smrtf), 'M_20180101120000.tif')

    def test_init_undefined_field(self):
        """
        Test initialization with undefined field name.
        """
        fields = {'pflag': 'M', 'test_time': '20180101120000'}

        with self.assertRaises(KeyError):
            SmartFilename(fields, self.fields_def, ext='.tif')

    def test_init_wrong_field_length(self):
        """
        Test initialization with wrong field length.
        """
        fields = {'pflag': 'ME'}

        with self.assertRaises(ValueError):
            SmartFilename(fields, self.fields_def, ext='.tif')

    def test_set_nonexisting_fields(self):
        """
        Test setting field which is non-existing in definition.
        """
        fields = {'pflag': 'M', 'dtime_1': '20180101120000'}
        smrtf = SmartFilename(fields, self.fields_def, ext='.tif')

        with self.assertRaises(KeyError):
            smrtf['new_field'] = 'test'

    def test_set_wrong_fields_len(self):
        """
        Test setting field with wrong length.
        """
        fields = {'pflag': 'M', 'dtime_1': '20180101120000'}
        smrtf = SmartFilename(fields, self.fields_def, ext='.tif')

        with self.assertRaises(ValueError):
            smrtf['pflag'] = 'MM'

    def test_set_and_get_fields(self):
        """
        Test set and get file name fields.
        """
        fields = {'pflag': 'M', 'dtime_1': '20180101120000'}
        smrtf = SmartFilename(fields, self.fields_def, ext='.tif')

        self.assertEqual(smrtf['pflag'], 'M')
        self.assertEqual(smrtf['dtime_1'], '20180101120000')

        smrtf['pflag'] = 'D'
        smrtf['dtime_1'] = '20180101130000'

        self.assertEqual(smrtf['pflag'], 'D')
        self.assertEqual(smrtf['dtime_1'], '20180101130000')

    def test_variable_length_fields(self):
        """
        Test if required delimiter for field with variable length is detected.
        """
        self.fields_def.update({'variable': {'len': 0, 'delim': ''}})

        fields = {'pflag': 'M', 'dtime_1': '20180101120000'}
        with self.assertRaises(ValueError):
            smrtf = SmartFilename(fields, self.fields_def)

        fn = 'M_20180101120000.tif'
        with self.assertRaises(ValueError):
            smrtf = SmartFilename.from_filename(fn, self.fields_def)

    def test_zero_entries(self):
        fields_def = OrderedDict([('text', {'len': 0}), ('empty', {'len': 0}), ('number', {'len': 6,
                                                                                           'decoder': decode_int,
                                                                                           'encoder': encode_int
                                                                                           })])
        fields = {'text': 'testfilename', 'number': 0}
        smrtf = SmartFilename(fields, fields_def, ext='.tif', compact=True)
        self.assertEqual(str(smrtf), 'testfilename__0.tif')
        smrtf_fn = SmartFilename.from_filename('fromfilename__0.tif', fields_def=fields_def, compact=True, convert=True)
        self.assertEqual(smrtf_fn['number'], 0)


if __name__ == '__main__':
    unittest.main()
