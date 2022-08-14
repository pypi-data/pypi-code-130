#!/usr/bin/env python
# coding: utf-8
"""
for rolling updates:
    - python3 setup.py bdist_wheel sdist
    - twine upload dist/*

"""
from welcome_page import *
from variables import *
from import_funcs import *
import pandas as pd 
import numpy as np
import re
from tqdm import tqdm
from datetime import datetime
# from sklearn.model_selection import train_test_split
# from sklearn.model_selection import KFold
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import mean_squared_error
# from xgboost import XGBClassifier
# import statistics
# import lightgbm as lgb
# import sys
from joblib import Parallel, delayed
# import warnings
# warnings.simplefilter(action='ignore', category=FutureWarning)
import os
# import multiprocessing



    

def activate_key(key_path):
    if key_path == None:
        return 0
    try:
        key_active_date = pd.read_pickle(key_path)
    except:
        print("The file you have entered is invalid. Pleas enter a valid file path or contact us at hello@linkedlabs.co")
        return 0
    pd.to_pickle(key_active_date,"key.nas")
    if datetime.today().date() > pd.to_datetime(str(key_active_date)).date():
        return 1
    else:
        print(f"Your subscription has expired on {key_active_date}")
        return 0




def get_key(key_path):
    try:
        if "key.nas" in os.listdir("./"):
            key_active_date = pd.read_pickle("key.nas")
            if datetime.today().date() > pd.to_datetime(str(key_active_date)).date():
                return 1
            else:
                return 0
        else:
            return 0
    except:
        pass
    return activate_key(key_path)



def get_internal_similarities(df,activation_key_path = None):
    account_activated = get_key(activation_key_path)
    df = df.rename(columns = lambda x:re.sub('[^A-Za-z0-9_]+', '', x))
    if account_activated == 0:
        df = df.head(2000).copy()
        print("This is a free version, and supports only upto 2000 rows. Remaining data will be truncated!")
        print("For commercial usage please mail us at hello@linkedlabs.co")
    untouched_df = df.copy()
    lis = df.columns
    cat,num,other = cato_numo_other(df)
    for i in cat+num:
        if(df[i].isnull().any()):
            if i in cat:
                df = missing_value_treatment(df,i,cat,num,other,"cat")
            elif i in num:
                df = missing_value_treatment(df,i,cat,num,other,"num")
    df.drop(columns=other,inplace=True)
    features_we_considered = df.columns
    bins = int(np.log(df.shape[0]))
    for _ in num:
        df[_] = pd.qcut(df[_],bins,duplicates="drop")
    # convert all the catagorical col whose no of cat is greater then 2% then tag it into others 
    # one hot encode the whole df
    df = pd.get_dummies(data=df, columns=df.columns)
    assert df.shape[0] == untouched_df.shape[0]
    df.reset_index(inplace=True,drop=True)
    untouched_df.reset_index(inplace=True,drop=True)
    r = Parallel(n_jobs=os.cpu_count()*2, verbose=0)(delayed(get_most_similar_vectors)(df.iloc[_].to_numpy(),df.to_numpy(),_) for _ in tqdm(df.index.values))
    df_scores = pd.concat([pd.DataFrame.from_dict(x, orient='index') for x in tqdm(r)])
    df_scores.reset_index(inplace=True,drop=True)
    df_scores.columns = ["best_similarity_score","best_similar_with_index_number","first_array","similar_array"]
    fin_df = pd.concat([untouched_df,df_scores[["best_similarity_score","best_similar_with_index_number"]]],axis=1)
    # clear()
    # print("your similarity scores are stored in 'best_similarity_score' column and it is most similar with row number stored in 'best_similar_with_index_number' column.(you can use .iloc[index_num] to look at the similar value)")
    return fin_df
def get_similarities(df1,df2,activation_key_path = None):
    df1 = df1.rename(columns = lambda x:re.sub('[^A-Za-z0-9_]+', '', x))
    df2 = df2.rename(columns = lambda x:re.sub('[^A-Za-z0-9_]+', '', x))
    account_activated = get_key(activation_key_path)
    if account_activated == 0:
        df1 = df1.head(1000)
        df2 = df2.head(5000)
        print("########################")
        print("This is a free version, and supports only upto 1000 rows and will be compared against first 5000 rows in the 2nd dataframe. Remaining data will be truncated!")
        print("For commercial usage please mail us at hello@linkedlabs.co")
        print("------------------------")
    org_df1 = df1.copy()
    org_df2 = df2.copy()
    if set(df1.columns) != set(df2.columns):
        print("columns of both dataframes are different!")
        exit()
    df1.loc[:,"which_df"]= 'df1'
    df2.loc[:,"which_df"]='df2'
    df = pd.concat([df1, df2], ignore_index=True)
    # df =df1.append(df2)
    untouched_df = df1.copy()
    untouched_df_2 = df2.copy()
    cat,num,other = cato_numo_other(df)
    for i in cat+num:
        if(df[i].isnull().any()):
            # print(i)
            if i in cat:
                df = missing_value_treatment(df,i,cat,num,other,"cat")
            elif i in num:
                df = missing_value_treatment(df,i,cat,num,other,"num")
    df.drop(columns=other,inplace=True)
    bins = int(np.log(df.shape[0]))
    for _ in num:
        df[_] = pd.qcut(df[_],bins,duplicates="drop")
    df = pd.get_dummies(data=df, columns=df.columns)
    df1 = df.loc[df['which_df_df1'] ==1,:]
    df2=df.loc[df['which_df_df2']==1,:]
    df1.drop(['which_df_df1','which_df_df2'],axis=1,inplace=True)
    df2.drop(['which_df_df1','which_df_df2'],axis=1,inplace=True)
    df1.reset_index(inplace=True,drop=True)
    df2.reset_index(inplace=True,drop=True)
    untouched_df.reset_index(inplace=True,drop=True)
    untouched_df_2.reset_index(inplace=True,drop=True)
    r = Parallel(n_jobs=os.cpu_count()*2, verbose=0)(delayed(get_most_similar_vectors_multi_df)(df1.iloc[_].to_numpy(),df2.to_numpy(),_) for _ in tqdm(df1.index.values))
    df_scores = pd.concat([pd.DataFrame.from_dict(x, orient='index') for x in tqdm(r)])
    df_scores.reset_index(inplace=True,drop=True)
    df_scores.columns = ["best_similarity_score","best_similar_with_index_number","first_array","similar_array"]
    fin_df = pd.concat([untouched_df,df_scores[["best_similarity_score","best_similar_with_index_number"]]],axis=1)
    fin_df.drop(['which_df'],axis=1,inplace=True)
    untouched_df_2.drop(['which_df'],axis=1,inplace=True)
    return fin_df , untouched_df_2
