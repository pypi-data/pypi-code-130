

import os
if os.name == 'nt':
    import MetaTrader5 as mt5 
else:
    Warning(f'Current system is not windows. Can not import MetaTrader5.')

import warnings
warnings.filterwarnings('ignore')

from datetime import datetime
from pathlib import Path
from typing import Union

import pandas as pd 




RET_COLS = ['En_Time', 'Volume', 'Symbol', 'En_Price',
            'Ex_Time', 'Ex_Price', 'Swap', 'Profit',
            'Comment', 'Magic']


def _get_history_positions(date_from: str, date_to=None) -> pd.DataFrame:
    """ Return positions dataframe indexed by position id, columns are:

       ['En_Time', 'En_Price', 'Volume', 'Symbol', 'Comment', 'Magic',
       'Ex_Time', 'Ex_Price', 'Profit', 'Swap']
       
    Trades opened or closed manually are filtered out from the history.

        for `reason` >= 3 are excuted by EA, actual description 
        see: https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties

    Args:
        date_from (str or datetime): date for start of history, enter dt of positions
        date_to (str or datetime, optional): date for end of history. Defaults to today.

    Returns:
        dataframe: retrieved histoies.
    """

    if isinstance(date_from, str): date_from = pd.to_datetime(date_from)
    if isinstance(date_to, str): date_to = pd.to_datetime(date_to)
    if date_to is None: date_to = datetime.today()
    position_deals = mt5.history_deals_get(date_from, date_to)
    deals_df = pd.DataFrame(list(position_deals),columns=position_deals[0]._asdict().keys()) 

    # Filt out non buy and sell deals
    deals_df = deals_df[deals_df.type.isin([0,1])]
    deals_df['time'] = pd.to_datetime(deals_df.time, unit='s')

    # Select deals with only closed positions
    pid_size = deals_df.groupby('position_id').size()
    closed_pids = pid_size[pid_size==2].index
    deals_df = deals_df[deals_df.position_id.isin(closed_pids)]

    rename_cols = {
        'time': 'En_Time',
        'price': 'En_Price',
        'reason': 'en_reason',
        'commission': 'en_commission',
        'comment': 'Comment',
        'symbol': 'Symbol',
        'magic': 'Magic'
    }
    deal_in = deals_df[deals_df.entry==0]
    deal_in['type'] *= -1
    deal_in.loc[deal_in.type==0, 'type'] = 1
    deal_in['Volume'] = deal_in.volume * deal_in.type
    deal_in.rename(columns=rename_cols, inplace=True)
    deal_in.index = deal_in.position_id
    deal_in = deal_in[['En_Time', 'En_Price', 'Volume', 'Symbol', 'en_commission', 'Comment', 'Magic', 'en_reason']]
    
    rename_cols = {
        'time': 'Ex_Time',
        'price': 'Ex_Price',
        'reason': 'ex_reason',
        'commission': 'ex_commission',
        'comment': 'ex_comment',
        'profit': 'Profit',
        'swap': 'Swap'
    }
    deal_out = deals_df[deals_df.entry==1]
    deal_out.rename(columns=rename_cols, inplace=True)
    deal_out.index = deal_out.position_id
    deal_out = deal_out[['Ex_Time', 'Ex_Price', 'Profit', 'ex_commission', 'Swap', 'ex_reason']]

    positions = deal_in.join(deal_out)
    
    positions['Commission'] = positions.en_commission + positions.ex_commission
    positions = positions[(positions.en_reason==3)&(positions.ex_reason==5)]
    
    positions.drop(columns=['en_commission', 'ex_commission', 'ex_reason', 'en_reason'], inplace=True)
    return positions[RET_COLS]


def read_mt5_terminal(
    mt5_exe_path:str,
    server:str,
    login:int,
    password:str,
    date_from:str,
    date_to:Union[str,None]=None
) -> pd.DataFrame:
    """It open mt5 terminal localed at `mt5_exe_path`, and login
    account sepecified by `server`, `login` and `password`. Then it 
    retrieve the trade history `from_date` to `date_to` or today if not 
    given. Returns the position DataFrame with columns

           ['En_Time', 'En_Price', 'Volume', 'Symbol', 'Comment', 'Magic',
            'Ex_Time', 'Ex_Price', 'Profit', 'Swap', 'Commission']

    Caveat: Trades opened or closed manually are filtered out from the history.

    Args:
        mt5_exe_path (str): exe file of mt5 terminal
        server (str): server
        login (int): account number
        password (str): Investor password
        date_from (str): Retrieved history started date
        date_to (List[str,None], optional): Retrieved history end date. Defaults to None.

    Returns:
        pd.DataFrame: Trade history.
    """

    successed = mt5.initialize(Path(mt5_exe_path).as_posix(), int(login), password=password, server=server)

    if successed:
        return _get_history_positions(date_from, date_to=date_to)
    else:
        print(f'Unable to get history, please check terminal setting.')
        return 



