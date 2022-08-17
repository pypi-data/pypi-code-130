import unittest
import copy
from xml.etree.ElementTree import QName
import numpy as np
import pandas as pd
from rdkit import Chem
from math import log10

import naclo
from naclo import Bleach
from naclo import UnitConverter
from naclo.__asset_loader import bleach_default_model
import stse


class TestBleach(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls._smiles_df = pd.DataFrame({
            'SMILES': ['Cc1cc(/C=C/C#N)cc(C)c1Nc1nc(Nc2ccc(C#N)cc2)ncc1N',
                       'Cc1cc(/C=C/C#N)cc(C)c1Nc1ncc(N)c(Nc2c(C)cc(/C=C/C#N)cc2C)n1',
                       'CCC',
                       'CCC.Cl',
                       'C.NO.S',
                       'Br',
                       '']
        })
        return super().setUpClass()
    
    @property
    def smiles_df(self):
        return self._smiles_df.copy()
    
    @property
    def default_model(self):
        return copy.deepcopy(bleach_default_model)
    
    def test_drop_na(self):
        df = pd.DataFrame({
            'SMILES': [
                pd.NA,
                '',
                'nan',
                'none',
                'CCC',
                np.nan
            ],
            'ROMol': [
                pd.NA,
                '',
                'nan',
                'C',
                None,
                np.nan
            ],
            'drop_empty': 6*[np.nan]
        })
        model = self.default_model
        
        # SMILES
        model['structure_col'] = 'SMILES'
        model['structure_type'] = 'smiles'
        
        bleach = Bleach(df, model)
        bleach.drop_na()
        
        expected = pd.DataFrame({
            'SMILES': ['CCC']
        }, index=[4])
        
        self.assertTrue(bleach.df.equals(expected))
        
        # Mols
        model['structure_col'] = 'ROMol'
        model['structure_type'] = 'mol'
        
        bleach = Bleach(df, model)
        bleach.drop_na()
        
        expected = pd.DataFrame({
            'ROMol': ['C']
        }, index=[3])
        
        self.assertTrue(bleach.df.equals(expected))
        
        # ALL_NA_STRUCTURES warning
        model['structure_col'] = 'drop_empty'
        bleach = Bleach(df, model)
        
        with self.assertWarns(RuntimeWarning):
            bleach.drop_na()
        self.assertTrue(bleach.df.equals(pd.DataFrame()))  # Empty df, all rows dropped
        
        # ALL_NA_TARGETS warning
        model['structure_col'] = 'ROMol'
        model['target_col'] = 'drop_empty'
        
        # Not set to drop NA targets
        bleach = Bleach(df, model)
        bleach.drop_na()
        
        expected = pd.DataFrame({
            'ROMol': ['C']
        }, index=[3])
        
        self.assertTrue(bleach._df.equals(expected))
        
        # Set to drop NA targets
        model['format_settings']['remove_na_targets'] = True
        bleach = Bleach(df, model)
        
        with self.assertWarns(RuntimeWarning):
            bleach.drop_na()
        self.assertTrue(bleach.df.equals(pd.DataFrame()))  # Empty df, all rows dropped
        
    def test_init_structure_compute(self):
        # From SMILES
        model = self.default_model
        model['structure_col'] = 'SMILES'
        model['structure_type'] = 'smiles'
        
        bleach = Bleach(self.smiles_df, model)
        bleach.drop_na()
        bleach.init_structure_compute()

        # Mol instances
        [self.assertIsInstance(m, Chem.rdchem.Mol) for m in bleach._df['ROMol']]
        
        # From SMILES w/ bad Mols
        mol_df = bleach.df
        
        new_row = pd.DataFrame({
            'SMILES': ['CC', 'C', 'CCC'],
            'ROMol': ['test', 1, 'CCC']
        })
        
        mol_df = pd.concat((mol_df, new_row))
        bleach = Bleach(mol_df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        
        # Rebuilt SMILES are the same
        self.assertEqual(
            bleach.df['SMILES'].tolist(),
            mol_df['SMILES'].tolist()
        )
        [self.assertIsInstance(m, Chem.rdchem.Mol) for m in bleach._df['ROMol']]
        
        # From Mols w/ bad Mols
        model['structure_col'] = 'ROMol'
        model['structure_type'] = 'mol'
        bleach = Bleach(mol_df, model)

        bleach.drop_na()
        bleach.init_structure_compute()
        
        # Drop bad Mols
        [self.assertIsInstance(m, Chem.rdchem.Mol) for m in bleach._df['ROMol']]
        self.assertEqual(
            len(bleach.df),
            len(mol_df) - 3
        )
        self.assertEqual(
            bleach._df['SMILES'].tolist(),
            self.smiles_df['SMILES'].tolist()[:-1]  # Excluding blank
        )
        
    def test_chem_cleanup(self):
        model = self.default_model
        model['structure_col'] = 'SMILES'
        model['structure_type'] = 'smiles'
        
        # Desalt only
        model['chem_settings']['desalt'] = True
        model['chem_settings']['fragment_filter'] = 'none'
        model['chem_settings']['neutralize_charge'] = False
        
        bleach = Bleach(self.smiles_df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        
        expected_smiles = [
            'Cc1cc(/C=C/C#N)cc(C)c1Nc1nc(Nc2ccc(C#N)cc2)ncc1N',
            'Cc1cc(/C=C/C#N)cc(C)c1Nc1ncc(N)c(Nc2c(C)cc(/C=C/C#N)cc2C)n1',
            'CCC',
            'CCC',
            'C.NO.S'
        ]
        
        self.assertEqual(
            bleach.df['SMILES'].tolist(),
            expected_smiles
        )
        
        # Filter only
        model['chem_settings']['desalt'] = False
        
        ## carbon count
        model['chem_settings']['fragment_filter'] = 'carbon_count'
        
        bleach = Bleach(self.smiles_df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        
        self.assertEqual(
            bleach.df['SMILES'].iloc[-2],
            'C'
        )
        
        ## atom count
        model['chem_settings']['fragment_filter'] = 'atom_count'
        
        bleach = Bleach(self.smiles_df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        
        self.assertEqual(
            bleach.df['SMILES'].iloc[-2],
            'NO'
        )
        
        ## molecular weight
        model['chem_settings']['fragment_filter'] = 'mw'
        
        bleach = Bleach(self.smiles_df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        
        self.assertEqual(
            bleach.df['SMILES'].iloc[-2],
            'S'
        )
        
        # Salts + filter together
        model['chem_settings']['desalt'] = True
        model['chem_settings']['fragment_filter'] = 'carbon_count'
        model['chem_settings']['neutralize_charge'] = False
        
        bleach = Bleach(self.smiles_df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        
        expected_smiles = [
            'Cc1cc(/C=C/C#N)cc(C)c1Nc1nc(Nc2ccc(C#N)cc2)ncc1N',
            'Cc1cc(/C=C/C#N)cc(C)c1Nc1ncc(N)c(Nc2c(C)cc(/C=C/C#N)cc2C)n1',
            'CCC',
            'CCC',
            'C'
        ]
        
        self.assertEqual(
            bleach.df['SMILES'].tolist(),
            expected_smiles
        )
        
    def test_handle_duplicates(self):
        df = self.smiles_df
        df['target'] = [1, 2, 3, 4, 5, 6, 7]
        
        model = self.default_model
        model['structure_col'] = 'SMILES'
        model['structure_type'] = 'smiles'
        model['target_col'] = 'target'
        
        expected = pd.DataFrame({
            'SMILES': ['Cc1cc(/C=C/C#N)cc(C)c1Nc1nc(Nc2ccc(C#N)cc2)ncc1N',
                       'Cc1cc(/C=C/C#N)cc(C)c1Nc1ncc(N)c(Nc2c(C)cc(/C=C/C#N)cc2C)n1',
                       'CCC',
                       'C'],
            
            'InchiKey': [
                'NFQWIYBXPYHNRC-ONEGZZNKSA-N',
                'IKTVSGAURLVDFP-KQQUZDAGSA-N',
                'ATUOYWHBWRKTHZ-UHFFFAOYSA-N',
                'VNWKTOKETHGBQD-UHFFFAOYSA-N'],
            
            'target': [1,
                       2,
                       3.5,
                       5]
        })
        
        # Remove
        model['format_settings']['duplicate_compounds'] = 'remove'
        
        bleach = Bleach(df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        bleach.handle_duplicates()
        
        expected_remove = expected.copy()
        expected_remove['target'] = [1, 2, 3, 5]
        
        self.assertTrue(bleach.df[['SMILES', 'InchiKey', 'target']].reset_index(drop=True).equals(expected_remove))
        
        # Keep
        model['format_settings']['duplicate_compounds'] = 'keep'
        
        bleach = Bleach(df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        
        df_before = bleach.df
        bleach.handle_duplicates()
        df_after = bleach.df.drop('InchiKey', axis=1)
        
        self.assertTrue(df_before.equals(df_after))
        
        self.assertIn(  # Added InChI key column
            'InchiKey',
            bleach.df.columns
        )
        
        # Average
        model['format_settings']['duplicate_compounds'] = 'average'
        
        ## WARNING: no target column
        model['target_col'] = ''
        
        bleach = Bleach(df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        
        with self.assertWarns(RuntimeWarning):
            bleach.handle_duplicates()
        ### defaults to same as remove
        self.assertTrue(bleach.df[['SMILES', 'InchiKey', 'target']].reset_index(drop=True).equals(expected_remove))
        
        ## ERROR: input units == mixed but units column not specified
        model['target_col'] = 'target'
        model['input_units'] = 'mixed'
        
        bleach = Bleach(df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        
        with self.assertRaises(ValueError):
            bleach.handle_duplicates()
            
        ## WARNING: input units != mixed but units column specified (even though not even present in df)
        model['target_col'] = 'target'
        model['input_units'] = 'uM'
        model['units_col'] = 'units'
        
        expected = naclo.dataframes.df_smiles_2_inchi_keys(df, 'SMILES', 'InchiKey')
        expected['target'] = [-1 * log10(i * 1e-6) for i in df['target']]
        expected = stse.duplicates.average(expected, subsets=['InchiKey'], average_by='target')
        expected_avg_targets = expected['target'].tolist()[:2] + [expected['target'].iloc[2:4].mean()] + \
            [expected['target'].tolist()[4]]
        
        bleach = Bleach(df, model)
        
        ### check pointer before (should be unchanged)
        self.assertEqual(
            bleach._target_col,
            model['target_col'],
            'target'
        )
        self.assertEqual(
            bleach._target_units,
            model['input_units'],
            'uM'
        )
        
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        
        with self.assertWarns(RuntimeWarning):
            bleach.handle_duplicates()
            
        ### check pointer after (should be changed to -log(M))
        self.assertEqual(
            bleach._target_col,
            'neg_log_molar_' + model['target_col'],
            'neg_log_molar_target'
        )
        self.assertEqual(
            bleach._target_units,
            '-log(m)'
        )
            
        model['units_col'] = ''
        bleach_2 = Bleach(df, model)
        bleach_2.drop_na()
        bleach_2.init_structure_compute()
        bleach_2.chem_cleanup()
        bleach_2.handle_duplicates()
            
        self.assertEqual(
            bleach.df['target'].tolist(),  # Static converter (µM) in response to warning
            bleach_2.df['target'].tolist(),  # No units column at all
            expected_avg_targets
        )
        
        ## mixed units
        model['input_units'] = 'mixed'
        model['units_col'] = 'units'
        df['units'] = [np.nan, 'nm', 'm', 'pg ml-1', 'UM', 'mM', 'M']
        
        bleach = Bleach(df, model)
        
        ### check pointer before (should be unchanged)
        self.assertEqual(
            bleach._target_col,
            model['target_col'],
            'target'
        )
        self.assertEqual(
            bleach._target_units,
            model['input_units'],
            'mixed'
        )
        
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        bleach.handle_duplicates()
        
        ### check pointer after (should be changed to -log(M))
        self.assertEqual(
            bleach._target_col,
            'neg_log_molar_' + model['target_col'],
            'neg_log_molar_target'
        )
        self.assertEqual(
            bleach._target_units,
            '-log(m)'
        )
        
    def test_final_unit_conversion(self):
        df = self.smiles_df
        df['target'] = [1, 2, 3, 4, 5, 6, 7]
        
        model = self.default_model
        model['structure_col'] = 'SMILES'
        model['structure_type'] = 'smiles'
        model['target_col'] = 'target'
        
        model['input_units'] = 'mixed'
        model['units_col'] = 'units'
        df['units'] = [np.nan, 'nm', 'm', 'pg ml-1', 'UM', 'mM', 'M']
        
        bleach = Bleach(df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        bleach.handle_duplicates()
        
        # No change: AVERAGE therefore -log(M) -> -log(M)
        before = bleach.df
        bleach.final_unit_conversion()
        after = bleach.df
        
        self.assertTrue(before.equals(after))
        
        model['output_units'] = 'uM'
        bleach = Bleach(df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        bleach.handle_duplicates()
        
        before = bleach.df
        bleach.final_unit_conversion()
        after = bleach.df
        
        self.assertFalse(before.equals(after))
        
        ## correct conversion factor
        u_molar = [1e6 * UnitConverter.inv_neg_log(v) for v in before['neg_log_molar_target']]
        self.assertTrue(
            np.allclose(
                u_molar,
                after['{0}_{1}'.format(model['output_units'], model['target_col'])].tolist(),
                equal_nan=True
            )
        )
        
        ## retains all conversion columns
        self.assertIn('target', after.columns)
        self.assertIn('neg_log_molar_target', after.columns)
        self.assertIn('uM_target', after.columns)
        
        # Not average: therefore no initial -log(M) conversion
        df = self.smiles_df
        df['target'] = [1, 2, 3, 4, 5, 6, 7]
        
        model = self.default_model
        model['structure_col'] = 'SMILES'
        model['structure_type'] = 'smiles'
        model['target_col'] = 'target'
        
        model['format_settings']['duplicate_compounds'] = 'remove'
        model['input_units'] = 'M'  # NOTE: For easy conversion factor testing
        model['units_col'] = 'units'
        
        ## -> -log(M) conversion
        bleach = Bleach(df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        bleach.handle_duplicates()
        
        before = bleach.df
        
        self.assertNotIn('neg_log_molar_target', before.columns)  # No -log(M)
        self.assertIn('target', before.columns)
        
        with self.assertWarns(RuntimeWarning):  # Units column specified but input units not mixed
            bleach.final_unit_conversion()
        after = bleach.df
        
        self.assertIn('neg_log_molar_target', after.columns)  # -log(M)
        self.assertIn('target', after.columns)
        
        ### correct conversion factor
        neg_log_molars = np.array([UnitConverter.neg_log(v) for v in before['target']])  # NOTE: Easy conversion factor!
        self.assertEqual(
            neg_log_molars.round(decimals=4).tolist(),
            after['neg_log_molar_target'].to_numpy().round(decimals=4).tolist()
        )
        
    # def test_append_columns(self):
        model = self.default_model
        model['structure_col'] = 'SMILES'
        model['structure_type'] = 'smiles'
        model['input_units'] = 'M'
        model['output_units'] = 'M'  # Same units, not conversion to avoid no target col warning
        model['format_settings']['duplicate_compounds'] = 'remove'  # Avoid no target col warning
        
        # All columns
        bleach = Bleach(self.smiles_df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        bleach.handle_duplicates()
        bleach.final_unit_conversion()
        bleach.append_columns()
        
        self.assertEqual(
            ['SMILES', 'ROMol', 'InchiKey', 'MW'],  # NOTE: No taget so dont worry about
            list(bleach._df.columns)
        )
        
        # No columns (except SMILES for testing purposes)
        model['format_settings']['append_columns'] = ['smiles']
        
        bleach = Bleach(self.smiles_df, model)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.chem_cleanup()
        bleach.handle_duplicates()
        bleach.final_unit_conversion()
        bleach.append_columns()
        
        self.assertEqual(
            ['SMILES'],
            list(bleach._df.columns)
        )
        
    def test_remove_header_chars(self):
        model = self.default_model
        model['structure_col'] = 'SMILES'
        model['structure_type'] = 'smiles'
        model['input_units'] = 'M'
        model['output_units'] = 'M'  # Same units, not conversion to avoid no target col warning
        model['format_settings']['duplicate_compounds'] = 'remove'  # Avoid no target col warning
        
        model['format_settings']['remove_header_chars'] = 'sr'
        
        bleach = Bleach(self.smiles_df, model)
        bleach.main()
        
        self.assertEqual(
            ['MILE', 'OMol', 'InchiKey', 'MW'],
            list(bleach._df.columns)
        )
        
    
if __name__ == '__main__':
    unittest.main()
