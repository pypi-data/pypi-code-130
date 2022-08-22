import pandas as pd
from pandas.tseries.offsets import BDay
from datetime import datetime, timedelta 
from typing import Union, List

def _yahoo_stockdata(ticker:str, start:str=None, end:str=None, periods:str=None) -> pd.DataFrame:
    '''Lädt tägliche Aktiendaten über Yahoo-Finance in einen Dataframe

    Input:
    - ticker: Kennung der Aktie gemäß Yahoo-Finance
    - start: Anfangsdatum (dd-mm-yyyy)
    - end: Enddatum (dd-mm-yyyy)

    Output: Dataframe mit Yahoo-Finance-Daten für die jeweiligen Angaben
    '''

    frequency = "1d"

    if  not ((start and end) or (start and periods) or (end and periods)):
        raise ValueError("Fehler: Werte für zwei Parameter (start, end, periods) andgeben")

    if periods:
        if start: 
            start = pd.to_datetime(start, format="%d-%m-%Y") #"#datetime.strptime(start, "%d-%m-%Y") 
            end = start + BDay(periods)
        elif end: 
            end = pd.to_datetime(end, format="%d-%m-%Y")
            start = end - BDay(periods)
        else:
            raise ValueError("Irgendetwas ist schief gelaufen....")
    else:
        start = pd.to_datetime(start, format="%d-%m-%Y")
        end = pd.to_datetime(end, format="%d-%m-%Y")
    
    # Convert start and end date into 10-digit time format
    start = start.strftime('%s')
    end = end.strftime('%s')
    
    _base_url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={start}&period2={end}&interval={frequency}&events=history&includeAdjustedClose=true'

    try:
        df = pd.read_csv(_base_url, parse_dates=["Date"])
        return df
    except:
        raise ValueError("Fehler: Daten konnten nicht geladen. Stellen Sie sicher, dass die Eingaben korrekt sind.")
    
    return None 

def get_stock_data(ticker:Union[str, List], start:str=None, end:str=None, periods:str=None) -> pd.DataFrame:

    if not isinstance(ticker, list): ticker = [ticker]

    data = [(_yahoo_stockdata(t, start, end, periods) 
            .assign(ticker=t))
            for t in ticker]

    _df = pd.concat(data, axis=0).reset_index(drop=True)

    return _df.sort_values(by="Date")


