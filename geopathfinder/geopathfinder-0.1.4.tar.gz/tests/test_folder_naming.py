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
import os
import glob
import shutil

from geopathfinder.folder_naming import SmartPath
from geopathfinder.folder_naming import NullSmartPath
from geopathfinder.naming_conventions.sgrt_naming import sgrt_tree
from geopathfinder.folder_naming import transform_bytes

def cur_path():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


def get_test_sp(root,
                sensor=None,
                mode=None,
                group=None,
                datalog=None,
                product=None,
                wflow=None,
                grid=None,
                tile=None,
                var=None,
                qlook=True,
                make_dir=False):
    '''
    Function creating a SmartPath() for testing SmartPath().
    '''


    # defining the levels in the directory tree (order could become shuffled around)
    levels = {'root': root,
              'sensor': sensor,
              'mode': mode,
              'group': group,
              'datalog': datalog,
              'product': product,
              'wflow': wflow,
              'grid': grid,
              'tile': tile,
              'var': var,
              'qlook': 'qlooks'}

    # defining the hierarchy
    hierarchy = ['root', 'sensor', 'mode', 'group',
                 'datalog', 'product', 'wflow', 'grid',
                 'tile', 'var', 'qlook']

    return SmartPath(levels, hierarchy, make_dir=make_dir)


def get_test_sp_4_smarttree(sensor=None,
                mode=None,
                group=None,
                datalog=None,
                product=None,
                wflow=None,
                grid=None,
                tile=None,
                var=None,
                qlook=True,
                make_dir=False):
    '''
    Function creating a SmartPath() for testing SmartTree().
    '''


    # defining the levels in the directory tree (order could become shuffled around)
    levels = {'sensor': sensor,
              'mode': mode,
              'group': group,
              'datalog': datalog,
              'product': product,
              'wflow': wflow,
              'grid': grid,
              'tile': tile,
              'var': var,
              'qlook': 'qlooks'}

    # defining the hierarchy
    hierarchy = ['sensor', 'mode', 'group',
                 'datalog', 'product', 'wflow', 'grid',
                 'tile', 'var', 'qlook']

    return SmartPath(levels, hierarchy, make_dir=make_dir)


def disk_usage_filelist(filepaths, unit='KB'):
    bytes = sum([os.path.getsize(filepath) for filepath in filepaths])

    return transform_bytes(bytes, unit=unit)


