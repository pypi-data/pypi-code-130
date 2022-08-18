from logging import warning
from math import log10
import pandas as pd
import numpy as np
import copy
from typing import Union, Iterable

import naclo
from naclo.__asset_loader import recognized_units


class UnitConverter:
    _recognized_units = copy.deepcopy(recognized_units)
    _standard_unit_col = 'standard_unit'
    _multiplier_col = 'multiplier'
    
    def __init__(self, values:Iterable, units:Iterable, mol_weights:Iterable) -> None:
        # Column names
        self._unit_col = 'unit'
        self._value_col = 'value'
        self._mw_col = 'mol_weight'
        
        self.df = pd.DataFrame({
            self._unit_col: copy.deepcopy(units),
            self._value_col: copy.deepcopy(values),
            self._mw_col: copy.deepcopy(mol_weights)
        })
        
        # Unit groups
        self.molar = [
            'pm',
            'nm',
            'um',
            'mm',
            'm'
        ]
        self.g_ovr_l = [
            'pg/l',
            'ng/l',
            'ug/l',
            'mg/l',
            'm/l',
            'pg/ml',
            'ng/ml',
            'ug/ml',
            'mg/ml',
            'm/ml'
        ]
        
        self.df = UnitConverter.standardize_units(self.df, self._unit_col)
    
    @staticmethod
    def neg_log(val:Union[int, float, np.number]) -> float:
        """Simple negative log10 computation.

        Args:
            val (Union[int, float, np.number]): Value to use for computation.

        Returns:
            float: Computed value.
        """
        if val < 0:
            warning(f'Negative value {val} passed to UnitConverter.__neg_log().')
            return np.nan
        elif val == 0:
            return 0
        else:
            return -1*log10(val)
    
    @staticmethod
    def inv_neg_log(val:float) -> float:
        '''Inverse of self.neg_log()'''
        return 10**(-1*val)
        
    @staticmethod
    def df_converter(df:pd.DataFrame, mol_col_name:str, value_col_name:str, units_col_name:str, output_units:str,
                         drop_na_units:bool) -> pd.DataFrame:
        """Converts mixed units to desired units using unit column in df

        Args:
            df (pd.DataFrame): Dataset
            mol_col_name (str): Name of Mol column in df
            value_col_name (str): Name of numerical value column in df refered to by units
            units_col_name (str): Name of units column in df
            output_units (str): Output unit type
            drop_na_units (bool): If True, drops w/ NA units. Else, keeps the values as nan

        Returns:
            pd.DataFrame: Dataset w/ units converted
        """
        df = df.copy()
        uc = UnitConverter(df[value_col_name], df[units_col_name], naclo.mol_weights(df[mol_col_name]))
        output_units = output_units.lower()
        
        if output_units == '-log(m)':
            col_name = f'neg_log_molar_{value_col_name}'
            df[col_name] = uc.to_neg_log_molar()
        elif output_units == 'm':
            col_name = f'molar_{value_col_name}'
            df[col_name] = uc.to_molar()
        elif output_units == 'mm':
            col_name = f'milli_molar_{value_col_name}'
            df[col_name] = uc.to_milli_molar()
        elif output_units in ['um', 'µm']:
            col_name = f'micro_molar_{value_col_name}'
            df[col_name] = uc.to_micro_molar()
        elif output_units == 'nm':
            col_name = f'nano_molar_{value_col_name}'
            df[col_name] = uc.to_nano_molar()
        else:
            raise ValueError(f'Output units: "{output_units}" are not recognized')
        
        return df.dropna(subset=[col_name]) if drop_na_units else df
        
    @staticmethod
    def convert(values:Iterable[float], in_unit:str, out_unit:str) -> str:
        '''Simply converts from one unit to another. out_unit can be -log(M)'''
        try:
            if in_unit.lower() == '-log(m)':
                molar_values = [UnitConverter.inv_neg_log(v) for v in values]
            else:
                molar_values = [v * UnitConverter._recognized_units[in_unit.lower()][1] for v in values]
        except KeyError:
            raise ValueError(f'Unit {in_unit} not recognized.')
        
        if out_unit.lower() == '-log(m)':
            return [UnitConverter.neg_log(m) for m in molar_values]
        else:
            try:
                return [m / UnitConverter._recognized_units[out_unit.lower()][1] for m in molar_values]
            except KeyError:
                raise ValueError(f'Unit {out_unit} not recognized.')
    
    @staticmethod
    def standardize_units(df, unit_col_name) -> pd.DataFrame:
        """Appends standard units and multipliers found in naclo/assets/recognized_units.json to self.df. Appends
        np.nan if unit is not recognized."""
        standard_units = []
        multipliers = []
        
        for unit in df[unit_col_name]:
            try:
                standard_unit, multiplier = UnitConverter._recognized_units[f'{unit}'.lower()]
                standard_units.append(standard_unit)
                multipliers.append(multiplier)
            except KeyError:
                standard_units.append(np.nan)
                multipliers.append(np.nan)
                continue
            
        df[UnitConverter._standard_unit_col] = standard_units
        df[UnitConverter._multiplier_col] = multipliers
        return df
            
    def __to_molar_broadcaster(self, row:pd.Series) -> float:
        """Broadcasting function to use with pd.DataFrame.apply(). Computes molar values from self.df.

        Args:
            row (pd.Series): pd.DataFrame row passed in apply().

        Returns:
            Union[float]: Molar value. np.nan if the standard unit is not found in self.molar or self.g_ovr_l.
        """
        if row[self._standard_unit_col] in self.molar:
            molar_val = float(row[self._value_col])*row[self._multiplier_col]
        elif row[self._standard_unit_col] in self.g_ovr_l:  # Divide by mw (g/mol) -> g/L * mol/g = M
            molar_val = float(row[self._value_col])*row[self._multiplier_col]/row[self._mw_col]  # Divide by mw
        else:
            molar_val = np.nan
        return molar_val
            
    def to_neg_log_molar(self) -> pd.Series:
        """Applies self.__to_molar_broadcaster and self.__neg_log to self.df.

        Returns:
            pd.Series: Negative log molar values.
        """
        return self.to_molar().apply(self.neg_log)
    
    def to_molar(self) -> pd.Series:
        """Applies self.__to_molar_broadcaster to self.df.

        Returns:
            pd.Series: Molar values.
        """
        return self.df.apply(self.__to_molar_broadcaster, axis=1)
    
    def to_milli_molar(self) -> pd.Series:
        return self.to_molar().apply(lambda x: x*1e3)

    def to_micro_molar(self) -> pd.Series:
        return self.to_molar().apply(lambda x: x*1e6)
    
    def to_nano_molar(self) -> pd.Series:
        return self.to_molar().apply(lambda x: x*1e9)
