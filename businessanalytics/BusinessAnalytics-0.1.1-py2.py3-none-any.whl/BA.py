import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

from datetime import datetime 
import time

def hello():
    print("Hello, world!")

def plot(data:pd.DataFrame, x:str, y:str, z:str=None,  plot_type:str="line", size=(9,6),
        title:str=None,
        xlabel:str=None,
        ylabel:str=None):
    
    fig, ax = plt.subplots(figsize=size)
    _x, _y = data[x], data[y]

    # Apply plot type
    if plot_type == "line": ax.plot(_x, _y)
    if plot_type == "bar": ax.bar(_x, _y)
    if plot_type == "scatter": ax.scatter(_x, _y)
    
    # Apply labeling
    if title: ax.set_title(title)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)

    # Apply formatting
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

def load_stockdata(ticker: str, frequency: str, start:str, end:str):
    '''
    Funktion, um Aktiendaten über Yahoo-Finance zu laden.

    Input:
    - ticker: Kennung der Aktie gemäß Yahoo-Finance
    - frequency: Häufigkeit der Daten, d.h. z.B. tägliche oder wöchentliche Kurse
    - start: Anfangsdatum
    - end: Enddatum

    Output: Dataframe mit Yahoo-Finance-Daten für die jeweiligen Angaben
    '''


    #ticker = ticker.replace("^", "%5E")

    # Convert start and end date into 10-digit time format
    start = datetime.strptime(start, "%m-%d-%Y").strftime('%s')
    #start = int(start)
    
    end = datetime.strptime(end, "%m-%d-%Y").strftime('%s')
    #end = int(end)
    
    _base_url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={start}&period2={end}&interval={frequency}&events=history&includeAdjustedClose=true'

    try:
        df = pd.read_csv(_base_url, parse_dates=["Date"])
        return df
    except:
        print("Fehler: Daten konnten nicht geladen. Stellen Sie sicher, dass die Eingaben korrekt sind.")
    
    return None 