class TestSmartPath(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(cur_path(), 'test_temp_dir')
        self.sp_obj = get_test_sp(self.path, sensor='Sentinel-1_CSAR',
                                  mode='IWGRDH', group='products',
                                  datalog='datasets', product='ssm',
                                  wflow='C1003', grid='EQUI7_EU500M',
                                  tile='E048N012T6', var='ssm',
                                  make_dir=True)

        self.path_perm = os.path.join(cur_path(), 'test_data')
        self.sp_obj_perm = get_test_sp(self.path_perm,
                                       sensor='Sentinel-1_CSAR',
                                       mode='IWGRDH', group='products',
                                       datalog='datasets', product='ssm',
                                       wflow='C1003', grid='EQUI7_EU500M',
                                       tile='E048N012T6', var='ssm',
                                       make_dir=True)

    def tearDown(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)


    def test_get_dir(self):
        '''
        Testing the creation of the directory.

        '''
        result = self.sp_obj.get_dir(make_dir=True)

        assert os.path.exists(result)


    def test_build_levels(self):
        '''
        Testing the level creation.

        '''
        should = os.path.join(self.path, 'Sentinel-1_CSAR', 'IWGRDH', 'products',
                              'datasets', 'ssm', 'C1003')

        result = self.sp_obj.build_levels(level='wflow', make_dir=True)

        assert should == result

        assert os.path.exists(result)


    def test_get_level(self):
        '''
        Testing the level query.

        '''
        should = os.path.join(self.path, 'Sentinel-1_CSAR', 'IWGRDH')

        result = self.sp_obj['mode']

        assert should == result


    def test_expand_full_path(self):
        '''
        Testing the path expansion

        '''
        should = [os.path.join(self.path, 'Sentinel-1_CSAR', 'IWGRDH', 'MY_TEST.txt')]

        result = self.sp_obj.expand_full_path('mode', ['MY_TEST.txt'])

        assert should == result


    def test_search_files(self):
        '''
        Testing the file search yielding file lists.

        '''
        should = ['M20161218_051642--_SSM------_S1BIWGRDH1VVD_095_C1003_EU500M_E048N012T6.tif',
                  'M20170406_050911--_SSM------_S1AIWGRDH1VVD_022_C1003_EU500M_E048N012T6.tif']

        src = glob.glob(os.path.join(cur_path(), 'test_data', '*.*'))
        dest = self.sp_obj.build_levels(level='var', make_dir=True)

        for file in src:
            shutil.copy(file, dest)

        result = self.sp_obj.search_files('var', pattern='SSM')

        assert should == result


    def test_build_file_register(self):
        '''
        Testing the file register.

        '''
        self.sp_obj_perm.build_file_register(down_to_level='var')

        self.assertEqual(self.sp_obj_perm.file_count, 5)


    def test_get_disk_usage(self):
        '''
        Testing the disk usage function.

        '''
        pass
        du1 = self.sp_obj_perm.get_disk_usage('MB', up_to_level='grid')
        self.assertAlmostEqual(du1, 0.058, places=2)

        du2 = self.sp_obj_perm.get_disk_usage('MB', down_to_level='grid')
        self.assertAlmostEqual(du2, 1.032, places=2)

        du3 = self.sp_obj_perm.get_disk_usage('MB')
        self.assertAlmostEqual(du3, 1.090, places=2)

        self.assertAlmostEqual(du1 + du2, du3, places=2)


class TestSmartTree(unittest.TestCase):
    """
    Tests function of the SmartTree() class, applied for testing to the
    SGRT convention.

    """
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), os.path.join('test_data', 'Sentinel-1_CSAR'))
        self.copy_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), os.path.join('test_data', 'copy_target'))
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        os.mkdir(self.copy_dir)
        self.stt_1 = sgrt_tree(self.test_dir, register_file_pattern='.tif')


    def tearDown(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)


    def test_tree_integrity(self):
        """
        Tests of only valid paths are added to the SmartTree()

        """
        self.assertTrue(
            all([True for x in self.stt_1.get_all_dirs() if self.test_dir in x]))


    def test_tree_dir_n_file_count(self):
        """
        Tests the dir_ and file_count of SmartTree()

        """
        self.assertEqual(self.stt_1.dir_count, 9)
        self.assertEqual(self.stt_1.file_count, 17)
        # TODO: should be 16 "file_too_deep.tif" should be not included in file_register!


    def test_get_smartpath(self):
        """
        Tests the selection of a SmartPath matching regex search patterns.

        """
        # typical use case
        should = ['M20160831_163321--_SIG0-----_S1AIWGRDH1VVA_175_A0201_EU500M_E048N006T6.tif']
        result = self.stt_1.get_smartpath(('A0202', 'sig0')).search_files(
            level='var')
        self.assertEqual(should, result)

        # typical use case
        should = ['Q20160831_163321--_SIG0-----_S1AIWGRDH1VVA_175_A0201_EU500M_E006N006T6.tif']
        result = self.stt_1[('A0202', 'sig0')].search_files(level='qlook')
        self.assertEqual(should, result)

        # test postive search pattern
        should = os.path.join(self.test_dir, 'IWGRDH', 'products', 'datasets', 'ssm', 'C1003', 'EQUI7_EU500M', 'E048N012T6', 'ssm-noise', 'qlooks')
        result = self.stt_1.get_smartpath(('C1003', 'E048N012T6', 'noise')).get_dir()
        self.assertEqual(should, result)

        # test negative search pattern
        should = os.path.join(self.test_dir, 'IWGRDH', 'products', 'datasets', 'ssm', 'C1003', 'EQUI7_EU500M', 'E048N012T6', 'ssm', 'qlooks')
        result = self.stt_1['C1003', 'E048N012T6', '-noise'].get_dir()
        self.assertEqual(should, result)

        # handling of no matches
        self.assertTrue(isinstance(self.stt_1['nonsense'], NullSmartPath))

        # handling of multiple matches
        self.assertTrue(isinstance(self.stt_1['A0202'], NullSmartPath))


    def test_collect_level(self):
        """
        Test the collect level functions

        """

        # unique case for the folder topnames
        should = ['E006N006T1', 'E006N006T6', 'E006N006T6',
                  'E006N006T6', 'E006N012T6', 'E048N012T6']
        result = sorted(self.stt_1.collect_level_topnames('tile', unique=True))
        self.assertEqual(should, result)

        # non-unique case for the folder topnames
        should = ['E006N006T1', 'E006N006T6', 'E006N006T6',
                  'E006N006T6', 'E006N006T6', 'E006N012T6',
                  'E048N012T6', 'E048N012T6']
        result = sorted(self.stt_1.collect_level_topnames('tile', unique=False))
        self.assertEqual(should, result)

        # unique case for full dirs
        should = [os.path.join(self.test_dir, 'IWGRDH', 'preprocessed', 'datasets', 'resampled', 'A0202', 'EQUI7_EU500M'),
                  os.path.join(self.test_dir, 'IWGRDH', 'products', 'datasets', 'ssm', 'C1001', 'EQUI7_AF010M'),
                  os.path.join(self.test_dir, 'IWGRDH', 'products', 'datasets', 'ssm', 'C1001', 'EQUI7_EU500M'),
                  os.path.join(self.test_dir, 'IWGRDH', 'products', 'datasets', 'ssm', 'C1003', 'EQUI7_EU500M')]
        result = sorted(self.stt_1.collect_level_string('grid', unique=True))
        self.assertEqual(should, result)

        # test if unique full dirs deliver correct number of topnames
        should = ['EQUI7_AF010M',
                  'EQUI7_EU500M',
                  'EQUI7_EU500M',
                  'EQUI7_EU500M']
        result = sorted(self.stt_1.collect_level_topnames('grid', unique=True))
        self.assertEqual(should, result)


    def test_collect_level_smartpaths(self):
        """
        Test the collect level functions

        """

        # unique case for the folder topnames
        should = ['E006N006T1', 'E006N006T6', 'E006N006T6',
                  'E006N006T6', 'E006N012T6', 'E048N012T6']
        result = sorted(self.stt_1.collect_level_topnames('tile', unique=True))
        self.assertEqual(should, result)

        # non-unique case for the folder topnames
        should = ['E006N006T1', 'E006N006T6', 'E006N006T6',
                  'E006N006T6', 'E006N006T6', 'E006N012T6',
                  'E048N012T6', 'E048N012T6']
        result = sorted(self.stt_1.collect_level_topnames('tile', unique=False))
        self.assertEqual(should, result)

        # unique case for full dirs
        should = [os.path.join(self.test_dir, 'IWGRDH', 'preprocessed', 'datasets', 'resampled', 'A0202', 'EQUI7_EU500M'),
                  os.path.join(self.test_dir, 'IWGRDH', 'products', 'datasets', 'ssm', 'C1001', 'EQUI7_AF010M'),
                  os.path.join(self.test_dir, 'IWGRDH', 'products', 'datasets', 'ssm', 'C1001', 'EQUI7_EU500M'),
                  os.path.join(self.test_dir, 'IWGRDH', 'products', 'datasets', 'ssm', 'C1003', 'EQUI7_EU500M')]
        result = sorted(self.stt_1.collect_level_string('grid', unique=True))
        self.assertEqual(should, result)

        # test if unique full dirs deliver correct number of topnames
        should = ['EQUI7_AF010M',
                  'EQUI7_EU500M',
                  'EQUI7_EU500M',
                  'EQUI7_EU500M']
        result = sorted(self.stt_1.collect_level_topnames('grid', unique=True))
        self.assertEqual(should, result)


    def test_trim2branch(self):
        """
        Test the function for returning a branch (subtree).

        """

        branch1 = self.stt_1.get_subtree_unique_rebased('wflow', 'C1003', register_file_pattern=('.'))
        self.assertEqual(branch1.collect_level_topnames('root'), ['C1003'])

        self.assertEqual(branch1.dir_count, 4)
        self.assertEqual(len(branch1.file_register), 12)
        self.assertEqual(branch1.file_count, 12)

        should = ['E006N006T6', 'E006N012T6', 'E048N012T6']
        self.assertEqual(sorted(branch1.collect_level_topnames('tile')), should)

        # handling of multiple matches
        branch2 = self.stt_1.get_subtree_unique_rebased('grid', 'EQUI7_EU500M')
        self.assertEqual(branch2.dir_count, 0)
        self.assertEqual(len(branch2.file_register), 0)
        self.assertEqual(branch2.file_count, 0)


    def test_copy_smarttree_on_fs(self):
        """
        Tests if the copy functions works properly.

        """
        self.stt_1.copy_smarttree_on_fs(self.copy_dir)

        files = next(os.walk(self.copy_dir))[2]
        file_count = sum([len(files) for r, d, files in os.walk(self.copy_dir)])

        self.assertEqual(file_count, 24)


    def test_copy_smarttree_on_fs_level_pattern(self):
        """
        Tests if the copy functions works properly for given level and pattern.

        """
        self.stt_1.copy_smarttree_on_fs(self.copy_dir,
                                        level='wflow', level_pattern='A0202')

        files = next(os.walk(self.copy_dir))[2]
        file_count = sum([len(files) for r, d, files in os.walk(self.copy_dir)])

        self.assertEqual(file_count, 4)


    def test_get_disk_usage(self):
        """
        Tests if the disk usage functions works properly.

        """
        ssm_rel_filepaths = [
        ("IWGRDH", "products", "datasets", "ssm", "C1001", "EQUI7_AF010M", "E006N006T1", "ssm",
         "M20161017_053649--_SSM------_S1BIWGRDH1VVD_066_C1003_AF010M_E006N006T1.tif"),
        ("IWGRDH", "products", "datasets", "ssm", "C1001", "EQUI7_EU500M", "E006N006T6", "ssm",
         "M20160426_053533--_SSM------_S1AIWGRDH1VVD_066_C1001_EU500M_E006N006T6.tif"),
        ("IWGRDH", "products", "datasets", "ssm", "C1003", "EQUI7_EU500M", "E006N012T6", "ssm",
         "M20161005_053649--_SSM------_S1BIWGRDH1VVD_066_C1003_EU500M_E006N012T6.tif"),
        ("IWGRDH", "products", "datasets", "ssm", "C1003", "EQUI7_EU500M", "E006N012T6", "ssm",
         "M20161017_053649--_SSM------_S1BIWGRDH1VVD_066_C1003_EU500M_E006N012T6.tif"),
        ("IWGRDH", "products", "datasets", "ssm", "C1003", "EQUI7_EU500M", "E006N012T6", "ssm",
         "M20161029_053649--_SSM------_S1BIWGRDH1VVD_066_C1003_EU500M_E006N012T6.tif"),
        ("IWGRDH", "products", "datasets", "ssm","C1003", "EQUI7_EU500M", "E048N012T6", "ssm",
         "M20150818_053449--_SSM------_S1AIWGRDH1VVD_066_C1003_EU500M_E048N012T6.tif"),
        ("IWGRDH", "products", "datasets", "ssm", "C1003", "EQUI7_EU500M", "E048N012T6", "ssm",
         "M20170403_053310--_SSM------_S1BIWGRDH1VVD_066_C1003_EU500M_E048N012T6.tif"),
        ("IWGRDH", "products", "datasets", "ssm", "C1003", "EQUI7_EU500M", "E048N012T6", "ssm", "qlooks",
         "Q20150818_053449--_SSM------_S1AIWGRDH1VVD_066_C1003_EU500M_E048N012T6.tif"),
        ("IWGRDH", "products", "datasets", "ssm", "C1003", "EQUI7_EU500M", "E048N012T6", "ssm", "qlooks",
         "Q20170403_053310--_SSM------_S1BIWGRDH1VVD_066_C1003_EU500M_E048N012T6.tif")]

        sig0_rel_filepaths = [
        ("IWGRDH", "preprocessed", "datasets", "resampled", "A0202", "EQUI7_EU500M", "E006N006T6",
         "sig0", "M20160831_163321--_SIG0-----_S1AIWGRDH1VVA_175_A0201_EU500M_E048N006T6.tif"),
        ("IWGRDH", "preprocessed", "datasets", "resampled", "A0202", "EQUI7_EU500M", "E006N006T6",
         "sig0", "qlooks", "Q20160831_163321--_SIG0-----_S1AIWGRDH1VVA_175_A0201_EU500M_E006N006T6.tif")]

        ssm_filepaths = [os.path.join(self.test_dir, *ssm_rel_filepath) for ssm_rel_filepath in ssm_rel_filepaths]
        sig0_filepaths = [os.path.join(self.test_dir, *sig0_rel_filepath) for sig0_rel_filepath in sig0_rel_filepaths]
        ssm_du = disk_usage_filelist(ssm_filepaths, unit='KB')
        sig0_du = disk_usage_filelist(sig0_filepaths, unit='KB')

        # test result from group_by
        result = self.stt_1.get_disk_usage(unit='KB', group_by=['var'])
        self.assertAlmostEqual(result.loc['ssm']['du'], ssm_du, places=2)

        # test result for file pattern
        result = self.stt_1.get_disk_usage(unit='KB', file_pattern='SIG0', total=True)
        self.assertAlmostEqual(result['du'][0], sig0_du, places=2)

        # test complete query result
        result = self.stt_1.get_disk_usage(unit='KB')
        self.assertEqual(result.shape, (33, 10))
        should = ['E006N006T1', 'E006N006T1', 'E006N006T6', 'E006N006T6', 'E006N006T6', 'E006N006T6', 'E006N006T6',
                  'E006N006T6', 'E006N006T6', 'E006N006T6', 'E006N006T6', 'E006N012T6', 'E006N012T6', 'E048N012T6',
                  'E048N012T6', 'E048N012T6', 'E048N012T6', 'E048N012T6']
        self.assertEqual(sorted(result['tile'].dropna().values), should)


if __name__ == "__main__":
    unittest.main()
