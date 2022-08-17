import pandas as pd
import warnings
from typing import Callable, Iterable, Optional
import copy

# sourced from github.com/jwgerlach00
import naclo
import stse
from naclo.UnitConverter import UnitConverter
from naclo.__asset_loader import bleach_default_model
from naclo.__model_schema import bleach_schema

class Bleach:
    filter_fragments_methods = ['carbon_count', 'mw', 'atom_count', 'none']
    
    def __init__(self, df:pd.DataFrame, model:dict=bleach_default_model) -> None:  # *
        # Load user options
        self._model = copy.deepcopy(model)
        
        # Validate model
        bleach_schema.validate(self.model)

        self._recognized_structures = ['smiles', 'mol']
        self._default_cols = {
            'smiles': 'SMILES',
            'mol': 'ROMol',
            'inchi_key': 'InchiKey',
            'mw': 'MW'
        }

        # Save user input data
        self._original_df = df.copy()
        self._df = df.copy()

        self.mol_col = None
        self.smiles_col = None
        self.inchi_key_col = None
        self._set_structure_cols()  # Assign mol and SMILES cols using input + defaults
        
        # Current tracked target data
        self._target_col = model['target_col']
        self._target_units = model['input_units']  # Tracks current units of target_col for conversion purposes
        self._average_flag = False
        
        # Convert static -> instance methods on init
        self.chem_cleanup = self._instance_chem_cleanup
        self.handle_duplicates = self._instance_handle_duplicates
        self.final_unit_conversion = self._instance_final_unit_conversion
        self.append_columns = self._instance_append_columns
        self.remove_header_chars = self._instance_remove_header_chars

# ----------------------------------------------------- ACCESSORS ---------------------------------------------------- #

    @property
    def original_df(self) -> pd.DataFrame:
        return self._original_df.copy()

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy()

    @property
    def model(self) -> dict:
        return copy.deepcopy(self._model)
        
# -------------------------------------------------- PRIVATE METHODS ------------------------------------------------- #
    def _set_structure_cols(self) -> None:
        '''Sets Mol and SMILES columns using declared structure type. Uses defaults if not declared'''
        self.mol_col = self.model['structure_col'] if self.model['structure_type'] == 'mol' else self._default_cols['mol']
        self.smiles_col = self.model['structure_col'] if self.model['structure_type'] == 'smiles' else \
            self._default_cols['smiles']
        self.inchi_key_col = self._default_cols['inchi_key']

    def _drop_na_structures(self) -> None:
        '''Drops NA along declared structure column'''
        self._df.dropna(subset=[self.model['structure_col']], inplace=True)  # NOTE: should save operation to log
        if not len(self._df):
            warnings.warn('ALL_NA_STRUCTURES: All structures in specified column were unrecognized, all rows dropped',
                          RuntimeWarning)

    def _drop_na_targets(self) -> None:
        '''Drops NA along declared target column'''
        run = self.model['format_settings']['remove_na_targets']

        if self._target_col and run and len(self._df):  # If run and TARGET COLUMN DECLARED
            self._df.dropna(subset=[self._target_col], inplace=True)  # NOTE: should save operation to log
            if not len(self._df):
                warnings.warn('ALL_NA_TARGETS: All targets in specified column were NA, all rows dropped',
                              RuntimeWarning)

        elif run:  # If run but not declared target
            warnings.warn('NO_ACTIVITY_COLUMN: format_settings.remove_na_targets was set to run but no activity column \
                was specified', RuntimeWarning)

    def _build_smiles(self) -> None:
        """Creates a SMILES column in the dataset using dataset MolFile column. DROPS NA."""
        self._df = naclo.dataframes.df_mols_2_smiles(self._df, self.mol_col, self.smiles_col)

    def _build_mols(self) -> None:
        """Creates MolFile column in the dataset using dataset SMILES column. DROPS NA."""
        self._df = naclo.dataframes.df_smiles_2_mols(self._df, self.smiles_col, self.mol_col)
        
    @staticmethod
    def _filter_fragments_factory(filter:str) -> Callable:
        '''Returns a callable SMILES fragment filter function using a key'''
        if filter == 'carbon_count':
            return naclo.fragments.carbon_count
        elif filter == 'mw':
            return naclo.fragments.mw
        elif filter == 'atom_count':
            return naclo.fragments.atom_count
        else:
            raise ValueError('Filter method is not recognized')

    @staticmethod
    def _append_inchi_keys(df:pd.DataFrame, mol_col_name:str, inchi_key_col_name:str) -> pd.DataFrame:
        '''Declares inchi key column name using default. Appends inchi keys to dataset'''
        return naclo.dataframes.df_mols_2_inchi_keys(df, mol_col_name, inchi_key_col_name)

    @staticmethod
    def _drop_columns(df:pd.DataFrame, return_columns:Iterable[str], mol_col_name:str, smiles_col_name:str,
                       inchi_key_col_name:str) -> pd.DataFrame:
        '''Removes columns that the user does not want in the final output.'''
        if 'mol' not in return_columns:
            df = df.drop(mol_col_name, axis=1)
        if 'inchi_key' not in return_columns:
            df = df.drop(inchi_key_col_name, axis=1)
        if 'smiles' not in return_columns:
            df = df.drop(smiles_col_name, axis=1)
        
        return df

    @staticmethod
    def _add_columns(df:pd.DataFrame, columns:Iterable[str], mol_col_name:str) -> pd.DataFrame:
        '''Add columns that the user wants in the final output.'''
        if 'mw' in columns:
            df = df.assign(MW = naclo.mol_weights(df[mol_col_name]))
        return df
    
