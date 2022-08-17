#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 31 11:51:59 2021

@author: David Grant

dependency on plotly , pandas 
"""

import plotly.express as px
import pandas as pd
import os
import csv
import configparser
import logging , logging.config
from pathlib import Path
 
logger = logging.getLogger(__name__)
                 

config = configparser.ConfigParser()
configfound = False 
for loc in os.curdir, os.path.expanduser("~/spend"), "/etc/spendingizer", os.environ.get("SPENDINGIZER_CONF"):
  
  if loc != None:
      conffile = os.path.join(loc,"spendingizer.conf") 
      path = Path(conffile)
      try:
          my_abs_path = path.resolve(strict=True)
      except FileNotFoundError:
          pass
      else:
          # exists
          print('found ',conffile)
          configfound = True
          config.read(conffile)

if not configfound:
    raise Exception("No configuration file found")
    
config.sections()
statement = config['SP']['statements']
catagories = config['SP']['catagories']
wildfile = config['SP']['wildcards']
extras = config['SP']['extras']    

def LoadStatements(path):  
    spending = pd.DataFrame() 
    filecount = 0 
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            path = os.path.join(root, filename)
            logger.info('Processing file: %s',filename)
            spending = spending.append(pd.read_csv(path,encoding='ISO-8859-1'))
            filecount += 1
    
    if filecount == 0:
        raise ValueError('no files to process')
    
    logger.info('Files loaded to value of %s',spending['Amount'].sum())  
    spending.drop(spending.filter(regex="Unname"),axis=1, inplace=True)
    # spending.drop(spending.filter(regex="Balance"),axis=1, inplace=True)
    return spending

def FormatStatements(spending,catfile):
   # Fix data types, trailing spaces, remove flow thru cash transactions sort categories 
    spending['Date'] = pd.to_datetime(spending['Date'], format = '%d/%m/%Y')
    spending['Month'] = spending['Date'].dt.strftime('%Y-%m')
    spending['Description'] = spending['Description'].str.replace(' ', '')
    spending['Amount'] *= -1
    spending.loc[(spending.Description.str.contains('NETWEALTH')),'Amount'] = 99999
    spending.loc[(spending.Description.str.contains('FUNDSTRANSFERRB')),'Amount'] = 99999
    spending.drop(spending[spending.Amount > 99998].index, inplace=True)
    category = pd.read_csv(catfile)
    category['Description'] = category['Description'].str.replace(' ', '')
    category.drop_duplicates(inplace=True)
    result = pd.merge(spending,category,on='Description',how='left')
    #spending is depicted as negative balance so swap yo positive
    
    reader = csv.reader(open(wildfile))
    for row in reader:
        result.loc[(result.Description.str.contains(row[0])),'Category'] = row[1]
    
    result['Category'].fillna('Other', inplace=True)
    logger.info('FormatStatement value %s',result['Amount'].sum())
    return result 

def GetMonths(df):
    rr2 = df.groupby(['Month','Category'])['Amount'].sum().unstack()
    rr2.reset_index
    rr2['Month'] = rr2.index
    data_top = rr2.head(10000)
    monty = []
    for index, row in data_top.iterrows():
        monty.append(row['Month'])
    
    logger.info('GetMonth returns # %s months',len(monty))
    return monty   

def GetLastQtr(mts):
    mtsidx = (-3,-2,-1)
    lastq = []
    for month in mtsidx:
        lastq.append(mts[month])
        
    return lastq   

def CheckSizeOtherCat(df,months):
    curmonth = months[-1]
    other = df[(df['Category'] == 'Other') & (df['Month'] == curmonth)]
    logger.info('CheckSizeOtherCat for month %s value %s',curmonth,other.Amount.sum())
    if other.Amount.sum() > 500:
        print('Other category for ',curmonth)
        print('+++++++++++++++++++++++++')
        for index, row in other.iterrows():
            print(row['Description'],row['Amount'])
        
        raise ValueError('Other Category Too large')

def ListOtherCat(df,months):
    curmonth = months[-1]
    otherlist = []
    other = df[(df['Category'] == 'Other') & (df['Month'] == curmonth)]
    for index, row in other.iterrows():
            otherlist.append((row['Description'],row['Amount']))
            
    logger.info('ListOtherCat for month %s value %s',curmonth,other.Amount.sum())
    return otherlist    
    
def RemoveInsuranceClaim(df):
    month_list = ['2020-06','2020-07','2020-08','2020-09','2020-10','2020-11','2020-12']
    cat_list = ['House','Amazon']
    insclaim = df.query('Category in @cat_list and Month in @month_list')
    insclaim['Category'] = 'Ins Claim'
    df.update(insclaim)
    insval = df[(df['Category'] == 'Ins Claim')].Amount.sum()
    logger.info('RemoveInsuranceClaim calculated %s , Val in df %s',insclaim['Amount'].sum(),insval)
    return df

def RemoveBigDeposits(df):
    deposits = df.query('Amount < -500')
    deposits['Category'] = 'Deposits'
    df.update(deposits)
    val = df[(df['Amount'] < -500)].Amount.sum()
    logger.info('RemoveInsuranceClaim calculated %s , Val in df %s',deposits['Amount'].sum(),val)
    return df

def CalcRunRate(df): 
    runrate = df[(df['Category'] == 'Food') |
                     (df['Category'] == 'Utility') |
                     (df['Category'] == 'Travel') |
                     (df['Category'] == 'Entertainment') |
                     (df['Category'] == 'House') |
                     (df['Category'] == 'Health') |
                     (df['Category'] == 'Amazon') |
                     (df['Category'] == 'Personal') |
                     (df['Category'] == 'Bluebell') |
                     (df['Category'] == 'Clothing') |
                     (df['Category'] == 'Other') ]
    return runrate

def AddExtraExpenses(df,extras):
    logger.info('Processing extra expenses file %s',extras)
    try:
        dfext = pd.read_csv(extras)
    except FileNotFoundError:
        logger.warning('No extra expenses file')
        return df
        
    dfext['Day'] = '01'
    dfext['Date'] = pd.to_datetime(dfext[['Year', 'Month','Day']])
    dfext['Month'] = dfext['Date'].dt.strftime('%Y-%m')
    dfext = dfext.drop(['Year','Day'], axis=1)
    df = df.append(dfext)
    logger.info('Expenses added : %s',dfext['Amount'].sum())
    
    return df 

def SpendAnalysis(df,mts):
    """
    Parameters
    ----------
    df : Dataframe of Spending Data
    mts : List of Months incorporated in DF in format YYYY-MM 

    Returns
    -------
    Disctionary : 
        TXT 
        LQTR
        QTRAVG
        LMTH
        MTHAVG 
        CURYR
        YTDSPEND

    """
    LastQtr = GetLastQtr(mts)
    logger.info('QuarterlyAnalysis %s',LastQtr)
    LastQTot = df.query("Month in @LastQtr")['Amount'].sum()
    NumMonths = len(mts)
    Total = df['Amount'].sum()
    MonthlyAvg = Total / NumMonths
    QtrAvg = MonthlyAvg  * 3
    CURYR , YTDSPEND = GetYTDSpend(df,mts)
    LastMonth=mts[-1]
    LastMonthSpend = df.query('Month in @LastMonth')
    LastMonthSUM = round(LastMonthSpend['Amount'].sum(),0)
    NarativeTxt = 'For {0:} YTD Spend is £{1:,.0f} Last Quarter spend £{2:,.0f} v/s average Qtr £{3:,.0f}. Last Month £{4:,.0f} v/s  monthly Average £{5:,.0f}'.format(CURYR,YTDSPEND,LastQTot,QtrAvg,LastMonthSUM,MonthlyAvg)
    SpendData = {"TXT":NarativeTxt,"LQTR":LastQTot,"QTRAVG":QtrAvg,"LMTH":LastMonthSUM,"MTHAVG":MonthlyAvg,"CURYR":CURYR, "YTDSPEND":YTDSPEND}
    logger.info('QuarterlyAnalysis %s',SpendData)
    return SpendData

def PlotMonthlySpend(df):
    df_stack=df.groupby(['Month','Category']).sum().reset_index()
    fig = px.bar(df_stack, x='Month', y='Amount', color = 'Category', barmode='stack')
    fig.update_layout(title = "Monthly Spending By Category")
    logger.info('PlotMonthlySpend')
    return fig 

def GetAnnualSpend(df):
    df['Year'] = df['Date'].dt.strftime('%Y')
    df_stack=df.groupby(['Year'])['Amount'].sum().reset_index()
    return df_stack

def PlotAnnualSpend(df):
    df['Year'] = df['Date'].dt.strftime('%Y')
    df_stack=df.groupby(['Year'])['Amount'].sum().reset_index()
    df_stack['Amount'] = df_stack['Amount'].round(0)
    numyears = df_stack.shape[0] - 1
    totalspend = df['Amount'].sum()
    currentyr = df_stack.iloc[-1,1]
    averagespend=(totalspend - currentyr) / numyears
    latestyear = df['Year'].max()
    
    logger.info('PlotAnnualSpend LatestYr: %s , NumYrs: %s, TotSpend %s, CurrentYr %s, AverageSpend %s',latestyear,numyears,totalspend,currentyr,averagespend)

    fig = px.bar(df_stack, x='Year', y='Amount', barmode='stack', text='Amount' ,width = 500, height = 300)
    fig.update_layout(shapes=[
    # adds line at y=averagespend
    dict(
      type= 'line',
      xref= 'paper', x0= 0, x1= 1,
      yref= 'y', y0= averagespend, y1= averagespend,
    ),
    ])
    
    fig.update_layout(title = "Annual Spending")
    
    return fig

def GetYTDSpend(df,mts):
    """
    Parameters
    ----------
    df : DataFrame of spending
    mts : list of months in format YYYY-MM

    Returns
    -------
    AnnualSpendTUP : A tuple of 
        YEAR  -  the current Year 
        YTD - Spending 

    """
    df['Year'] = df['Date'].dt.strftime('%Y')
    df_stack=df.groupby(['Year'])['Amount'].sum().reset_index()
    df_stack['Amount'] = df_stack['Amount'].round(0)
    latestyear = df['Year'].max()
    YTDMts = [s for s in mts if latestyear in s]
    YTD = df.query('Month in @YTDMts')
    YTDSpend = round(YTD['Amount'].sum(),0)
    print('For %s Spend of %s v/s budget %s',latestyear,YTDSpend)
    logger.info('For %s Spend of %s v/s budget %s',latestyear,YTDSpend)   
    return latestyear , YTDSpend

def PlotQtrCompare(df,mts):
    LastMonths = GetLastQtr(mts)
    lastqtr = df.query('Month in @LastMonths')
    lastqtr_gp = lastqtr.groupby(['Category'])['Amount'].sum().reset_index()
    lastqtr_gp['Type'] = 'Last Quarter'
    avgqtr = df.groupby(['Category'])['Amount'].sum().reset_index()
    avgqtr['Amount'] = avgqtr['Amount'] / len(mts) * 3
    avgqtr['Type'] = 'Average Quarter'
    result = avgqtr.append(lastqtr_gp)
    fig = px.bar(result, x="Type", y="Amount", color="Category", title="Last Quarter Spend Comparison",width = 500, height = 400)
    return fig 
    
def ProcessSpending():
    rawspend = LoadStatements(statement)
    fmtspend = FormatStatements(rawspend,catagories)
    mts = GetMonths(fmtspend)
    netspend = RemoveInsuranceClaim(fmtspend)
    netspend = RemoveBigDeposits(netspend)
    netspend = AddExtraExpenses(netspend,extras)
    CheckSizeOtherCat(netspend,mts)
    netrunrate = CalcRunRate(netspend)
    return netrunrate
    
if __name__ == '__main__':
    print('**** Running Core Spendingizer ****')
    
    runrate = ProcessSpending()
    mts = GetMonths(runrate)
    SpendData = SpendAnalysis(runrate,mts)
    print(SpendData)
    PlotMonthlySpend(runrate)
    Year , YTDSpend = GetYTDSpend(runrate,mts)
    print('YTDSpending ', Year , YTDSpend)
    # Is last quarter spending on budget for year 
    # Manage overheads
    # Project Spend for year within salary 
    
    