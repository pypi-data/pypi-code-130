
import pandas as pd
import numpy as np

from pathlib import Path
from typing import Union, Tuple, List

from fxutils.utils import PIP_VALUE, get_pippoint, standardize_symbol

from .mql5 import read_mql5
from .myfxbook import read_myfxbook
from .backtest_report import read_btreport



AV_SOURCES = ["MQL5", "MyFxbook", "MT5Termial", "BacktestReport", "Local"]

class HistoryReader:
    """
    This class provides a wrapper around various `reader` from different
    sources of trade history. It unifies the input and output.

    Attributes
    ----------

    source: str
        Source of the history. One of the following
            `MQL5`, mql5 signal url or trade history csv file.
            `MyFxbook`, myfxbook downloaded trade history csv file.
            `MT5Termial`, open and login mt5 account, download history.
            `BacktestReport`, html backtest report from mt4/5 tester (None grid EAs).
            `Local`, local saved csv trade history, usually from previouse saved files.

    fn_or_url: str
        File path or url to the source file. 

    name: str
        Name of the history, if given by user. Else use the filename.

    gmt: (=3) int
        GMT timezone in summer time.

    is_usd_acc: (=True) bool
        If its not USD account, the Profit column is calulated use outdated
        pipvalue.

    start_date: datetime.datetime
        Date of the first trade.

    end_date: datetime.datetime
        Date of the last trade.

    history: pd.DataFrame
        Tradde history in dataframe format indexed by transaction id which if not provided
        in the source file, its indexd by interger. 

        - Complusary columns are:

            En_Time: datetime
                Enter time of the trade.
            Ex_Time: datetime
                Exit time of the trade.
            En_Price: float
                Enter price of the trade.
            Ex_Price: float
                Exit price of the trade.
            Symbol: str
                Traded symbol in standardized format.
            Volume: float, in between [-100, 100]
                Traded volume, negative value for short and
                positive for long trade.
            Profit: float
                Raw profit in USD (Exclude commision and swap). If account currency isnt USD, 
                `is_usd_acc`=False, then this value is calculated
                from outdated pip value.
            

        - Calculated columns:

            pip_pnl: float
                Profit and losss in pips.
            unitlot_pnl: float
                Profit in USD including Commission given by `comm`, and Swap extracted
                from source history.

        
        - Optional columns (depends on sources):

            Magic: int (`source` = MT5Termial)
                Magic number of the trade.
            Comment: str (`source` = MT5Termial)
                Comment of the entering trade


    Methods
    -------

    save: (to_path='./`name`.csv':str)
        Save history to given path, without saving index.

    """

    def __init__(self,
            source:str,
            fn_or_url:Union[None, str]=None,
            name:Union[None, str]=None,
            gmt:int=3,
            comm:int=3,
            is_usd_acc:bool=True,
            mt5_exe_path:Union[None,str]=None,
            server:Union[None,str]=None,
            login:Union[None,int]=None,
            password:Union[None,str]=None,
            date_from:Union[None,str]=None,
            date_to:Union[None,str]=None,
        ) -> None:
        """Read trade history from given source.

        Args:
            source (str): Source of the history. One of the following
                [MQL5, MyFxbook, MT5Termial, BacktestReport]
            fn_or_url (Union[None, str], optional):
                File path or url to the source file.
            name (Union[None, str], optional): 
                Name of the history, if given by user. Else use the filename.. Defaults to None.
            gmt (int, optional): 
                GMT timezone in summer time. Defaults to 3.
            comm (int, optional):
                Commission per unitlot round trade. Default to 3 USD.
            is_usd_acc (bool, optional): 
                If its not USD account, the Profit column is calulated use outdated
                pipvalue. Defaults to True.
            mt5_exe_path (str): 
                (Optional, for `source`=MT5Terminal) exe file of mt5 terminal
            server (str):
                (Optional, for `source`=MT5Terminal) server
            login (int): 
                (Optional, for `source`=MT5Terminal) account number
            password (str): 
                (Optional, for `source`=MT5Terminal)Investor password
            date_from (str): 
                (Optional, for `source`=MT5Terminal) Retrieved history started date
            date_to (List[str,None], optional): 
                (Optional, for `source`=MT5Terminal) Retrieved history end date. Defaults to None.

        """
        
        if 'mql5' in source.lower():
            history = read_mql5(fn_or_url)
        elif 'fxbook' in source.lower():
            history = read_myfxbook(fn_or_url)
        elif 'report' in source.lower():
            history, name = read_btreport(fn_or_url, name=name)
        elif 'terminal' in source.lower():
            import os
            if os.name != 'nt':
                print('Current system isnt windows, can not read MT5!')
                return
            from fxutils import MT5Api

            mt5api = MT5Api(
                mt5_exe_path=mt5_exe_path,
                server=server,
                login=login,
                password=password,
                view_only=True)
            
            history = mt5api.get_history_positions(
                date_from=date_from,
                date_to=date_to
            )
            if name is None:
                name = f'Acc{login}_history'
        elif source.lower() == 'local':
            history = pd.read_csv(fn_or_url)
        else:
            print(f'Unknow source: {source}. Please use only the following sources: {AV_SOURCES}')
            return
        
        if name is None:
            # Use filename as name
            _path = Path(fn_or_url)
            if _path.is_file():
                name = _path.stem
            else:
                name = 'UnKnown'

        # Tidy up dtypes and sort columns.
        history['En_Time'] = pd.to_datetime(history['En_Time'])
        history['Ex_Time'] = pd.to_datetime(history['Ex_Time'])

        if source.lower() != 'local':
            history['Symbol'] = history.Symbol.apply(standardize_symbol)
            # Shift hours based on gmt
            hours_to_shift = gmt - 3
            if hours_to_shift < 0:
                hours_to_shift = pd.to_timedelta(f'{abs(hours_to_shift)}H')
                history.En_Time -= hours_to_shift
                history.Ex_Time -= hours_to_shift
            elif hours_to_shift > 0:
                hours_to_shift = pd.to_timedelta(f'{abs(hours_to_shift)}H')
                history.En_Time += hours_to_shift
                history.Ex_Time += hours_to_shift

            # Calculate extra columns
            history['pip_pnl'] = (history.Ex_Price - history.En_Price)*np.sign(history.Volume)*history.Symbol.apply(lambda sym: get_pippoint(sym))

            if not is_usd_acc:
                history['Profit'] = history.apply(lambda row: row.pip_pnl * PIP_VALUE[row.Symbol] * abs(row.Volume), axis=1).round(2)

            # Calculate unitlot pnl, including commision and swap
            unitlot_factor = 1/history.Volume.abs()
            unitlot_swap = history.Swap * unitlot_factor
            history['unitlot_pnl'] = (history.Profit * unitlot_factor) + unitlot_swap - comm

            # Tidy up history
            history.drop(columns=['Swap'], inplace=True)

        history.En_Price = history.En_Price.astype(float)
        history.Ex_Price = history.Ex_Price.astype(float)
        history.Profit = history.Profit.astype(float).round(2)
        history.pip_pnl = history.pip_pnl.astype(float).round(1)
        history.unitlot_pnl = history.unitlot_pnl.astype(float).round(2)
                

        self.history = history
        self.name = name
        self.is_usd_acc = is_usd_acc
        self.gmt = gmt
        self.fn_or_url = fn_or_url
        self.start_date = self.history.En_Time.min()
        self.end_date = self.history.Ex_Time.max()

    def save(self, fn):
        self.history.to_csv(fn, index=False)