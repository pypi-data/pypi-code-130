
import warnings
warnings.filterwarnings('ignore')

from datetime import time, datetime, timedelta
from time import sleep
from pathlib import Path
import pandas as pd 

import os

if os.name == 'nt':
    import MetaTrader5 as mt5 
else:
    Warning(f'Current system is not windows. Can not import MetaTrader5.')


class _PrintLogger:
    info = print
    error = print


class MT5Api:
    """

    Attributes:
    -----------
    account_info: 
        e.g.
        login=300064610, trade_mode=0, leverage=100, limit_orders=0, margin_so_mode=0, 
        trade_allowed=False, trade_expert=True, margin_mode=2, currency_digits=2, 
        fifo_close=False, balance=91748.07, credit=0.0, profit=0.0, 
        equity=91748.07, margin=0.0, margin_free=91748.07, margin_level=0.0, 
        margin_so_call=100.0, margin_so_so=100.0, margin_initial=0.0, 
        margin_maintenance=0.0, assets=0.0, liabilities=0.0, commission_blocked=0.0,
        name='My Forex Funds - Evaluation Phase 1 Demo - Xiaolei Lu ', 
        server='TradersGlobalGroup-Demo', currency='USD', 
        company='Traders Global Group Incorporated')
    broker_time:
    broker_time_local:
    cur_positions: 




    Methods:
    --------
    get_market_close_dt: (static)
    get_market_open_dt: (static)
    login: ()
    get_positions: ()
    close_position: ()
    get_history_positions: ()
    get_price_to_close: (position)
    get_M1_bars: ()


    
    """
    HISTORY_RET_COLS = ['En_Time', 'Volume', 'Symbol', 'En_Price',
                'Ex_Time', 'Ex_Price', 'Swap', 'Profit',
                'Comment', 'Magic']
    @staticmethod
    def get_market_close_dt(min_before=2):
        """returns `datetime`(Broker GMT) of market for current week, shifted by `min_before`

        Args:
            min_before (int, optional): shift number of minutes before. Defaults to 2.

        Returns:
            datetime: datetime of market close
        """
        # doesnt requires mt5, return 1 minutes before
        today = datetime.now().date() + timedelta(1)
        friday = today + timedelta( (4-today.weekday()) % 7 )
        market_close_dt = datetime.combine(friday, datetime.min.time()) + timedelta(hours=23, minutes=55)
        if min_before >= 0:
            return market_close_dt - timedelta(minutes=min_before)
        else:
            return market_close_dt + timedelta(minutes=abs(min_before))
            
    @staticmethod
    def get_market_open_dt(min_after=0):
        '''Return dt of market open, If make comparison, required to request mt5 '''
        return MT5Api.get_market_close_dt(min_before=-5-min_after) + timedelta(days=2)


    def __init__(self, 
        mt5_exe_path:str,
        server:str,
        login:int,
        password:str,
        view_only:bool=True,
        logger=_PrintLogger,
        **kwargs):

        """Login to account and checking market time condition.
        """
        self._login_conf =  {
            'mt5_exe_path': Path(str(mt5_exe_path)),
            'server': server,
            'login': int(login),
            'password': password
        }
        self.view_only = view_only
        self.logger = logger
        self.login()
        if not view_only:
            check_ok, reason = self._check()
            
            if not check_ok:
                raise ValueError(reason)
        
    @property
    def account_info(self):
        return mt5.account_info()

    @property
    def broker_time_local(self):
        """Returns broker time calculated locally

        Returns:
            datetime: datetime of current calculated broker time 
        """
        return self._time_delta + datetime.utcnow()

    @property
    def broker_time(self):
        """Each call returns datetime from broker

        Returns:
            datetime: datetime of EURUSD 
        """
        sec = mt5.symbol_info_tick('EURUSD').time
        return pd.to_datetime(sec, unit='s')


    @property
    def cur_positions(self):
        """Return current open positions
        """
        try:
            return mt5.positions_get()
        except:
            self.logger.error(f'Error when get current positions, mt5 error: {mt5.last_error()}')
            return []

    def _account_has_changed(self):
        """Return True if account has changed in mt5"""
        if self.account_info.login != self._login_conf['login']:
            return True
        else:
            return False

    def login(self):
        """Login mt5 account, rase Error if not succeessed
        """
        _login = self._login_conf['login']
        mt5.initialize(Path(self._login_conf['mt5_exe_path']).as_posix())
        authorized=mt5.login(_login, password=self._login_conf['password'], server=self._login_conf['server'])

        if authorized:
            if mt5.account_info()!=None: 
                self.logger.info(f"Loggin successful for account {_login}")
            else:
                self.logger.error(f"Loggin failed for account {_login}")
        else: 
            raise ValueError(f"Failed to connect to trade account {_login} error code =",mt5.last_error()) 

    def _check(self):
        """Return a check on AutoTrading and EURUSD symbol enabled

        Returns:
            success (bool): good to go. 
            reason (str): if not success, the reason of it
        """
        eu_selected = mt5.symbol_info('EURUSD').select
        trade_allowed = mt5.terminal_info().trade_allowed
        if not eu_selected:
            return False, 'EURUSD not listed Marketwatch'
        
        if not trade_allowed:
            return False, 'AutoTrading is disabled'
        
        return True, ''
        

    def _check_market_is_open(self):
        """Return a bool value indicates is market open or not

        By checking the tick time of EURUSD in an interval of 5 seconds
        
        Returns:
            bool: true for open, false for closed
        """
        self.logger.info('Checking is market open... ')
        t1 = mt5.symbol_info_tick('EURUSD').time
        if pd.to_datetime(t1, unit='s').weekday() <= 4: 
            return True
        sleep(10)
        t2 = mt5.symbol_info_tick('EURUSD').time
        if (t1 == t2) and (t1.time() == time(23,54,59)):
            self.logger.info(' Market is closed!')
            return False
        else:
            self.logger.info(' Market is open!')
            return True

    def get_price_to_close(self, position):
        """Return the price if close the `position`

        Args:
            position (positon): position to close
        """
        tick = mt5.symbol_info_tick(position.symbol)
        volume = position.volume if position.type == 0 else -position.volume
        ex_price = tick.bid if volume > 0 else tick.ask
        return ex_price

    def _get_bar(self, symbol, lb=10):
        """Return M1 bar dataframe with `lb` looklack period. Index sorted by datetime

        Args:
            lb (int, optional): look back period. Defaults to 10.

        Returns:
            dataframe: bar dataframe indexed by broker time, with columns ['open', 'high', 'low', 'close]
        """
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, lb+1) 
        rates_frame = pd.DataFrame(rates) 
        rates_frame.index = pd.to_datetime(rates_frame['time'], unit='s') 
        return rates_frame[['open', 'high', 'low', 'close']]

    def get_M1_bars(self, symbol, lb=10):
        """Return M1 dataframe with last minute fully passed. 
        Args:
            symbol (str): symbol to retrieve
            lb (int, optional): look back period. Defaults to 10.

        Returns:
            DataFrame: with length `lb`+1, columns are ['open', 'high', 'low', 'close']
        """
        assert mt5.terminal_info().maxbars > lb+1, f'Please set max bars larger than {lb+1} in mt5!'
        cur_dt = self.broker_time
        sleep(59 - cur_dt.time().second)
        time_loc = cur_dt.replace(second=0)
        bars = self._get_bar(symbol, lb=lb).loc[:time_loc]
        return bars
    
    def get_positions(self, position_id=None, symbol=None):
        """Return open positions given its position id or symbol.
        
        return a list if symbol is given
        return position obj if position_id is given

        Args:
            position_id (int): position id of cur open position
            symbol (str): symbol to get

        Returns:
            position: if not opened, return None
        """
        if self._account_has_changed():
            self.logger.error('Account has changed in MT5, abort!')
            return
        positions = []
        for pos in self.cur_positions:
            if not position_id is None:
                if pos.identifier == position_id:
                    return pos
            if not symbol is None:
                if pos.symbol == symbol:
                    positions += [pos]
        return positions

    def close_position(self, position, comment='From Python API'):
        """Close position with market order

        Args:
            position (MT5 Position): position object, which to close

        Returns:
            bool: indicates closed successfully or not
        """
        if self._account_has_changed():
            self.logger.error('Account has changed in MT5, abort!')
            return
        if self.view_only:
            self.logger.error('Current instance can only view the account, abort!')
            return

        if len(self.get_positions(position_id=position.identifier))==0:
            self.logger.info(f'dt: {self.broker_time_local} Acc: {self.account_info.login}, Sym: {position.symbol}, Position has already clsoed.')
            return False

        if self.TEST_MODE:
            pos = position
            row = pd.Series({
                'Sim_profit': pos.profit,
                'Sim_Ex_Time': self.broker_time,
                'Sim_Ex_Price': self.get_price_to_close(pos),
                'Sim_Ex_comment': comment
            }, name=pos.identifier)
            self._record(row)
            return True

        request={ 
            "action": mt5.TRADE_ACTION_DEAL, 
            "symbol": position.symbol, 
            "volume": position.volume, 
            "type": mt5.ORDER_TYPE_SELL if position.type==0 else mt5.ORDER_TYPE_BUY, 
            "position": position.identifier, 
            "magic": position.magic, 
            "comment": comment, 
            "type_time": mt5.ORDER_TIME_GTC, 
            "type_filling": mt5.ORDER_FILLING_IOC, 
        } 
        # send a trading request 
        result=mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            if result.retcode == 10027:
                self.logger.warn(f'AutoTrading disabled!')
            self.logger.error(f" dt: {self.broker_time_local}, order_send failed, retcode={result.retcode} Acc: {self.account_info.login}, Sym: {position.symbol}") 
            #self.logger.error(result)
            return False
        else:
            #self.trigger_closed_positions += [position]
            return True
        

    def get_history_positions(self, date_from, date_to=None):
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
        if self._account_has_changed():
            self.logger.error('Account has changed in MT5, abort!')
            return

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
        return positions[self.HISTORY_RET_COLS]
