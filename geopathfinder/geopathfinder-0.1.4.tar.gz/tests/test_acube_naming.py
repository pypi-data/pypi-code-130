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


import os
import unittest
import logging
from datetime import datetime
from datetime import time

from geopathfinder.naming_conventions.acube_naming import ACubeFilename

logging.basicConfig(level=logging.INFO)


class TestACubeFilename(unittest.TestCase):

    def setUp(self):
        self.dtime_1 = datetime(2008, 1, 1, 12, 23, 33)
        self.dtime_2 = datetime(2009, 2, 2, 22, 1, 1)

        fields = {'dtime_1': self.dtime_1, 'dtime_2': self.dtime_2,
                  'var_name': 'SSM'}

        self.acube_fn = ACubeFilename(fields, convert=True)

        fields = {'dtime_1': self.dtime_1,
                  'var_name': 'SSM'}

        self.acube_fn2 = ACubeFilename(fields, convert=True)

        self.acube_fn3 = ACubeFilename(fields)

        fn = 'SIG0-----_SGRTA01_S1B_IWGRDH1VVA_20170725_165004--_EU500M_E048N012T6.tif'
        self.acube_fn4 = ACubeFilename.from_filename(fn, convert=True)

        fn = 'TMENSIG40_SGRTB01_ASA_WSM1-----D_20170725_20181225_EU500M_E048N012T6.tif'
        self.acube_fn5 = ACubeFilename.from_filename(fn)
        self.acube_fn6 = ACubeFilename.from_filename(fn, convert=True)

    def test1_build_acube_filename(self):
        """
        Test building ACube file name.

        """
        fn = ('SSM------_-------_---_----------_20080101_20090202_------_----------.tif')

        self.assertEqual(str(self.acube_fn), fn)

    def test2_get_n_set_date(self):
        """
        Test set and get start and end date.

        """
        self.assertEqual(self.acube_fn['dtime_1'], self.dtime_1.date())
        self.assertEqual(self.acube_fn['dtime_2'], self.dtime_2.date())

        new_start_time = datetime(2009, 1, 1, 12, 23, 33).date()
        self.acube_fn['dtime_1'] = new_start_time

        self.assertEqual(self.acube_fn['dtime_1'], new_start_time)

    def test30_get_n_set_date_n_time(self):
        """
        Test set and get date and time for a single datetime.

        """
        self.assertEqual(self.acube_fn2['dtime_1'], self.dtime_1.date())
        self.assertEqual(self.acube_fn2['dtime_2'], self.dtime_1.time())

        new_start_time = datetime(2009, 1, 1, 12, 23, 33)
        self.acube_fn2['dtime_1'] = new_start_time
        self.acube_fn2['dtime_2'] = new_start_time

        self.assertEqual(self.acube_fn2['dtime_1'], new_start_time.date())
        self.assertEqual(self.acube_fn2['dtime_2'], new_start_time.time())

    def test31_get_n_set_date_n_time_dts(self):
        """
        Test get and set date and time for a single datetime,
        returning strings.

        """
        self.assertEqual(self.acube_fn2.obj.dtime_1, datetime(2008, 1, 1).date())
        self.assertEqual(self.acube_fn2.obj.dtime_2, time(12, 23, 33))

        new_start_time = datetime(2345, 1, 2, 7, 8, 9)
        self.acube_fn2['dtime_1'] = new_start_time
        self.acube_fn2['dtime_2'] = new_start_time

        self.assertEqual(self.acube_fn2.obj.dtime_1, datetime(2345, 1, 2).date())
        self.assertEqual(self.acube_fn2.obj.dtime_2, time(7, 8, 9))

    def test32_get_n_set_date_n_time_strings(self):
        """
        Test get and set date and time for a single datetime,
        returning strings.

        """
        self.assertEqual(self.acube_fn3.obj.dtime_1, '20080101')
        self.assertEqual(self.acube_fn3.obj.dtime_2, '122333')

        new_start_time = datetime(2345, 1, 2, 7, 8, 9)
        self.acube_fn3['dtime_1'] = new_start_time
        self.acube_fn3['dtime_2'] = new_start_time

        self.assertEqual(self.acube_fn3.obj.dtime_1, '23450102')
        self.assertEqual(self.acube_fn3.obj.dtime_2, '070809')

    def test4_create_acube_filename(self):
        """
        Tests the creation of a SmartFilename from a given string filename.

        """

        # testing for single datetime
        self.assertEqual(self.acube_fn4['dtime_1'], datetime(2017, 7, 25).date())
        self.assertEqual(self.acube_fn4['dtime_2'], time(16, 50, 4))
        self.assertEqual(self.acube_fn4['var_name'], 'SIG0')
        self.assertEqual(self.acube_fn4['sat_name'], 'S1B')
        self.assertEqual(self.acube_fn4['product'], 'IWGRDH1')
        self.assertEqual(self.acube_fn4['pol'], 'VV')
        self.assertEqual(self.acube_fn4['direction'], 'A')
        self.assertEqual(self.acube_fn4['algorithm'], 'SGRTA01')
        self.assertEqual(self.acube_fn4['grid_name'], 'EU500M')
        self.assertEqual(self.acube_fn4['tile_name'], 'E048N012T6')
        self.assertEqual(self.acube_fn4.ext, '.tif')

        # testing for empty fields and two dates
        self.assertEqual(self.acube_fn5['dtime_1'], '20170725')
        self.assertEqual(self.acube_fn5['dtime_2'], '20181225')
        self.assertEqual(self.acube_fn5['var_name'], 'TMENSIG40')
        self.assertEqual(self.acube_fn5['sat_name'], 'ASA')
        self.assertEqual(self.acube_fn5['product'], 'WSM1')
        self.assertEqual(self.acube_fn5['pol'], '')

        # testing for empty pol field
        self.assertEqual(self.acube_fn6['pol'], None)

    def test5_build_ascat_ssm_fname(self):
        """
        Tests the creation of a resampled ASCAT SSM filename.

        """
        date_time = '20331122_112233'
        tilename = 'EU500M_E012N024T6'

        xfields = {'dtime_1': datetime.strptime(date_time[:8], "%Y%m%d"),
                   'dtime_2': datetime.strptime(date_time[-6:], "%H%M%S"),
                   'var_name': 'SSM',
                   'sat_name': 'ASC',
                   'product': 'SMO12NA',
                   'pol': 'XX',
                   'direction': 'D',
                   'algorithm': 'SGRTC01',
                   'grid_name': tilename[:6],
                   'tile_name': tilename[7:]}

        should = 'SSM------_SGRTC01_ASC_SMO12NAXXD_20331122_112233--_EU500M_E012N024T6.tif'
        fn = ACubeFilename(xfields)
        self.assertEqual(str(fn), should)


if __name__ == "__main__":
    unittest.main()
