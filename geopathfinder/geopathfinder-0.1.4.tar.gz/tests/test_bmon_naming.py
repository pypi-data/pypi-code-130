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

from geopathfinder.naming_conventions.bmon_naming import BMonFilename

logging.basicConfig(level=logging.INFO)


class TestBMonFilename(unittest.TestCase):

    def setUp(self):
        self.var_name = "BMON_DM_ENSEMBLE"
        self.sres = "500m"
        self.timestamp_1 = datetime(2016, 1, 1, 12)
        self.timestamp_2 = datetime(2017, 1, 1, 12)
        self.version = "v1"

        fields_1 = {'var_name': self.var_name, 'sres': self.sres, 'timestamp': self.timestamp_1,
                    'version': self.version}

        self.bmon_fn_1 = BMonFilename(fields_1, convert=True)

        fields_2 = {'var_name': self.var_name, 'sres': self.sres, 'timestamp': self.timestamp_2,
                    'version': self.version}

        self.bmon_fn_2 = BMonFilename(fields_2, convert=True)

        fn = "BMON_DM_ENSEMBLE_500m_20160101120000_v1.nc"
        self.bmon_fn_3 = BMonFilename.from_filename(fn, convert=True)

        self.bmon_fn_4 = BMonFilename.from_filename(fn, convert=False)

    def test_build_bmon_filename(self):
        """
        Test building SGRT file name.

        """
        fn = ("BMON_DM_ENSEMBLE_500m_20160101120000_v1.nc")

        self.assertEqual(str(self.bmon_fn_1), fn)

    def test_get_n_set_date(self):
        """
        Test set and get start and end date.

        """

        self.assertEqual(self.bmon_fn_2['timestamp'], self.timestamp_2)

        new_timestamp = datetime(2009, 1, 1, 12, 23, 33)
        self.bmon_fn_2['timestamp'] = new_timestamp

        self.assertEqual(self.bmon_fn_2['timestamp'], new_timestamp)

    def test_create_bmon_filename(self):
        """
        Tests the creation of a SmartFilename from a given string filename.

        """

        # testing for decoded types
        self.assertEqual(self.bmon_fn_3['var_name'], self.var_name)
        self.assertEqual(self.bmon_fn_3['sres'], '500m')
        self.assertEqual(self.bmon_fn_3['timestamp'], self.timestamp_1)
        self.assertEqual(self.bmon_fn_3['version'], 'v1')
        self.assertEqual(self.bmon_fn_3.ext, '.nc')

        # testing for string types
        self.assertEqual(self.bmon_fn_4['var_name'], self.var_name)
        self.assertEqual(self.bmon_fn_4['sres'], '500m')
        self.assertEqual(self.bmon_fn_4['timestamp'], '20160101120000')
        self.assertEqual(self.bmon_fn_4['version'], 'v1')
        self.assertEqual(self.bmon_fn_4.ext, '.nc')


if __name__ == "__main__":
    unittest.main()

