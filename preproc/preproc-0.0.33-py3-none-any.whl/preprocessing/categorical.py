import pandas as pd
import numpy as np
from preproc_utils import MyJsonObject, replaceOrAddColumn
from exception import CategoricalNoneException

def LabelEncoder(df, columnName, newColumn):
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "LabelEncoder", "columnName": columnName, "isTest":True})

    # 전처리 값 계산
    labels = list(df[columnName].unique())
    if 'nan' in labels:
        raise CategoricalNoneException()
    labels.sort()

    num_labels = [i for i in range(len(labels))]
    mapping = {labels[i]: i for i in range(len(labels))}
    
    # 전처리 컬럼 및 메타 수정
    meta.set("numLabel", num_labels)
    meta.set("label", labels)
    newColVal = df[columnName].map(mapping)
    replaceOrAddColumn(df, newColVal, newColumn, meta)
    return [meta.__dict__, df]

def OneHotEncoder(df, columnName, newColumn):
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "OneHotEncoder", "columnName": columnName, "isTest":True})

    # one-hot 인코딩 계산
    labels = list(df[columnName].unique())
    if 'nan' in labels:
        raise CategoricalNoneException()
    labels.sort()

    newColNameList = []
    for i, label in enumerate(labels): 
        newColVal = df[columnName].map(lambda x: 1 if x == label else 0) # 
        newColName = columnName + "_" + str(label) # ex) Name_Pear
        df[newColName] = newColVal
        newColNameList.append(newColName)

    # 전처리 컬럼 및 메타 수정
    meta.set("label", labels)
    meta.set("newColumn", newColNameList)
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
    """
    data = [line.strip().split(',') for line in lines.split("\n")]
    data = [d for d in data if len(d) == 3]
    df = pd.DataFrame(data=data[1:], columns=data[0])

    # df.replace("NaN", np.nan, inplace=True)
    df.replace("NaN", 0, inplace=True)
    df["Count"] = df["Count"].astype('int')
    df["Price"] = df["Price"].astype('int')

    # =================================
    df = pd.read_csv('../dataset/Telecom_Customer_Churn.csv')
    result = LabelEncoder(df, "Contract", newColumn=True)
    print('meta정보 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    result = OneHotEncoder(df, "Contract", newColumn=True)
    print('meta정보 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])