# -------------------------------------------------- PUBLIC METHODS -------------------------------------------------- #
    
    @staticmethod
    def remove_fragments(df:pd.DataFrame, smiles_col_name:str, mol_col_name:str, desalt:bool,
                          filter_method:Optional[str]) -> pd.DataFrame:
        """Removes salts if specified. Drops NA as a result of salt removal. Filters out other fragments by specified
        method. Regenerates Mols between SMILES operations

        Args:
            df (pd.DataFrame): Dataset
            smiles_col_name (str): Name of SMILES column in df
            mol_col_name (str): Name of Mol column in df
            desalt (bool): Run desalter. If True removes recognized salts
            filter_method (Optional[str]): Method to filter other fragments. Options: Bleach.filter_fragments_methods

        Returns:
            pd.DataFrame: Dataset w/ fragments removed
        """
        df = df.copy()
        f_rebuild_mols = lambda x: naclo.dataframes.df_smiles_2_mols(x, smiles_col_name, mol_col_name)
            
        if desalt:
            df[smiles_col_name] = df[smiles_col_name].apply(naclo.fragments.remove_recognized_salts)  # NOTE: should save operation to log
            df = f_rebuild_mols(df)

            # Drop NA (blank string after salts)
            df = stse.dataframes.convert_to_nan(df, na=[''])  # Convert bc NA is just empty string
            df.dropna(subset=[smiles_col_name], inplace=True)  # Drop NA bc may include molecule that is ONLY salts

        # Filter
        if filter_method and filter_method != 'none':
            df[smiles_col_name] = df[smiles_col_name].apply(Bleach._filter_fragments_factory(filter_method))
            df = f_rebuild_mols(df)
            
        return df
    
    @staticmethod
    def nlm_geometric_mean(df:pd.DataFrame, mol_col_name:str, inchi_key_col_name:str, value_col_name:str,
                           input_units:str, units_col_name:Optional[str]) -> pd.DataFrame:
        """Converts values in df to -log(M) and to computes the geometric mean

        Args:
            df (pd.DataFrame): _description_
            mol_col_name (str): _description_
            inchi_key_col_name (str): _description_
            value_col_name (str): _description_
            input_units (str): _description_
            units_col_name (Optional[str]): _description_

        Returns:
            pd.DataFrame: _description_
        """
        df = df.copy()
        col_name = value_col_name
        
        # 1. Convert to -log(M)
        if input_units == 'mixed':  # Unit column
            if units_col_name:
                df = UnitConverter.df_converter(df=df, mol_col_name=mol_col_name, value_col_name=value_col_name,
                                                units_col_name=units_col_name, output_units='-log(m)', drop_na_units=False)
            else:
                raise ValueError('Must specify units_col_name if input_units is mixed')
        else:
            if units_col_name:
                warnings.warn('CONFLICTING_INPUT_UNITS: Units column was specified but input units were not mixed',
                              RuntimeWarning)
            df[col_name] = UnitConverter.convert(df[value_col_name].astype(float), input_units, '-log(m)')
        
        # 2. Average
        return stse.duplicates.average(df, subsets=[inchi_key_col_name], average_by=col_name)  # NOTE: should save operation to log
    

                
            
            # df[col_name] = UnitConverter.static_neg_log_converter(df[value_col_name], input_units)


