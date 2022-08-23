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

from geopathfinder.naming_conventions.sgrt_naming import SgrtFilename
from geopathfinder.naming_conventions.sgrt_naming import sgrt_tree
from geopathfinder.naming_conventions.sgrt_naming import sgrt_path

logging.basicConfig(level=logging.INFO)


class TestSgrtFilename(unittest.TestCase):

    def setUp(self):
        self.dtime_1 = datetime(2008, 1, 1, 12, 23, 33)
        self.dtime_2 = datetime(2009, 2, 2, 22, 1, 1)

        fields = {'dtime_1': self.dtime_1, 'dtime_2': self.dtime_2,
                  'var_name': 'SSM'}

        self.sgrt_fn = SgrtFilename(fields, convert=True)

        fields = {'dtime_1': self.dtime_1,
                  'var_name': 'SSM'}

        self.sgrt_fn2 = SgrtFilename(fields, convert=True)

        self.sgrt_fn3 = SgrtFilename(fields)

        fn = 'M20170725_165004--_SIG0-----_S1BIWGRDH1VVA_146_A0104_EU500M_E048N012T6.tif'
        self.sgrt_fn4 = SgrtFilename.from_filename(fn, convert=True)

        fn = 'M20170725_20181225_TMENSIG40_ASAWS---M1--D_146_A0104_EU500M_E048N012T6.tif'
        self.sgrt_fn5 = SgrtFilename.from_filename(fn)

        fn = 'M20170725_20181225_TMENSIG40_ASAWS---M1--D_---_A0104_EU500M_E048N012T6.tif'
        self.sgrt_fn6 = SgrtFilename.from_filename(fn, convert=True)

    def test1_build_sgrt_filename(self):
        """
        Test building SGRT file name.

        """
        fn = ('-20080101_20090202_SSM------_-------------_---_-----_------_----------.tif')

        self.assertEqual(str(self.sgrt_fn), fn)

    def test2_get_n_set_date(self):
        """
        Test set and get start and end date.

        """
        self.assertEqual(self.sgrt_fn['dtime_1'], self.dtime_1.date())
        self.assertEqual(self.sgrt_fn['dtime_2'], self.dtime_2.date())

        new_start_time = datetime(2009, 1, 1, 12, 23, 33).date()
        self.sgrt_fn['dtime_1'] = new_start_time

        self.assertEqual(self.sgrt_fn['dtime_1'], new_start_time)

    def test30_get_n_set_date_n_time(self):
        """
        Test set and get date and time for a single datetime.

        """
        self.assertEqual(self.sgrt_fn2['dtime_1'], self.dtime_1.date())
        self.assertEqual(self.sgrt_fn2['dtime_2'], self.dtime_1.time())

        new_start_time = datetime(2009, 1, 1, 12, 23, 33)
        self.sgrt_fn2['dtime_1'] = new_start_time
        self.sgrt_fn2['dtime_2'] = new_start_time

        self.assertEqual(self.sgrt_fn2['dtime_1'], new_start_time.date())
        self.assertEqual(self.sgrt_fn2['dtime_2'], new_start_time.time())

    def test31_get_n_set_date_n_time_dts(self):
        """
        Test get and set date and time for a single datetime,
        returning strings.

        """
        self.assertEqual(self.sgrt_fn2.obj.dtime_1, datetime(2008, 1, 1).date())
        self.assertEqual(self.sgrt_fn2.obj.dtime_2, time(12, 23, 33))

        new_start_time = datetime(2345, 1, 2, 7, 8, 9)
        self.sgrt_fn2['dtime_1'] = new_start_time
        self.sgrt_fn2['dtime_2'] = new_start_time

        self.assertEqual(self.sgrt_fn2.obj.dtime_1, datetime(2345, 1, 2).date())
        self.assertEqual(self.sgrt_fn2.obj.dtime_2, time(7, 8, 9))

    def test32_get_n_set_date_n_time_strings(self):
        """
        Test get and set date and time for a single datetime,
        returning strings.

        """
        self.assertEqual(self.sgrt_fn3.obj.dtime_1, '20080101')
        self.assertEqual(self.sgrt_fn3.obj.dtime_2, '122333')

        new_start_time = datetime(2345, 1, 2, 7, 8, 9)
        self.sgrt_fn3['dtime_1'] = new_start_time
        self.sgrt_fn3['dtime_2'] = new_start_time

        self.assertEqual(self.sgrt_fn3.obj.dtime_1, '23450102')
        self.assertEqual(self.sgrt_fn3.obj.dtime_2, '070809')

    def test4_create_sgrt_filename(self):
        """
        Tests the creation of a SmartFilename from a given string filename.

        """

        # testing for single datetime
        self.assertEqual(self.sgrt_fn4['pflag'], 'M')
        self.assertEqual(self.sgrt_fn4['dtime_1'], datetime(2017, 7, 25).date())
        self.assertEqual(self.sgrt_fn4['dtime_2'], time(16, 50, 4))
        self.assertEqual(self.sgrt_fn4['var_name'], 'SIG0')
        self.assertEqual(self.sgrt_fn4['mission_id'], 'S1')
        self.assertEqual(self.sgrt_fn4['spacecraft_id'], 'B')
        self.assertEqual(self.sgrt_fn4['mode_id'], 'IW')
        self.assertEqual(self.sgrt_fn4['product_type'], 'GRD')
        self.assertEqual(self.sgrt_fn4['res_class'], 'H')
        self.assertEqual(self.sgrt_fn4['level'], '1')
        self.assertEqual(self.sgrt_fn4['pol'], 'VV')
        self.assertEqual(self.sgrt_fn4['orbit_direction'], 'A')
        self.assertEqual(self.sgrt_fn4['relative_orbit'], 146)
        self.assertEqual(self.sgrt_fn4['workflow_id'], 'A0104')
        self.assertEqual(self.sgrt_fn4['grid_name'], 'EU500M')
        self.assertEqual(self.sgrt_fn4['tile_name'], 'E048N012T6')
        self.assertEqual(self.sgrt_fn4.ext, '.tif')

        # testing for empty fields and two dates
        self.assertEqual(self.sgrt_fn5['dtime_1'], '20170725')
        self.assertEqual(self.sgrt_fn5['dtime_2'], '20181225')
        self.assertEqual(self.sgrt_fn5['var_name'], 'TMENSIG40')
        self.assertEqual(self.sgrt_fn5['mission_id'], 'AS')
        self.assertEqual(self.sgrt_fn5['spacecraft_id'], 'A')
        self.assertEqual(self.sgrt_fn5['mode_id'], 'WS')
        self.assertEqual(self.sgrt_fn5['product_type'], '')
        self.assertEqual(self.sgrt_fn5['res_class'], 'M')
        self.assertEqual(self.sgrt_fn5['level'], '1')
        self.assertEqual(self.sgrt_fn5['pol'], '')

        # testing for empty relative orbit field
        self.assertEqual(self.sgrt_fn6['relative_orbit'], None)

    def test5_build_ascat_ssm_fname(self):
        """
        Tests the creation of a resampled ASCAT SSM filename.

        """
        date_time = '20331122_112233'
        tilename = 'EU500M_E012N024T6'

        xfields = {'pflag': 'D',
                   'dtime_1': datetime.strptime(date_time[:8], "%Y%m%d"),
                   'dtime_2': datetime.strptime(date_time[-6:], "%H%M%S"),
                   'var_name': 'SSM',
                   'mission_id': 'AS',
                   'spacecraft_id': 'C',
                   'mode_id': 'SM',
                   'product_type': 'O12',
                   'res_class': 'N',
                   'level': 'A',
                   'pol': 'XX',
                   'orbit_direction': 'D',
                   'workflow_id': 'C0102',
                   'grid_name': tilename[:6],
                   'tile_name': tilename[7:]}

        should = 'D20331122_112233--_SSM------_ASCSMO12NAXXD_---_C0102_EU500M_E012N024T6.tif'
        fn = SgrtFilename(xfields)
        self.assertEqual(str(fn), should)


