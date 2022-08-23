# -*- coding: utf-8 -*-

from dtw import dtw # https://dynamictimewarping.github.io/
from dtw import rabinerJuangStepPattern


def CandleSimilar(df1, df2, cols, std01=True):
    '''
    计算K线相似度，df1和df2应包含K线列cols
    '''
    if std01:
        df1, df2 = df1.copy(), df2.copy()
        for col in cols:
            vmin1, vmax1 = df1[col].min(), df1[col].max()
            df1[col] = (df1[col] - vmin1) / (vmax1 - vmin1)
            vmin2, vmax2 = df2[col].min(), df2[col].max()
            df2[col] = (df2[col] - vmin2) / (vmax2 - vmin2)
    alignment = dtw(df1[cols], df2[cols])
    Sim = alignment.distance
    stdSim = alignment.normalizedDistance
    return stdSim, Sim 
    
    
if __name__ == '__main__':
    import time
    import pandas as pd
    from utils_hoo import load_csv, plot_Series
    from utils_hoo.utils_plot.plot_Candle import plot_Candle  
    
    strt_tm = time.time()
    
    # test
    df1 = pd.DataFrame({'close':
                        [1, 2, 0, 1, 1, 2, 0, 1, 1, 2, 0, 1, 1, 2, 0, 1]})
    df2 = pd.DataFrame({'close':
                        [0, 1, 1, 2, 0, 1, 1, 2, 0, 1, 1, 2, 0, 1, 1, 2]})
    df3 = pd.DataFrame({'close': [0.8, 1.5, 0, 1.2, 0, 0, 0.6, 1, 1.2, 0, 0,
                                  1, 0.2, 2.4, 0.5, 0.4]})
    df4 = pd.DataFrame({'close': [1, 2, 3, 4]})
    df5 = pd.DataFrame({'close': [5, 4, 3, 2]})
    plot_Series(df1, {'close': '.-k'}, figsize=(6, 3), nXticks=4)
    plot_Series(df2, {'close': '.-k'}, figsize=(6, 3), nXticks=4)
    plot_Series(df3, {'close': '.-k'}, figsize=(6, 3), nXticks=4)
    plot_Series(df4, {'close': '.-k'}, figsize=(6, 3), nXticks=4)
    plot_Series(df5, {'close': '.-k'}, figsize=(6, 3), nXticks=4)
    print(CandleSimilar(df1, df2, ['close']))
    print(CandleSimilar(df1, df3, ['close']))
    print(CandleSimilar(df4, df5, ['close']))
    
    
    # 50ETF日线行情
    fpath = '../test/510050_daily_pre_fq.csv'
    df = load_csv(fpath)
    df['time'] = df['date']
    df.set_index('date', drop=True, inplace=True)
    df = df.reindex(columns=['time', 'open', 'low', 'high', 'close', 'volume'])
    
    df1 = df.iloc[-50:-42, :]
    df2 = df.iloc[-40:-32:, :]
    plot_Candle(df1, N=df1.shape[0], args_ma=None, args_boll=None,
                plot_below=None, figsize=(6, 4))
    plot_Candle(df2, N=df2.shape[0], args_ma=None, args_boll=None,
                plot_below=None, figsize=(6, 4))
    plot_Series(df1, {'close': '.-k'}, figsize=(6, 3), nXticks=4)
    plot_Series(df2, {'close': '.-k'}, figsize=(6, 3), nXticks=4)    
    
    print(CandleSimilar(df1, df2, ['close', 'high', 'low', 'open']))   


    
    print(f'used time: {round(time.time()-strt_tm, 6)}s.')
    
    
    
    
    
    
    
