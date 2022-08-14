from variables import *
# from import_funcs import *
import pandas as pd 
import numpy as np
# import re
from tqdm import tqdm
# from sklearn.model_selection import train_test_split
# from sklearn.model_selection import KFold
# from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
# from xgboost import XGBClassifier
import statistics
import lightgbm as lgb
# import sys
# from joblib import Parallel, delayed
from os import system, name
# import warnings
# warnings.simplefilter(action='ignore', category=FutureWarning)

# define our clear function
def clear():
  
    # for windows
    if name == 'nt':
        _ = system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

# ## Detect Categories



def other_to_cat(df,cato,oth):
    temp_other = oth
    for i in tqdm(temp_other):
        percent_head_val = int(head_for_category_cut * df[i].nunique())
        df.loc[~df[i].isin(df[i].value_counts().head(percent_head_val).index),i]='other'
        if(other_category_cut * df[df[i] != 'other'].shape[0] >= df[df[i] == 'other'].shape[0]):
            cato.append(i)
            oth.remove(i)
        else:
            pass   
    return cato,oth




def cato_numo_other(data,cato=[],num=[]):
    data.dropna(axis=1, how='all',inplace=True)
    data_cols = data.columns
    other = list(set(data_cols)- set(cato+num))
    if len(cato) != 0 and len(num) !=0:
        return cato,num,[]
    oth=[]
    for i in other:
        percent_unique = (data[i].nunique()/data.shape[0])*100
        try:
            t=data[i].dropna().astype(float)
            if(percent_unique > cat_cut_of_pec):   
                mean_of_col=data[i].mean()
                if((statistics.mode(data[i].diff(1)) ==1) or (statistics.mode(data[i].diff(1)) == -1)):
                    oth.append(i)
                elif("id" in i.lower() or "key" in i.lower()):
                    oth.append(i)   
                elif mean_of_col > 1000000000:
                    oth.append(i)
                else:
                    num.append(i)
            else:
                cato.append(i)
        except:
            if(percent_unique > cat_cut_of_pec):
                oth.append(i)
            else:
                cato.append(i)
    cato_f,oth_f = other_to_cat(data,cato,oth)
    return cato_f,num,oth_f

# ## missing value treatment


def missing_value_treatment(df,col,cato,num,oth,which_cat):
    ddf=df.copy()
    y_pred_rf=[]
    y_true_rf=[]
    features = df.columns[~df.isna().any()].tolist()
    filter_features = list(set(features) - set(oth))
    cato_filter   = list(set(filter_features).intersection(set(cato)))
    null_filters = df.columns[df.isna().any()].tolist()
    null_filters_cato = list(set(null_filters).intersection(set(cato)))
    df=pd.get_dummies(data=df, columns=cato_filter)
    one_hot_filter_features = list(set(df.columns) - set(oth).union(set(null_filters)))
    not_null_df = df[~df[col].isnull()].copy()
    null_df = df[df[col].isnull()].copy()
    X_train = not_null_df[one_hot_filter_features]
    y_train = not_null_df[col].to_numpy()
    X_test = null_df[one_hot_filter_features].to_numpy()
    y_test = null_df[col].to_numpy()
    if which_cat == "num":
        model = lgb.LGBMRegressor()
    else:
        model = lgb.LGBMClassifier()
    lgb_model = model.fit(X_train,y_train)
    df_missing=lgb_model.predict(X_test)
    nn_df = ddf[ddf[col].notnull()].copy()
    n_df = ddf[ddf[col].isnull()].copy()
    n_df[col] = df_missing
    nn_df = pd.concat([nn_df, n_df], ignore_index=True)
    # nn_df = nn_df.append(n_df)
    nn_df.sort_index(inplace=True)
    return nn_df

def modified_nucleotide_dictance(arr1,arr2):
    assert len(arr1) == len(arr2)
    dissimilarity_score = np.sum(list(map(lambda x:x[0]+x[1],filter(lambda x:(x[0] != x[1]),zip(arr1,arr2)))))
    similarity_score = np.sum(list(map(lambda x:x[0]+x[1],filter(lambda x:(x[0] == x[1]) and ((x[0] !=0) and (x[1] !=0))
                                                                 ,zip(arr1,arr2)))))
    return (similarity_score)/(similarity_score+dissimilarity_score)


def get_most_similar_vectors(nc_arr,c_matrix,position):
    a = list(map(lambda x:modified_nucleotide_dictance(nc_arr,x),c_matrix))
    a[position]=0
    score = max(a)
    most_similar_credit_position = a.index(score)
    return {position:[score , most_similar_credit_position,nc_arr,c_matrix[most_similar_credit_position]]}
def get_most_similar_vectors_multi_df(nc_arr,c_matrix,position):
    a = list(map(lambda x:modified_nucleotide_dictance(nc_arr,x),c_matrix))
    score = max(a)
    most_similar_credit_position = a.index(score)
    return {position:[score , most_similar_credit_position,nc_arr,c_matrix[most_similar_credit_position]]}