# ---------------------------------------------------- MAIN STEPS ---------------------------------------------------- #
    # Step 1
    def drop_na(self) -> None:  # *
        '''Converts blanks to NA. Drops NA Mols or SMILES. Handles NA targets. Removes entire NA columns'''

        # 1. Convert all df blanks and 'none' to NA
        self._df = stse.dataframes.convert_to_nan(self._df)

        # 2. Drop rows
        self._drop_na_structures()
        self._drop_na_targets()

        # 3. Drop entire empty cols
        self._df = stse.dataframes.remove_nan_cols(self._df)  # After dropping rows because columns may BECOME empty
        
    # Step 2 
    def init_structure_compute(self) -> None:  # *
        '''Builds (or rebuilds from Mols) SMILES. Builds Mols if not present in dataset. SMILES should be rebuilt from 
        Mols to canonicalize'''
        if self.model['structure_type'] == 'mol':
            self._build_smiles()
            # Rebuilding Mols not necessary

        elif self.model['structure_type'] == 'smiles':
            self._build_mols()
            self._build_smiles()  # Canonicalize SMILES

    # Step 3
    @staticmethod
    def chem_cleanup(df:pd.DataFrame, smiles_col_name:str, mol_col_name:str, desalt:bool, filter_method:Optional[str],
                    neutralize_charge:bool) -> pd.DataFrame:  # * (except neutralize)
        '''Cleans Mols and SMILES'''
        df = df.copy()

        # 1. Deal with fragments (includes salt step -- may include a molecule that is ONLY salts (NA dropped))
        df = Bleach.remove_fragments(df=df, smiles_col_name=smiles_col_name, mol_col_name=mol_col_name, desalt=desalt,
                                      filter_method=filter_method)

        # 2. Neutralize mols
        if neutralize_charge:
            df[mol_col_name] = naclo.neutralize.neutralize_charges(df[mol_col_name])  # NOTE: should save operation to log
            df = naclo.dataframes.df_mols_2_smiles(df, mol_col_name, smiles_col_name)  # Rebuild SMILES
        
        return df
    
    def _instance_chem_cleanup(self) -> None:
        self._df = Bleach.chem_cleanup(df=self._df, smiles_col_name=self.smiles_col, mol_col_name=self.mol_col,
                                     desalt=self.model['chem_settings']['desalt'],
                                     filter_method=self.model['chem_settings']['fragment_filter'],
                                     neutralize_charge=self.model['chem_settings']['neutralize_charge'])

    # Step 4
    @staticmethod
    def handle_duplicates(df:pd.DataFrame, mol_col_name:str, inchi_key_col_name:str, target_col_name:Optional[str]=None,
                          input_units:Optional[str]=None, units_col_name:Optional[str]=None,
                          method='average') -> pd.DataFrame:  # *
        '''Computes inchi keys. Averages, removes, or keeps duplicates. ONLY BY INCHI KEY FOR NOW. Will return units in
        -log(M) if method is average, else original units'''
        avg_flag = False
        df = Bleach._append_inchi_keys(df, mol_col_name, inchi_key_col_name)

        if method == 'average' and target_col_name:
            # Average only on -log(M)
            df = Bleach.nlm_geometric_mean(df=df, mol_col_name=mol_col_name, inchi_key_col_name=inchi_key_col_name,
                                           value_col_name=target_col_name, input_units=input_units,
                                           units_col_name=units_col_name)  # NOTE: should save operation to log
            avg_flag = True
        elif method == 'remove' or (method == 'average' and not target_col_name):
            if method == 'average':
                warnings.warn('Average duplicates was seletced but no target column was specified. Duplicates were \
                    removed instead.', RuntimeWarning)
            df = stse.duplicates.remove(df, subsets=[inchi_key_col_name])  # NOTE: should save operation to log
        return df, avg_flag
    
    def _instance_handle_duplicates(self) -> None:
        self._df, self._average_flag = Bleach.handle_duplicates(df=self._df, mol_col_name=self.mol_col, inchi_key_col_name=self.inchi_key_col,
                                           target_col_name=self._target_col,
                                           input_units=self.model['input_units'],
                                           units_col_name=self.model['units_col'],
                                           method=self.model['format_settings']['duplicate_compounds'])
        
        # Set units to -log(m) if they were converted for geometric mean
        if self._average_flag:
            self._target_col = f'neg_log_molar_{self._target_col}'  # Change column pointer
            self._target_units = '-log(m)'
    
    @staticmethod  
    def final_unit_conversion(df, input_units, output_units, units_col_name, mol_col_name, value_col_name, drop_na_units):
        if input_units == 'mixed':
            if units_col_name:
                return UnitConverter.df_converter(df=df, mol_col_name=mol_col_name, value_col_name=value_col_name,
                                                units_col_name=units_col_name, output_units=output_units,
                                                drop_na_units=drop_na_units)
            else:
                raise ValueError('Must specify units_col_name if input_units is mixed')
        else:
            if units_col_name:
                warnings.warn('CONFLICTING_INPUT_UNITS: Units column was specified but input units were not mixed. Converted using input units',
                              RuntimeWarning)
                
            units_label = 'neg_log_molar' if output_units.lower() == '-log(m)' else output_units  # -log(M) may screw up datasheet characters
            df[f'{units_label}_{value_col_name}'] = UnitConverter.convert(df[value_col_name], input_units, output_units)
            return df
            
    def _instance_final_unit_conversion(self):
        if self._target_units.lower() == self.model['output_units'].lower():
            return  # No change -- already in correct units
        elif not self.model['target_col']:
            warnings.warn('OUTPUT_UNITS_CONVERSION: No target column was specified. No unit conversion was performed.',
                          RuntimeWarning)
            return
        
        # Has already been converted to -log(m)
        if self._average_flag:
            col_name = '{0}_{1}'.format(self.model['output_units'], self.model['target_col'])
            self._df[col_name] = UnitConverter.convert(self._df[self._target_col], '-log(m)', self.model['output_units'])
        else:
            self._df = Bleach.final_unit_conversion(df=self._df, input_units=self.model['input_units'],
                                         output_units=self.model['output_units'],
                                         units_col_name=self.model['units_col'], mol_col_name=self.mol_col,
                                         value_col_name=self._target_col, drop_na_units=self.model['drop_na_units'])

    # Step 6
    @staticmethod
    def append_columns(df:pd.DataFrame, columns:Iterable[str], mol_col_name:str, smiles_col_name:str, inchi_key_col_name:str) -> pd.DataFrame:  # *
        df = df.copy()
        
        df = Bleach._drop_columns(df=df, return_columns=columns, mol_col_name=mol_col_name,
                                  smiles_col_name=smiles_col_name, inchi_key_col_name=inchi_key_col_name)
        df = Bleach._add_columns(df=df, columns=columns, mol_col_name=mol_col_name)
        return df
    
    def _instance_append_columns(self) -> None:
        self._df = Bleach.append_columns(df=self._df, columns=self.model['format_settings']['append_columns'],
                                        mol_col_name=self.mol_col, smiles_col_name=self.smiles_col, inchi_key_col_name=self.inchi_key_col)

    # Step 7
    @staticmethod
    def remove_header_chars(df, chars) -> pd.DataFrame:  # *
        '''Removes any chars listed in a string of chars from the df column headers'''
        return stse.dataframes.remove_header_chars(df, chars)
    
    def _instance_remove_header_chars(self) -> None:
        self._df = Bleach.remove_header_chars(self._df, self.model['format_settings']['remove_header_chars'])


# ----------------------------------------------------- MAIN LOOP ---------------------------------------------------- #
    def main(self) -> pd.DataFrame:
        self.drop_na()  # Before init_structure bc need NA
        self.init_structure_compute()
        self.chem_cleanup()
        self.handle_duplicates()
        
        self.final_unit_conversion()
        
        self.append_columns()
        self.remove_header_chars()
        return self.df
