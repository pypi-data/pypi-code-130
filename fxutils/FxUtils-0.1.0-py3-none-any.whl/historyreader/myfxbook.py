
import pandas as pd

RET_COLS = ['En_Time', 'Volume', 'Symbol', 'En_Price',
            'Ex_Time', 'Ex_Price', 'Swap', 'Profit']


def read_myfxbook(fn: str) -> pd.DataFrame:
    """Return trade history parsed from myfxbook csv file.
    
    `Profit`: myfxbook's `Profit` column` natively included all.
    """
    raw_hist = pd.read_csv(fn)

    raw_cols = ['Open Date', 'Close Date', 'Symbol', 'Action', 'Units/Lots',
         'Open Price', 'Close Price']

    new_cols = ['En_Time', 'Ex_Time', 'Symbol', 'Type', 'Volume',
                 'En_Price', 'Ex_Price']
    col_maps = {
        k:v for k,v in zip(raw_cols, new_cols)
    }
    raw_hist = raw_hist.rename(columns=col_maps)

    # Myfxbook profit is net profit. we turn into raw profit
    raw_hist['Profit'] -= raw_hist.Commission + raw_hist.Swap

    raw_hist.loc[raw_hist['Type'] == 'Buy', 'Type'] = 1
    raw_hist.loc[raw_hist['Type'] == 'Sell', 'Type'] = -1
    raw_hist = raw_hist[raw_hist['Type'].isin([1,-1])]

    raw_hist['Volume'] = raw_hist['Type'] * raw_hist['Volume']

    return raw_hist[RET_COLS]