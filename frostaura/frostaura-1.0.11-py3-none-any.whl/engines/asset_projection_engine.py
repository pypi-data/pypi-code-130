'''This module defines projection engine components.'''
import pandas as pd

class IAssetProjectionEngine:
    '''Component to perform functions related to asset projections.'''

    def project_monthly_asset_growth(self,
                                   n_months: int,
                                   annual_growth_rate: float,
                                   principal_value: float,
                                   monthly_deposit: float) -> pd.DataFrame:
        '''Determine an asset's growth at a given annual rate over a specified number of months while applying a monthly deposit.'''

        raise NotImplementedError()

    def project_monthly_holdings_growth(self,
                                   n_months: int,
                                   annual_growth_rates: list,
                                   principal_values: list,
                                   monthly_deposits: list) -> pd.DataFrame:
        '''Determine a comprehensive holdings growth at a given annual rates over a specified numbers of months while applying a monthly deposits.'''

        raise NotImplementedError()
