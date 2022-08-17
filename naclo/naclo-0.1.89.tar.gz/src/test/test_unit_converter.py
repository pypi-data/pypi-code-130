import unittest
import numpy as np
import pandas as pd

import naclo
from naclo import UnitConverter


class TestUnitConverter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_values = [
            55,
            4,
            7,
            100,
            2000
        ]
        cls.test_units = [
            'ug•ml-1',
            'mg/l',
            'unrecognized',
            np.nan,
            'pm'
        ]
        cls.test_mws = [
            220,
            400,
            300,
            110,
            150
        ]
        cls.test_smiles = 5*['CCC']
        cls.test_mols = naclo.smiles_2_mols(cls.test_smiles)
        
        cls.unit_converter = UnitConverter(cls.test_values, cls.test_units, cls.test_mws)
        return super().setUpClass()
    
    def test_to_molar_conversions(self):
        expected = np.array([
            250e-6,
            10e-6,
            np.nan,
            np.nan,
            2000e-12
        ])
        
        # Test all molar prefixes
        molars = self.unit_converter.to_molar()
        milli_molars = self.unit_converter.to_milli_molar()
        micro_molars = self.unit_converter.to_micro_molar()
        nano_molars = self.unit_converter.to_nano_molar()
        for vals, multi in zip([molars, milli_molars, micro_molars, nano_molars],
                               [1, 1e3, 1e6, 1e9]):
            self.assertIsInstance(
                vals,
                pd.Series
            )
            self.assertTrue(
                np.allclose(
                    vals.to_numpy(),
                    expected * multi,
                    equal_nan=True  # np.nan does not evaluate equal
                )
            )
        
    def test_to_neg_log_molar(self):
        neg_log_molars = self.unit_converter.to_neg_log_molar()
        
        self.assertIsInstance(
            neg_log_molars,
            pd.Series
        )
        
        expected = np.array([
            3.60206,
            5,
            np.nan,
            np.nan,
            8.69897
        ])
        
        self.assertTrue(
            np.allclose(
                neg_log_molars.to_numpy(),
                expected,
                equal_nan=True
            )
        )
        
    def test_df_converter(self):
        # Dont drop NA
        df = pd.DataFrame({'value': self.test_values, 'unit': self.test_units, 'mol': self.test_mols})
        out = UnitConverter.df_converter(df, 'mol', 'value', 'unit', 'm', drop_na_units=False)
        
        self.assertIn(
            'molar_value',
            out.columns
        )
        self.assertEqual(
            out['molar_value'].iloc[-1],
            df['value'].iloc[-1] * 1e-12  # pM
        )
        
        # Drop NA indices
        out = UnitConverter.df_converter(df, 'mol', 'value', 'unit', 'm', drop_na_units=True)
        self.assertEqual(
            list(out.index),
            [0, 1, 4]
        )
        
    def test_convert(self):
        units = ['M', 'mM', 'uM', 'nM', 'µM']
        for unit in units + [u.lower() for u in units] + [u.upper() for u in units[:-1]]:  # DONT CAP THE MU
            out = UnitConverter.convert(self.test_values, unit, '-log(m)')
            self.assertIsInstance(out, list)
        
        # ERROR: invalid input unit
        with self.assertRaises(ValueError):
            UnitConverter.convert(self.test_values, 'unrecognized', '-log(m)')
        
        # ERROR: invalid output unit
        with self.assertRaises(ValueError):
            UnitConverter.convert(self.test_values, 'm', 'unrecognized')

        
if __name__ == '__main__':
    unittest.main()
