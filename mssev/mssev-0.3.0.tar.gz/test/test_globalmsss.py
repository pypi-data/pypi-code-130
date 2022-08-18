import unittest
import pandas as pd

from mssev import global_msss


class TestGlobalMSSS(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = pd.read_csv('test/data.csv')

    def test_original(self):
        original_msss = global_msss(self.data, table='original')
        msss_delta = original_msss - self.data.oGMSSS
        self.assertTrue((msss_delta.abs() < 0.001).all())

    @unittest.expectedFailure
    def test_updated(self):
        updated_msss = global_msss(self.data, table='updated')
        msss_delta = updated_msss - self.data.uGMSSS
        self.assertTrue((msss_delta.abs() < 0.001).all())
