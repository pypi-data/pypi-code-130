import sys
import pandas as pd
import numpy as np
from preproc_utils import MyJsonObject, replaceOrAddColumn

def column_name_mapping_after_groupby(orgdf, resdf, method):
    """
    if "by" == ['gender', 'age']
        ORG <= ['student', 'gender', 'age', 'math', 'society']
        RES <= ['student', 'math', 'society']

    """
    print("ORG", list(orgdf.columns))
    print("RES", list(resdf.columns))
    org_names = list(resdf.columns)
    new_names = [col+'_' + method for col in org_names]
    return dict(zip(org_names, new_names))

def GroupBy(df:pd.DataFrame, columnName:str, method:str):
    # 전처리 메타 생성

    groupby = df.groupby(columnName)

    if method == 'MEAN':
        resdf = groupby.mean()
    elif method == 'SUM':
        resdf = groupby.sum()
    elif method == 'COUNT':
        resdf = groupby.count()
    elif method == 'MAX':
        resdf = groupby.max()
    elif method == 'MIN':
        resdf = groupby.min()

    name_mapping = column_name_mapping_after_groupby(df, resdf, method)
    print("MAPPING", name_mapping)
    resdf.rename(columns=name_mapping, inplace=True)


    # 전처리 컬럼 및 메타 수정
    resdf = resdf.reset_index()

    meta = MyJsonObject({
        "name": "GroupBy", 
        "columnName": columnName,
        "newColumn": list(name_mapping.values()),
        "isTest":True}
    )
    print(meta.__dict__)
    # meta.setMany({
    #     "newMin": new_min, "newMax": new_max,
    #     "newMean": new_avg, "newStdDev": new_stddev
    # })

    return [meta.__dict__, resdf]


if __name__=="__main__":
    df = pd.read_csv('../dataset/nan.csv')
    # result = StandardScaler(df, "tenure", False)
    # result = MinMaxScaler(df, "TotalCharges", False)
    # result = RobustScaler(df, "Partner", False)
    # result = LogScaler(df, "Partner", False)
    # result = ExpScaler(df, "Dependents", False)
    # result = GroupBy(df, "customerID", "MAX")
    # import pprint
    # print('meta정보 : ', result[0])
    # print('========')
    # print('dataframe :\n', result[1])
        
    # result = GroupBy(df, "gender", "MEAN")
    # df2 = result[1]
    # print(df2.describe())
    # print(list(df2.columns))

    df = pd.read_csv('../dataset/people.csv')
    result = GroupBy(df, ["gender", "age"], "MEAN")
    # result = GroupBy(df, ["gender"], "MEAN")
    df2 = result[1]
    print(df2)
    # print(df2.describe())
    print(list(df2.columns))