'''This module defines public asset data access components.'''
import pandas as pd

class IPublicAssetDataAccess:
    '''Component to perform functions related to public assets.'''

    def get_symbol_history(self, symbol: str, ignore_cache: bool) -> pd.DataFrame:
        '''Get historical price movements for a given symbol.'''

        raise NotImplementedError()
