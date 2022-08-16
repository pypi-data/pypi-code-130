import sys
import pandas as pd
import numpy as np
from scipy import stats
from preproc_utils import MyJsonObject, replaceOrAddColumn

"""
@param df pandas DataFrame object
@param columnName 전처리 대상이 되는 칼럼이름의 목록
@param newColumn 전처리 결과를 새 칼럼으로 만들지 또는 기존 칼럼의 값을 수정할지 결정하는 boolean
"""

# Standard 표준화
# 인자 : dataframe(df), columnName(str), newColumn(bool)
def StandardScaler(df, columnName, newColumn):
    """
    Standard 표준화 공식 : X-X.mean() / X.std()
    scikit-learn의  StandardScaler (stddev를 1/N로 구함)
    pandas의 std() 함수는 stddev를 구할 때 1/(N-1)으로 구함
    """
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "StandardScaler", "columnName": columnName, "isTest":True})

    # 전처리 값 계산
    org_min, org_max, org_avg = df[columnName].min(), df[columnName].max(), df[columnName].mean()
    org_stddev = df[columnName].std(ddof=0) # 1/ (N - ddof)
    newColVal = df[columnName].map(lambda x: (x - org_avg)/org_stddev)
    
    # 전처리 컬럼 및 메타 수정
    replaceOrAddColumn(df, newColVal, newColumn, meta)
    new_min, new_max, new_avg, new_stddev = df[columnName].min(), df[columnName].max(), df[columnName].mean(), df[columnName].std(ddof=0)
    org_min, org_max, org_avg, org_stddev, new_min, new_max, new_avg, new_stddev = float(org_min), float(org_max), float(org_avg), float(org_stddev), float(new_min), float(new_max), float(new_avg), float(new_stddev)
    meta.setMany({
        "orgMin": org_min, "orgMax": org_max, # 
        "orgMean": org_avg, "orgStdDev": org_stddev,
        "newMin": new_min, "newMax": new_max,
        "newMean": new_avg, "newStdDev": new_stddev
    })
    return [meta.__dict__, df]

# MinMax 정규화
# 인자 : dataframe(df), columnName(str), newColumn(bool)
def MinMaxScaler(df, columnName, newColumn):
    """
    MinMax 정규화 공식 : X-X.min() / (X.max() - X.min())
    """
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "MinMaxScaler", "columnName": columnName, "isTest":True})

    # 전처리 값 계산
    org_min , org_max, org_avg = df[columnName].min(), df[columnName].max(), df[columnName].mean()
    org_stddev = df[columnName].std(ddof=0) 
    range = org_max - org_min
    if range != 0:
        newColVal = df[columnName].map(lambda x: (x - org_min)/range)
    else:
        newColVal = df[columnName].map(lambda x: 0)

    # 전처리 컬럼 및 메타 수정
    replaceOrAddColumn(df, newColVal, newColumn, meta)
    new_min, new_max, new_avg = df[columnName].min(), df[columnName].max(), df[columnName].mean()
    new_stddev = df[columnName].std(ddof=0) 
    org_min, org_max, org_avg, org_stddev, new_min, new_max, new_avg, new_stddev = float(org_min), float(org_max), float(org_avg), float(org_stddev), float(new_min), float(new_max), float(new_avg), float(new_stddev)
    meta.setMany({
        "orgMin": org_min, "orgMax": org_max,
        "orgMean": org_avg, "orgStdDev": org_stddev,
        "newMin": new_min, "newMax": new_max,
        "newMean": new_avg, "newStdDev": new_stddev
    })
    return [meta.__dict__, df]

# Robust 표준화
# 인자 : dataframe(df), columnName(str), newColumn(bool)
def RobustScaler(df, columnName, newColumn):
    """
    Robust 표준화 공식 : X-X_2분위수 / (X_3분위수 - X_1분위수)
    """
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "RobustScaler", "columnName": columnName, "isTest":True})
    org_min, org_max = df[columnName].min(), df[columnName].max()

    # 전처리 값 계산
    q25, q50, q75 = df[columnName].quantile([.25, .5, .75])
    range = q75 - q25
    if range != 0:
        newColVal = df[columnName].map(lambda x: (x - q50)/range)
    else:
        newColVal = df[columnName].map(lambda x: 0)

    # 전처리 컬럼 및 메타 수정
    replaceOrAddColumn(df, newColVal, newColumn, meta)
    # meta.setMany({"q25": q25, "q50": q50, "q75":q75})
    new_min, new_max = df[columnName].min(), df[columnName].max()
    new_q25, new_q50, new_q75 = df[columnName].quantile([.25, .5, .75])

    org_min, org_max, q25, q50, q75, new_min, new_max, new_q25, new_q50, new_q75 = float(org_min), float(org_max), float(q25), float(q50), float(q75), float(new_min), float(new_max), float(new_q25), float(new_q50), float(new_q75)
    meta.setMany({
        "orgMin": org_min, "orgMax": org_max,
        "orgQ25": q25, "orgQ50": q50, "orgQ75": q75,
        "newMin": new_min, "newMax": new_max,
        "newQ25": new_q25, "newQ50": new_q50, "newQ75": new_q75,
    })
    return [meta.__dict__, df]

