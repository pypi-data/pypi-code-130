"""
Read MT5/MT4 backtest htm report. And do simple preporcessing.

"""
import warnings

warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Union

from fxutils.utils import ALL_SYMBOLS, PIP_VALUE, MARGIN_UNIT, standardize_symbol, get_pippoint


RET_COLS = ['En_Time', 'Volume', 'Symbol', 'En_Price',
            'Ex_Time', 'Ex_Price', 'Swap', 'Profit']

def read_btreport(html_fn, name:Union[None, str]=None):
    """Thin wrapper func around `BTReportReader` class, that extract
    only the trade history.
    Returns 

    Args:
        html_fn (str): report heml file
        name (Union[None, str], optional): 
            Name of the report, if not given, will return `{EA name}_BT`.
            Defaults to None.

    Returns:
        _type_: tuple(pd.Dataframe, str)
            trade history with columns 
            `['En_Time', 'Volume', 'Symbol', 'En_Price',
                'Ex_Time', 'Ex_Price', 'Swap', 'Profit']`,
            and the name.
    """

    BTR = BTReportReader(html_fn)
    raw_hist = pd.DataFrame()
    for chart in BTR.charts:
        pos = chart.position
        pos['Symbol'] = chart.Symbol
        raw_hist = raw_hist.append(pos)

    raw_hist = raw_hist[RET_COLS].sort_values('En_Time').reset_index(drop=True)
    if name is None:
        name = f'{BTR.EA}_BT'
    return raw_hist, name


