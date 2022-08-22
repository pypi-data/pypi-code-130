
import requests
import io

import pandas as pd

RET_COLS = ['En_Time', 'Volume', 'Symbol', 'En_Price',
            'Ex_Time', 'Ex_Price', 'Swap', 'Profit']


def _read_from_url(url:str) -> pd.DataFrame:
    """
    Given mql5 signal url, download the trade history and return as a DataFrame.
    If not successed, return `None`.
    Args:
        url (str): url of mql5 signal. 
    
    Return:
        pd.DataFrame: trade history.
    """
    ## Parse signal id from provided url

    if not 'signals' in url or not 'www.mql5.com' in url:
        print(f'Wrong signal url: {url}')
        return 
    sid = url.split('signals/')[1].split('/')[0].split('?')[0]
    download_url = f"https://www.mql5.com/en/signals/{sid}/export/history"

    # Use hardcoded auth
    auth = "1JUVntng32y-0DUNaTQI7GEUUtUzWVIheCDdpNAM5GWr7IIXjVNwh1IqX7I-jGlpCNGQgiG_fe0j2Rk0IlFkb-5Os-oE9eEegysBDF1wNjOVyCNHM-bNrrDzofYOXIHQ8G__IaguWLHIErJPPIqCUw"
    try:
        response = requests.get(url=download_url, headers={
            "cookie": f"auth={auth}"
        })
        return pd.read_csv(io.StringIO(str(response.content, 'utf-8')), sep=';')
    except Exception as e:
        print(f'Download file from {download_url} failed : {e}')
        return 



def read_mql5(fn_or_url: str, gmt=3) -> pd.DataFrame:
    """
    Read mql5 signal histroy. Given either csv file downloaded from mql5 or the raw signal address.

    Args:
        fn_or_url (str): path to csv file or url address of mql5 signal.
        gmt (int, optional): The signal timezone. Defaults to 3.

    Returns:
        pd.DataFrame: trade history with timezone aligned to GMT3.

    """
    if '.csv' in fn_or_url:
        raw_hist = pd.read_csv(fn_or_url, sep=';')
    else:
        raw_hist = _read_from_url(fn_or_url)
        if raw_hist is None:
            return 

    col_maps = {
        'Time': 'En_Time',
        'Price': 'En_Price',
        'Time.1': 'Ex_Time',
        'Price.1': 'Ex_Price'
    }
    raw_hist = raw_hist.rename(columns=col_maps)

    raw_hist['Swap'] = raw_hist['Swap'].fillna(0)
    raw_hist['Commission'] = raw_hist['Commission'].fillna(0)

    for col in ['En_Price', 'Ex_Price', 'Commission', 'Swap', 'Profit']:
        if col not in raw_hist.columns: continue
        raw_hist[col] = raw_hist[col].apply(lambda p: float(str(p).replace(" ","")))
    
    raw_hist.loc[raw_hist['Type'] == 'Buy', 'Type'] = 1
    raw_hist.loc[raw_hist['Type'] == 'Sell', 'Type'] = -1
    raw_hist = raw_hist[raw_hist['Type'].isin([1,-1])]

    raw_hist['Volume'] = raw_hist['Type'] * raw_hist['Volume']

    return raw_hist[RET_COLS]