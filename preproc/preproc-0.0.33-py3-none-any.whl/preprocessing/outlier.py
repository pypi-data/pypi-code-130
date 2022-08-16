import pandas as pd
import numpy as np
from preproc_utils import MyJsonObject, replaceOrAddColumn

# 이상치 처리 - carling 
# 인자 : dataframe(df), columnName(str), newColumn(bool)
def Carling(df, columnName, newColumn):
    """
    Carling 이상치 처리 공식 : q50 - iqr*2.3 < 정상 < q50 + iqr*2.3
    """
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "Carling", "columnName": columnName})

    # 전처리 값 계산
    q25, q50, q75 = df[columnName].quantile([.25, .5, .75])
    iqr = q75 - q25 # IQR 계산하기
    carlingMultiplier = 2.3 # outlier cutoff 계산하기
    
    # lower와 upper bound 값 구하기
    cut_off = iqr * carlingMultiplier
    lower, upper = q50 - cut_off, q50 + cut_off

    # 이상치 판단
    if newColumn == True:
        def is_outlier_func(x):
            return not (lower <= x and x <= upper)
        newColVal = df[columnName].map(is_outlier_func)
        outlierN = int(newColVal.sum())
        meta.set("isTest", True)
        replaceOrAddColumn(df, newColVal, newColumn, meta)
        
    # 이상치 제거
    else:
        org_df = len(df)
        df = df.loc[df[columnName]<=upper]
        df = df.loc[df[columnName]>=lower]
        outlierN = org_df - len(df) # 이상치 갯수 구하기
        meta.set("isTest", False)

    # 전처리 컬럼 및 메타 수정
    meta.setMany({"q25": float(q25), "q50": float(q50), "q75": float(q75),
                 "lower": float(lower), "upper": float(upper), 
                 "outlierN": int(outlierN)})
    df = df.reset_index(drop=True)
    return [meta.__dict__, df]

# 이상치 처리 - Tukey 
# 인자 : dataframe(df), columnName(str), newColumn(bool)
def Tukey(df, columnName, newColumn):
    """
    tukey 이상치 처리 공식 : q25 - iqr*1.5 < 정상 < q75 + iqr*1.5
    """
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "Tukey", "columnName": columnName})

    # 전처리 값 계산
    q25, q50, q75 = df[columnName].quantile([.25, .5, .75])
    iqr = q75 - q25 # IQR 계산하기
    tukeyMultiplier = 1.5

    # lower와 upper bound 값 구하기
    cut_off = iqr * tukeyMultiplier
    lower, upper = q25 - cut_off, q75 + cut_off
    
    # 이상치 판단
    if newColumn == True:
        def is_outlier_func(x):
            return not (lower <= x and x <= upper)
        newColVal = df[columnName].map(is_outlier_func)
        outlierN = int(newColVal.sum())
        meta.set("isTest", True)
        replaceOrAddColumn(df, newColVal, newColumn, meta)
        
    # 이상치 제거
    else:
        org_df = len(df)
        df = df.loc[df[columnName]<=upper]
        df = df.loc[df[columnName]>=lower]
        outlierN = org_df - len(df) # 이상치 갯수 구하기
        meta.set("isTest", False)

    # 전처리 컬럼 및 메타 수정
    meta.setMany({"q25": float(q25), "q50": float(q50), "q75": float(q75),
                 "lower": float(lower), "upper": float(upper),
                 "outlierN": int(outlierN)})
    df = df.reset_index(drop=True)
    return [meta.__dict__, df]

# 이상치 처리 - ESD 
# 인자 : dataframe(df), columnName(str), newColumn(bool)
def ESD(df, columnName, newColumn):
    """
    ESD(Extreme Studentized deviate test)
    ESD 이상치 처리 공식 : 평균 - 표준편차*3 < 정상 < 평균 + 표준편차*3
    """
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "ESD", "columnName": columnName})

    # 전처리 값 계산
    avg = df[columnName].mean()
    stddev = df[columnName].std(ddof=0) # 1/ (N - ddof)
    ESDMultiplier = 3

    # lower와 upper bound 값 구하기
    cut_off = stddev * ESDMultiplier
    lower, upper = avg - cut_off, avg + cut_off
    
    # 이상치 판단
    if newColumn == True:
        def is_outlier_func(x):
            return not (lower <= x and x <= upper)
        newColVal = df[columnName].map(is_outlier_func)
        outlierN = int(newColVal.sum())
        meta.set("isTest", True)
        replaceOrAddColumn(df, newColVal, newColumn, meta)
        
    # 이상치 제거
    else:
        org_df = len(df)
        df = df.loc[df[columnName]<=upper]
        df = df.loc[df[columnName]>=lower]
        outlierN = org_df - len(df) # 이상치 갯수 구하기
        meta.set("isTest", False)

    # 전처리 컬럼 및 메타 수정
    meta.setMany({"orgMean" : float(avg), "stddev": float(stddev), "cutoff": float(cut_off),
                  "lower": float(lower), "upper": float(upper), 
                  "outlierN": int(outlierN)})
    df = df.reset_index(drop=True)
    return [meta.__dict__, df]

# main
if __name__ == "__main__":
    # test data
    lines = """
        Name,Count,Price
        Apples,21,200
        Mango,5,NaN
        Banana,30,300
        Pear,10,40
        Mango,NaN,250
        Tomato,50,450
        Tomato,50,1300000
    """
    data = [line.strip().split(',') for line in lines.split("\n")]
    data = [d for d in data if len(d) == 3]
    df = pd.DataFrame(data=data[1:], columns=data[0])

    # df.replace("NaN", np.nan, inplace=True)
    df.replace("NaN", 0, inplace=True)
    df["Count"] = df["Count"].astype('int')
    df["Price"] = df["Price"].astype('int')

    df = pd.read_csv('../dataset/Telecom_Customer_Churn.csv')
    # 이상치 판단 Carling, tukey, ESD
    result = Carling(df, "tenure", newColumn = True)
    print('meta정보1 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    # 이상치 제거
    result = Carling(df, "tenure", newColumn = False)
    print('meta정보2 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    # 이상치 판단 Carling, Tukey, ESD
    result = Tukey(df, "tenure", newColumn = True)
    print('meta정보3 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    # 이상치 제거
    result = Tukey(df, "tenure", newColumn = False)
    print('meta정보4 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    # 이상치 판단 Carling, tukey, ESD
    result = ESD(df, "tenure", newColumn = True)
    print('meta정보5 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    # 이상치 제거
    result = ESD(df, "tenure", newColumn = False)
    print('meta정보6 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])