class Chart:
    '''
    Holds positions of single pair from a report.

    Name is unique and it has forms of 

    {EA name}_{Trade symbol}_{Trade Timeframe}_{Sefile name}
    '''
    _position_cols = ['En_Time', 'Ex_Time', 'Volume', 'Swap', 'Profit', 'Unitlot_PnL','En_Price', 'Ex_Price', 'Profit_Pip']
    
    def __init__(self, name, df, Symbol, currency='USD', comm=7, mt5=True) -> None:
        Symbol = standardize_symbol(Symbol)
        self.name = name
        self.Symbol = Symbol
        self.comm = comm
        if mt5:
            if currency == 'USD':# df.Commission.sum()!=0:
                self._positions = self._process_position_dollarprofit(df, Symbol)
            else:
                self._positions = self._process_position_pipprofit(df, Symbol)
        else:
            self._positions = self._process_mt4_deals(df)

        self._positions['Ex_date'] = self._positions.Ex_Time.apply(lambda dt: dt.date())
        daily_pnl = self._positions[['Ex_date', 'Unitlot_PnL']].groupby('Ex_date').sum()

        self._daily_pnl = daily_pnl.rename(columns={'Unitlot_PnL': self.name}).round(1)

        self._get_quarter_margin()
        self._cal_stats()
        pass
    
    @property
    def stats(self):
        return self._stats
    
    @property
    def position(self):
        return self._positions
    
    @property
    def daily_PnL(self):
        return self._daily_pnl

    @property
    def quarter_margin(self):
        return self._quarter_margin
    
    def _cal_stats(self):
        worst_dates = self.daily_PnL.sort_values(self.name).index[:3]
        trades = self._positions.Unitlot_PnL
        trade_days = np.busday_count(self.daily_PnL.index[0], self.daily_PnL.index[-1])
        
        self._stats = {
            'SetName': '_'.join(self.name.split('_')[3:]), # In case some set name contains '_'
            'TradeSymbol': self.Symbol,
            'MostTradeHour': self._positions.En_Time.apply(lambda dt:dt.hour).median(),
            'TotalTrades': len(self._positions),
            'TradesPerDay': round(len(self._positions)/trade_days, 1),
            'MaxLoss': round(trades.min(), 1),
            'Skew': round(trades.skew(), 1),
            'BadDate1st': str(worst_dates[0]),
            'BadDate2nd': str(worst_dates[1]),
            'BadDate3rd': str(worst_dates[2])
        }
        pass

    def save_curve(self, save_fn):
        # Save balance curve
        cumsum = self._positions.copy().set_index('Ex_date').Unitlot_PnL.cumsum()
        print(f'Saving graph of {self.name} to {save_fn}')
        plot = cumsum.plot(legend=True, title=self.name, ylabel='Unit Lot PnL ($)')
        fig = plot.get_figure()
        fig.savefig(save_fn)
        fig.clear()


    def _process_mt4_deals(self, df_deal):
        df_deal.columns = df_deal.iloc[0].values
        # Remove unwanted rows ()
        df_deal = df_deal.iloc[1:]
        df_deal['Time'] = pd.to_datetime(df_deal.Time)
        for num_col in ['Size', 'Price', 'Profit']:
            df_deal[num_col] = df_deal[num_col].astype(float)

        deal_in = df_deal[df_deal.Type.isin(['buy','sell'])]
        deal_in.set_index('Order', drop=True, inplace=True)
        deal_in['Volume'] = deal_in.Type.apply(lambda t: 1 if t == 'buy' else -1) * deal_in.Size
        deal_in = deal_in[['Time', 'Volume', 'Price']]
        deal_in = deal_in.rename(columns={'Time': 'En_Time', 'Price': 'En_Price'})

        deal_out = df_deal.dropna(subset=['Profit'])
        deal_out.set_index('Order', drop=True, inplace=True)
        deal_out = deal_out[['Time', 'Price', 'Profit']]
        deal_out = deal_out.rename(columns={'Time': 'Ex_Time', 'Price': 'Ex_Price'})

        position = deal_in.join(deal_out)
        position['Profit_Pip'] = (position.Ex_Price - position.En_Price)*np.sign(position.Volume)*get_pippoint(self.Symbol)
        position['Unitlot_PnL'] = position.Profit/position.Volume.abs()
        return position[self._position_cols]

    def _process_position_dollarprofit(self, df, Symbol):
        '''
        For backtest result profit calcualte as dollar
        '''
        df.loc[df['Type'] == 'buy', 'Type'] = 1
        df.loc[df['Type'] == 'sell', 'Type'] = -1
        df['Volume'] *= df.Type

        #  Only applicable to out deal
        df['Profit_Pip'] = df.Profit / (PIP_VALUE.get(Symbol, 10.) * (df.Volume.abs()))

        # Back calulcate Enter price. Only applicale to out deal
        df['_exp_en_price'] = df.Price - (df.Profit_Pip/(-df.Type*get_pippoint(Symbol))) # -df.Type here because -1 for deal out for Long postiin

        deal_in = df[df.Direction=='in']
        deal_out = df[df.Direction=='out']

        # Assign order number of out deal to in deal, 
        # Must satisfy
        # 1. Out order > In order number
        # 2. Volumn abs value must be same
        # 3. Out exp_en_price is the closest to Price of deal in
        left_in_orders = np.array(deal_in.index)
        mismatch_pips = []
        match_in_orders = []
        for o, row in deal_out.iterrows():

            con1_o = left_in_orders[left_in_orders<o]
            deal_in_sub = deal_in.loc[con1_o]
            deal_in_sub = deal_in_sub[deal_in_sub.Volume==-1*row.Volume]

            diff = (deal_in_sub.Price - row._exp_en_price).abs()
            mismatch_pips += [diff.min()]
            matching_in_order = diff.idxmin()
            left_in_orders = left_in_orders[left_in_orders!=matching_in_order]
            match_in_orders += [matching_in_order]

        mismatch_pips = round((np.array(mismatch_pips)*get_pippoint(Symbol)).mean(), 2)
        if mismatch_pips != 0:
            print(f'    {Symbol} Mismatch mean pips: {mismatch_pips}  Compare to mean PnL pips:  {round((deal_out.Profit_Pip).abs().mean(), 2)}')

        deal_in_matched = deal_in.loc[match_in_orders]
        deal_out['Volume'] *= -1 # Deal in Volume represent actual direction.
        deal_out['En_Time'] = deal_in_matched.Time.values
        unitlot_factor = 1/deal_out.Volume.abs()

        if deal_out.Commission.sum() == 0:
            # Case in TDS
            deal_out['Commission'] = deal_out.Volume.abs() * self.comm

        # Comm times 2 here, because BT split comm into deal in and out
        unitlot_comm_swap = (deal_out.Commission*2 + deal_out.Swap) * unitlot_factor
        deal_out['Unitlot_PnL'] = deal_out.Profit * unitlot_factor + unitlot_comm_swap
        deal_out['Ex_Time'] = deal_out.Time

        # Extra columns
        deal_out['En_Price'] = deal_in_matched.Price.values
        deal_out['Ex_Price'] = deal_out['Price']
        deal_out['Profit_Pip'] = (deal_out.Ex_Price - deal_out.En_Price)*np.sign(deal_out.Volume)*get_pippoint(self.Symbol)
        # Commison makes following asssertion not workinng
        #assert ((np.sign(deal_out.Unitlot_PnL) * np.sign(deal_out.Profit_Pip))==1).sum() == len(deal_out), 'NOT Match'
        
        return deal_out[self._position_cols]
    
    def _process_position_pipprofit(self, df, Symbol):
        '''
        For backtest result profit calcualte as pips
        '''
        df.reset_index(drop=True, inplace=True)
        df.loc[df['Type'] == 'buy', 'Type'] = 1
        df.loc[df['Type'] == 'sell', 'Type'] = -1
        df['Volume'] *= df.Type

        ## Loop through each deal, match out with in deals, by Profit.
        ## Since we uses `calculate pip profit only` for backtesting, so we can back calcualte the entry price, 
        ## Hence able to find the matching.
        ## Goal is to split deal in adn deal out dataframe, match in rows

        # Since our Profit is measure in pip, each pip value calculated as 10. Only applicale to out deal
        df['Profit_Pip'] = df.Profit / (10 * (df.Volume.abs()))

        # Back calulcate Enter price. Only applicale to out deal
        df['_exp_en_price'] = df.Price - (df.Profit_Pip/(-df.Type*get_pippoint(Symbol))) # -df.Type here because -1 for deal out for Long postiin

        df['_eqaul_prev'] = abs(df._exp_en_price - df.Price.shift(1)) <= 0.5/get_pippoint(Symbol)
        df['in_id'] = df.index-1 # Majority are linked to above deal

        deal_in_taken = df[(df.Direction=='out')&df._eqaul_prev].in_id.values
        deal_in_left = df[(df.Direction=='in')&(~df.index.isin(deal_in_taken))].index.values

        issue_df = df[(~df._eqaul_prev)&(df.Direction=='out')]

        # Loop back index to find matching deal in
        not_match_out_id = []
        for out_id, row in issue_df.iterrows():
            found = False
            for candidate_in_id in deal_in_left[deal_in_left<out_id]:
                if abs(row._exp_en_price - df.loc[candidate_in_id].Price) <= 0.5/get_pippoint(Symbol):
                    found = True
                    df.loc[out_id, 'in_id'] = candidate_in_id
            if not found:
                not_match_out_id += [out_id]
        if len(not_match_out_id) > 0:
            print(f' {Symbol} Deal in not found for dea out ids {not_match_out_id}')

        deal_out = df[df.Direction=='out']
        deal_in = df.loc[deal_out.in_id.values]
        deal_in.reset_index(drop=True, inplace=True)
        deal_out.reset_index(drop=True, inplace=True)

        deal_in.rename(columns={'Time': 'En_Time', 'Price': 'En_Price'}, inplace=True)
        deal_in = deal_in[['En_Time', 'En_Price','Symbol', 'Volume']]

        deal_out.rename(columns={'Time': 'Ex_Time', 'Price': 'Ex_Price'}, inplace=True)
        deal_out = deal_out[['Ex_Time', 'Ex_Price', 'Profit_Pip']]

        positions = deal_in.join(deal_out)
        positions['Unitlot_PnL'] = positions.Profit_Pip * PIP_VALUE[Symbol] - self.comm 
        #assert ((np.sign(positions.Unitlot_PnL) * np.sign(positions.Profit_Pip))==1).sum() == len(positions)
        return positions[self._position_cols]

    def _get_quarter_margin(self):
        # Build a 15 minute based unit margin usage unleveraged
        # Only timeindex is fine, with occupation from previous 15m to current,
        # Forexample 1:15 means position holds from 1:00 - 1:15
        # Round down to nearest quarter hour for enter time
        # Round up to nearest quarter hour for exit time
        round_early = lambda dt: datetime(dt.year, dt.month, dt.day, dt.hour, 15*(dt.minute // 15))
        ent_early = self._positions.En_Time.apply(round_early).values
        ext_late = (self._positions.Ex_Time + pd.Timedelta('15m')).apply(round_early).values

        time_index = pd.DatetimeIndex([])
        for en_t, ex_t in zip(ent_early, ext_late):
            
            ti = pd.date_range(en_t, ex_t, freq='15Min', closed='right')
            time_index = time_index.append(ti)

        margin = pd.Series(time_index, name=self.name).value_counts() * MARGIN_UNIT[self.Symbol]
        self._quarter_margin = margin.to_frame()

    
    

class BTReportReader:
    '''
    Backtester HTML report reader. 

    It parses Backtest info, set info, trades from html. 


    {EA name}_{Trade symbol}_{Trade Timeframe}_{Sefile name}
    '''
    # unit buying power, to calculate UniMargin_PnL, UniMargin_Volume
    UNITMARGIN = 10000 


    def __init__(self, fn, project_dir=None, comm=6, save_set=False):
        self.fn = fn = Path(fn)
        self.project_dir = project_dir
        print(self.fn)
        self.save_set = save_set
        self.comm = comm
        self.success = True
        self.reason = ''

        # Check if its mt4 or mt5, by  lines
        # mt5: <meta name="generator" content="strategy tester">
        # mt4: <meta name="generator" content="MetaQuotes Software Corp.">
        try:
            f = Path(fn).open('r', encoding='utf-16')
            f.readline()
        except:
            f = Path(fn).open('r', encoding='utf-8')
        
        counter = 0
        while True:
            content = f.readline()
            if 'meta' in content:
                if 'strategy' in content:
                    self.MT = 5
                else:
                    self.MT = 4
                break
            counter += 1
            if counter >= 10:
                self.success = False
                self.reason = f'Failed to detect metatrader version, the file may corrupt'
                return


        try:
            report = pd.read_html(str(fn.absolute()))
            if self.MT == 5:
                try:
                    self._read_stat_mt5(report[0])
                except Exception as e:
                    print(f'Error parse stats: {e}')
                self._read_trades_mt5(report[1])
            else:
                self.comm = 0
                self._read_stat_mt4(report[0])
                self._charts = [Chart(self.ChartName0, report[1], self.Symbol0, comm=0, mt5=False)]
                
        except Exception as e:
            import traceback
            print(f">>>{traceback.format_exc()}")
            print(f'{fn} Report Reading failed Error: {e}"')
            self.success = False
            self.reason = str(e)

    def _read_stat_mt4(self, df_stat):
        f =  self.fn.open('r')
        while True:
            content = f.readline()
            if '<title>' in content:
                # Assumes EA name contained in line such as
                # '    <title>Strategy Tester: R Factor V1.72</title>\n'
                f.close()
                break
        try:
            self.EA = content.split('Strategy Tester: ')[1].split('</title>')[0]  
        except:
            self.EA = 'UnkownEA_'+self.fn.name
            print(f'Parse Mt4 EA name failed, last content: {content}  set EA name to {self.EA}')
        
        period_str = df_stat.iloc[1, 2]
        period_str = period_str.split('(')[1].split(')')
        self.BTTimeframe = period_str[0]
        date_range = period_str[1].split('-')
        BTStart = pd.to_datetime(date_range[0]).date()
        BTEnd = pd.to_datetime(date_range[1]).date()

        self.Symbol0 = BTSymbol = df_stat.iloc[0, 2].split('(')[0].replace(' ','')
        self.bt_info = {
                    'EA': self.EA,
                    'BTTimeframe': self.BTTimeframe,
                    'BTSymbol': BTSymbol,
                    'BTStart': str(BTStart),
                    'BTEnd': str(BTEnd),
                    'RawFile': self.fn
                }
        
        self.set_list = df_stat.loc[3, 2].split('; ')


        
        self.ChartName0 = f'{self.EA}_{standardize_symbol(BTSymbol)}_{self.BTTimeframe}_{self.Symbol0}'


    def _read_stat_mt5(self, df_stat):
        '''
        Read backtest info, and set list
        '''
        #print(df_stat)
        initial_deposit = df_stat.loc[df_stat[df_stat[0]=='Initial Deposit:'].index[0],3]

        BTQuality = df_stat.loc[df_stat[df_stat[0]=='History Quality:'].index[0],3] # On mac it was 3
        #print(df_stat.loc[df_stat[df_stat[0]=='History Quality:'].index[0]])
        BTQuality = float(BTQuality.split('%')[0])
        if BTQuality < 99:
            print(f'!!!WAARNING!!! Low repoort quality {BTQuality} %  for report: {self.fn} ')
        self.BTQuality = BTQuality

        set_start = df_stat[df_stat[0]=='Settings'].index[0] + 1 

        b_str = 'Broker:' if 'Broker' in df_stat[0].unique() else 'Company:'
        set_end = df_stat[df_stat[0]==b_str].index[0] - 1
        df_set = df_stat.loc[set_start:set_end, 3]
        self.currency = df_stat[df_stat[0]=='Currency:'][3].iat[0]

        self.EA = df_set.iat[0]
        BTSymbol = df_set.iat[1]
        self.BTTimeframe = df_set.iat[2].split('(')[0].replace(' ','')
        BTStart = df_set.iat[2].split('(')[1].split(' - ')[0]
        BTEnd = df_set.iat[2].split(' - ')[1][:-1]

        self.set_list = df_stat.loc[set_start+3:set_end, 3].values
        self.bt_info = {
            'EA': self.EA,
            'Initial_deposit': int(float(initial_deposit.replace(' ',''))),
            'BTTimeframe': self.BTTimeframe,
            'BTSymbol': BTSymbol,
            'BTStart': BTStart,
            'BTEnd': BTEnd,
            'RawFile': self.fn
        }


    @property
    def charts(self) -> list:
        '''
        List of Chart objects
        '''
        return self._charts

    @property
    def chart0(self):
        '''
        Return the first chart
        '''
        return self.charts[0]
    
    @property
    def position0(self):
        '''
        Return the position of the first chart
        '''
        return self.chart0.position


    def _read_trades_mt5(self, df_deal):
        '''
        Reads deals, then create Posistion Object for each symbol. 
        Give each Position a unique name
        '''
        #assert len(df_deal) > 10, f'Too few trades {len(df_deal)}'
        for i, v in df_deal[1].items():
            if v == 'Deals':
                break
        
        i = df_deal[df_deal[1]=='Deals'].index[0]
        df_deal = df_deal.iloc[i+1:]
        df_deal = df_deal.rename(columns=df_deal.iloc[0].to_dict())
        df_deal = df_deal[df_deal.Type.isin(['buy','sell'])]

        df_deal['Time'] = pd.to_datetime(df_deal.Time)
        for col in ['Volume', 'Price', 'Commission', 'Swap', 'Profit']:
            df_deal[col] = df_deal[col].apply(lambda s: s.replace(' ','')).astype(float)
        
        self._charts = []
        for Symbol, df in df_deal.groupby('Symbol'):
            name = Symbol
            self._charts += [Chart(name, df, Symbol, currency=self.currency, comm=self.comm)]

    