class TestSgrtPath(unittest.TestCase):
    """
    Tests checking if a SGRT path is correctly reflected by sgrt_tree.
    """

    def setUp(self):
        """
        Setting up the test sgrt_tree.
        """

        self.test_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'test_data', 'Sentinel-1_CSAR')

    def test_full_path(self):
        """
        Tests the SmartPath() for the SGRT naming conventions
        """

        should = os.path.join(self.test_dir, 'IWGRDH', 'products', 'datasets',
                              'ssm', 'C1003', 'EQUI7_EU500M', 'E048N012T6',
                              'ssm', 'qlooks')

        stp1 = sgrt_path(self.test_dir,
                         mode='IWGRDH', group='products', datalog='datasets',
                         product='ssm', wflow='C1003', grid='EQUI7_EU500M',
                         tile='E048N012T6', var='ssm',
                         qlook=True, make_dir=False)

        self.assertEqual(stp1.directory, should)

        # giving no specifications on group and datalog levels
        stp2 = sgrt_path(self.test_dir,
                         mode='IWGRDH', product='ssm', wflow='C1003',
                         grid='EQUI7_EU500M', tile='E048N012T6', var='ssm',
                         qlook=True, make_dir=False)

        self.assertEqual(stp2.directory, should)

        pass


class TestSgrtTree(unittest.TestCase):
    """
    Tests checking if a SGRT tree is correctly reflected by sgrt_tree.
    """

    def setUp(self):
        """
        Setting up the test sgrt_tree.
        """

        self.test_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'test_data', 'Sentinel-1_CSAR')
        self.hierarchy_should = ['root', 'mode', 'group', 'datalog', 'product',
                                 'wflow', 'grid', 'tile', 'var', 'qlook']
        self.stt = sgrt_tree(self.test_dir, register_file_pattern='.tif')


    def test_tree_hierarchy(self):
        """
        Tests if a correct SGRT hierarchy was built.
        """

        self.assertEqual(self.stt.hierarchy, self.hierarchy_should)

        self.assertEqual(self.stt.root, self.test_dir)


    def test_tree_depth(self):
        """
        Checks if maximum depth is not violated.
        """

        max_depth_allowed = len(self.stt.root.split(os.sep)) + \
                            len(self.hierarchy_should) - 1

        self.assertTrue(all([len(x.split(os.sep)) <= max_depth_allowed
                             for x in self.stt.get_all_dirs()]))


if __name__ == "__main__":
    unittest.main()
