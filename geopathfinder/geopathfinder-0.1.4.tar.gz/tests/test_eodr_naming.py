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

import logging
import unittest
from datetime import datetime

from geopathfinder.naming_conventions.eodr_naming import EODRFilename

logging.basicConfig(level=logging.INFO)


class TestEODRFilename(unittest.TestCase):

    def setUp(self):
        self.file_counter = 1
        self.id_1 = "123456"
        self.id_2 = "654321"
        self.dt_1 = datetime(2008, 1, 1, 12, 23, 33)
        self.dt_2 = datetime(2009, 2, 2, 22, 1, 1)
        self.file_num = 2

        fields_1 = {'counter': self.file_counter, 'id': self.id_1, 'dt_1': self.dt_1, 'file_num': self.file_num,
                    'band': 'B1'}

        self.eodr_fn_1 = EODRFilename(fields_1, convert=True)

        fields_2 = {'counter': self.file_counter, 'id': self.id_2, 'dt_1':  self.dt_1, 'dt_2': self.dt_2,
                    'file_num': self.file_num, 'band': 'B12', 'd1': '45'}

        self.eodr_fn_2 = EODRFilename(fields_2, convert=True)

        fn = '00303_123456------_20181220T232333_---------------_544_B5_34_aug.vrt'
        self.eodr_fn_3 = EODRFilename.from_filename(fn, convert=True)

        self.eodr_fn_4 = EODRFilename.from_filename(fn)

    def test_build_eodr_filename(self):
        """
        Test building SGRT file name.

        """
        fn = ('00001_123456------_20080101T122333_---------------_2_B1.vrt')

        self.assertEqual(str(self.eodr_fn_1), fn)

    def test_get_n_set_date(self):
        """
        Test set and get start and end date.

        """
        self.assertEqual(self.eodr_fn_2['dt_1'].date(), self.dt_1.date())
        self.assertEqual(self.eodr_fn_2['dt_2'].date(), self.dt_2.date())

        new_start_time = datetime(2009, 1, 1, 12, 23, 33)
        self.eodr_fn_2['dt_1'] = new_start_time

        self.assertEqual(self.eodr_fn_2['dt_1'].date(), new_start_time.date())

    def test_create_eodr_filename(self):
        """
        Tests the creation of a SmartFilename from a given string filename.

        """

        # testing for decoded types
        self.assertEqual(self.eodr_fn_3['counter'], 303)
        self.assertEqual(self.eodr_fn_3['id'], '123456')
        self.assertEqual(self.eodr_fn_3['dt_1'], datetime(2018, 12, 20, 23, 23, 33))
        self.assertEqual(self.eodr_fn_3['dt_2'], None)
        self.assertEqual(self.eodr_fn_3['file_num'], 544)
        self.assertEqual(self.eodr_fn_3['band'], 'B5')
        self.assertEqual(self.eodr_fn_3['d1'], '34')
        self.assertEqual(self.eodr_fn_3['d2'], 'aug')
        self.assertEqual(self.eodr_fn_3.ext, '.vrt')

        # testing for string types
        self.assertEqual(self.eodr_fn_4['counter'], '00303')
        self.assertEqual(self.eodr_fn_4['id'], '123456')
        self.assertEqual(self.eodr_fn_4['dt_1'], '20181220T232333')
        self.assertEqual(self.eodr_fn_4['dt_2'], '')
        self.assertEqual(self.eodr_fn_4['file_num'], '544')
        self.assertEqual(self.eodr_fn_4['band'], 'B5')
        self.assertEqual(self.eodr_fn_4['d1'], '34')
        self.assertEqual(self.eodr_fn_4['d2'], 'aug')
        self.assertEqual(self.eodr_fn_4.ext, '.vrt')


if __name__ == "__main__":
    unittest.main()
