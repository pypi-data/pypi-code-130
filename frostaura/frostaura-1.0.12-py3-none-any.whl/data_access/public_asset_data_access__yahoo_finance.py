'''This module defines Yahoo Finance data access components.'''
import yfinance as yf
import pandas as pd
from logging import info, warning
from expiringdict import ExpiringDict
from frostaura.data_access.public_asset_data_access import IPublicAssetDataAccess

class YahooFinanceDataAccess(IPublicAssetDataAccess):
    '''Yahoo Finance public asset-related functionality.'''

    def __init__(self, config: dict = {}):
        self.config = config
        self.__cache__ = ExpiringDict(max_len=999999,
                                      max_age_seconds=60*5)

    def get_symbol_history(self, symbol: str, ignore_cache: bool = False) -> pd.DataFrame:
        '''Get historical price movements for a given symbol.'''

        info(f'Fetching historical price movements for symbol "{symbol}".')

        value = self.__cache__.get(symbol)

        if value is None:
            warning(f'No item with the key "{symbol}" existed in the cache.')
            ticker = yf.Ticker(symbol)
            value = ticker.history(period='max')
            self.__cache__[symbol] = value
        else:
            info(f'Item for key "{symbol}" retrieved from cache with value: {value}')

        return value
