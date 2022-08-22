

import pandas as pd
from typing import Tuple, Union, List
from configobj import ConfigObj
from pathlib import Path


from fxutils.historyreader import HistoryReader

def merge_histories(hists: List[Union[pd.DataFrame, HistoryReader]]) -> pd.DataFrame:
    """Merge histories 
    in which the hisoties in the list are overlapped.
    Assumes the latest dates are the same. 

    Args:
        hists (List): list of `HistoryReader` instance or 
        history Pd.DataFrame

    Returns:
        pd.DataFrame: Merged history with Sorted by `En_Time`
    """
    hist_dfs = []
    earliest_date = pd.to_datetime('1999-01-01') 
    for hist in hists:
        if isinstance(hist, HistoryReader):
            hist = hist.history
        hist_dfs += [hist]
        earliest_date = max(hist.En_Time.min(), earliest_date)

    hist_all = pd.concat(hist_dfs, axis=0)
    hist_all = hist_all[hist_all.En_Time>=earliest_date]
    '''
    hist_all['EA'] = hist_all.index.map(lambda n: n.split('__')[0].split('_')[0])
    hist_all['pid'] = hist_all.index.map(lambda n: n.split('__')[1])
    hist_all['night_date'] = hist_all.apply(_find_night_date, axis=1)
    hist_all['is_weekend'] = hist_all.En_Time.apply(_is_weekend_trade)
    '''
    return hist_all.sort_values('En_Time')

def read_port_config(config_fn:List[Path,str]) -> Tuple(list,pd.DataFrame):
    """
    Given porfolio configure ini file path.
    Read histories of trades for each source, 
    also a dataframe contains lotsizes for all
    """

    if isinstance(config_fn, str):
        config_fn = Path(config_fn)
    conf_obj = ConfigObj(config_fn.as_posix())
    root_history = config_fn.parent.parent/Path('history')

    hist_list = []
    port_lot = pd.DataFrame()

    for ea, conf in conf_obj.items():
        if ea == 'Global':
            trade_weekend = conf.as_bool('trade_weekend')
            remove_best = conf.as_bool('remove_best')
            remove_worst = conf.as_bool('remove_worst')
            
            acc_balance = conf.as_int('acc_balance')
            max_dd = conf.as_float('max_dd')
            monthly_profit_target = conf.as_float('monthly_profit_target')
            comm = conf.as_float('comm')
            continue
        
        if not conf.as_bool('include'):
            continue
            
        hist_fn = root_history / conf['hist_fn']
        HR = HistoryReader(hist_fn, name=ea)
        
        all_syms = HR.history.Symbol.unique()
        sel_syms = conf.as_list('symbols')

        if sel_syms == ['']: # Select All
            sel_syms = list(all_syms)
        
        hist_list += [HR.history[HR.history.Symbol.isin(sel_syms)]]
        
        global_lotsize = conf.as_float('lot_size')
        sym_lotsize = {sym: global_lotsize for sym in sel_syms}
        
        if 'Lot_Sizes' in conf:
            # Overwrite custom sym lotsize
            for sym, size in conf['Lot_Sizes'].items():
                sym_lotsize[sym] = float(size)
                
        ea_lot = pd.DataFrame({'EA': ea, 'Symbol': sym_lotsize.keys(), 'lot': sym_lotsize.values()})
        port_lot = port_lot.append(ea_lot)
    return hist_list, port_lot



class Portfolio:
    

    def __init__(self) -> None:
        
        pass

    def add_single_history(self,
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
            date_to:Union[None,str]=None
        ):
        pass

    def add_histories_from_config_file(self):
        pass

