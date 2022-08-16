import sys
from numpy.core.defchararray import isdigit
import pandas as pd
import numpy as np
from preproc_utils import MyJsonObject, replaceOrAddColumn
from exception import replaceStringRangeException

"""
@param df pandas DataFrame object
@param columnName 전처리 대상이 되는 칼럼이름의 목록
@param newColumn 전처리 결과를 새 칼럼으로 만들지 또는 기존 칼럼의 값을 수정할지 결정하는 boolean
"""

# 값 변경 : 특정 값을 특정 값으로 변환
# 인자 : dataframe(df), columnName(str), newColumn(bool, False), mapping(dict)
# key : 문자열로 들어온 mapping을 정수, 실수, 논리형등으로 분리 필요
def ReplaceValue(df, columnName, newColumn, mapping):
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "ReplaceValue", "columnName": columnName, "isTest":True})

    # 컬럼 key값 dtype 파악
    col_dtype = str(df[columnName].dtypes)
    mapping = dict(mapping) # 값 대체 값들 -> {'1':'True', '0':'False'} 다 문자열로 넘어옴.

    # 대체할 value값 dtype 파악
    func_map = {
        'int64':lambda x:int(x),
        'float64':lambda x:float(x),
        'bool':lambda x:bool(x),
        'object': lambda x:str(x)
    }
    val = str(list(mapping.values())[0])
    if val.isdigit(): # 정수일 때
        val_dtype = 'int64'
    else: # 실수나 boolean 형
        if val=='True' or val=='False':
            val_dtype = 'bool'
        else:
            val_dtype = 'float64'

    # key, value dtypes 들 파악 완료 후 변환
    mapping = {func_map[col_dtype](k) : func_map[val_dtype](v) for k, v in mapping.items()}
    newColVal = df[columnName].replace(mapping)
    
    sum_map = 0
    for k, _ in mapping.items():
        sum_map += (df[columnName]==k).sum()
    meta.set("replaceSum", int(sum_map))

    missing_num = df[columnName].isna().sum()
    meta.set("missingNum", int(missing_num))
    
    # 전처리 컬럼 및 메타 수정
    meta.set("orgValues", list(mapping.keys()))
    meta.set("replaceValues", list(mapping.values()))
    
    replaceOrAddColumn(df, newColVal, newColumn, meta)
    return [meta.__dict__, df]

# 값 변경 : 특정 값을 특정 값으로 변환
# 인자 : dataframe(df), columnName(str), newColumn(bool, True), range_list(double list)
def ReplaceRangeValue(df, columnName, newColumn, range_list):
    # range_list = [[0,20,'F'],[21,40,'D'], [41,60,'C'], [61,80,'B'], [81,100,'A']]
    # 전처리 메타 생성
    meta = MyJsonObject({"name": "ReplaceRangeValue", "columnName": columnName, "isTest":True})
    col_dtype = df[columnName].dtypes

    # 전처리 값 계산
    cond_list, value_list = [], []
    if col_dtype == 'object':
        raise replaceStringRangeException()
        # for min_v, max_v, new_v in range_list:
        #     filter_df = (df[columnName] >= min_v) & (df[columnName]<max_v)

        #     cond_list.append(filter_df) # 조건 list
        #     value_list.append(new_v) # 변경 값 리스트

    elif col_dtype =='int64' or col_dtype =='float64' or col_dtype =='bool':
        for min_v, max_v, new_v in range_list:
            filter_df = (df[columnName] >= float(min_v)) & (df[columnName]< float(max_v))
            cond_list.append(filter_df) # 조건 list
            value_list.append(new_v) # 변경 값 리스트
        
            for i, val in enumerate(range_list):
                min_v, max_v, new_v = val
                if col_dtype == 'int64':
                    range_list[i] = [int(min_v), int(max_v), new_v]
                elif col_dtype == 'float64':
                    range_list[i] = [float(min_v), float(max_v), new_v]
                elif col_dtype == 'bool':
                    range_list[i] = [bool(min_v), bool(max_v), new_v]
        

    # 신규컬럼에 반영. 
    newColVal = np.select(cond_list, value_list, default=None) # pd.NA

    # 전처리 컬럼 및 메타 수정
    meta.set("rangeList", range_list)
    replaceOrAddColumn(df, newColVal, newColumn, meta)
    missing_num = df[columnName + "_" + meta.name].isna().sum()

    range_list_sum = len(df) - missing_num 
    meta.setMany({"missingNum":int(missing_num), "replaceSum": int(range_list_sum)})

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
    result = ReplaceValue(df, "gender", False, {'Female':'Female__', 'Male':'Male__'})  
      
    print('meta정보 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    # [['0','20','F'],['21','40','D'], ['41','60','C'], ['61','80','B'], ['81','100','A']]
    result = ReplaceRangeValue(df, "tenure", True, [[0, 20,'F'],[21, 40,'D'], [41, 60,'C'], [61, 80,'B'], [81, 100,'A']])  
    print('meta정보 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    result = ReplaceValue(result[1], "tenure_ReplaceRangeValue", True, {'nan':'A'})  
      
    print('meta정보 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])