# Log 스케일러
# 인자 : dataframe(df), columnName(str), newColumn(bool)
def LogScaler(df, columnName, newColumn):
    """
    Log 스케일러 공식 : log1p(x)
    https://steadiness-193.tistory.com/224
    """
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "LogScaler", "columnName": columnName, "isTest":True})

    # 전처리 값 계산
    org_min, org_max = df[columnName].min(), df[columnName].max()
    newColVal = df[columnName].map(lambda x: np.log1p(x))

    # 전처리 컬럼 및 메타 수정
    replaceOrAddColumn(df, newColVal, newColumn, meta)
    new_min, new_max = df[columnName].min(), df[columnName].max()

    org_min, org_max, new_min, new_max = float(org_min), float(org_max), float(new_min), float(new_max)
    meta.setMany({
        "orgMin": org_min, "orgMax": org_max,
        "newMin": new_min, "newMax": new_max,
    })
    return [meta.__dict__, df]

# exp 스케일러
# 인자 : dataframe(df), columnName(str), newColumn(bool)
def ExpScaler(df, columnName, newColumn):
    """
    exp 스케일러 공식 : exp(x)-1
    https://steadiness-193.tistory.com/224
    """
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "ExpScaler", "columnName": columnName, "isTest":True})

    # 전처리 값 계산
    org_min, org_max = df[columnName].min(), df[columnName].max()
    newColVal = df[columnName].map(lambda x: np.exp(x)-1)
    
    # 전처리 컬럼 및 메타 수정
    replaceOrAddColumn(df, newColVal, newColumn, meta)
    new_min, new_max = df[columnName].min(), df[columnName].max()
    org_min, org_max, new_min, new_max = float(org_min), float(org_max), float(new_min), float(new_max)
    meta.setMany({
        "orgMin": org_min, "orgMax": org_max,
        "newMin": new_min, "newMax": new_max,
    })
    return [meta.__dict__, df]

# BoxCoxTransform
# 인자 : dataframe(df), columnName(str), newColumn(bool)
def BoxCoxTransform(df, columnName, newColumn):
    """
    BoxCoxTransform : 정규 분포 처럼 바꿔주는 알고리즘
    https://dining-developer.tistory.com/18
    """
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "BoxCoxTransform", "columnName": columnName, "isTest":True})
    org_min, org_max = df[columnName].min(), df[columnName].max()

    # 전처리 값 계산
    try:
        newColVal = stats.boxcox(df[columnName]+sys.float_info.epsilon)[0] # boxcox는 양수에만 적용 가능해서.
    except ValueError as e:
        newColVal = df[columnName]
        print("Error: BoxCox는 양수에 대해서만 적용 가능합니다.", e)
        
    # 전처리 컬럼 및 메타 수정
    replaceOrAddColumn(df, newColVal, newColumn, meta)
    new_min, new_max = df[columnName].min(), df[columnName].max()
    org_min, org_max, new_min, new_max = float(org_min), float(org_max), float(new_min), float(new_max)
    meta.setMany({
        "orgMin": org_min, "orgMax": org_max,
        "newMin": new_min, "newMax": new_max,
    })
    return [meta.__dict__, df]

# main
if __name__ == "__main__":
    lines = """
        Name,Count,Price
        Apples,21,3
        Mango,5,NaN
        Banana,30,300
        Pear,10,40
        Mango,NaN,250
        Tomato,50,450
    """
    
    data = [line.strip().split(',') for line in lines.split("\n")]
    data = [d for d in data if len(d) == 3]
    df = pd.DataFrame(data=data[1:], columns=data[0])

    # df.replace("NaN", np.nan, inplace=True)
    df.replace("NaN", 0, inplace=True)
    df["Count"] = df["Count"].astype('int')
    df["Price"] = df["Price"].astype('int')
    # df['Price'][5:]  = np.nan

    # =================================
    df = pd.read_csv('../dataset/Telecom_Customer_Churn.csv')
    # result = StandardScaler(df, "tenure", False)
    # result = MinMaxScaler(df, "TotalCharges", False)
    # result = RobustScaler(df, "Partner", False)
    # result = LogScaler(df, "Partner", False)
    # result = ExpScaler(df, "Dependents", False)
    result = BoxCoxTransform(df, "OnlineBackup", False)
    print('meta정보 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])