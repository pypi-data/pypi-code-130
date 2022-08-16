import pandas as pd
import numpy as np
import json
from preproc_utils import MyJsonObject, replaceOrAddColumn
from exception import filteringNumberException, filteringStringRangeException


"""
==========================================
| 컬럼   | 비교대상 | 가능 식 ==
| 논리형 |  논리형  | >, <, >=, <=, ==, !=
# | 논리형 |  수치형  | >, <, >=, <=, ==, !=
# | 논리형 |  문자형  | ==, !=
==========================================
| 수치형 |  수치형  | >, <, >=, <=, ==, !=
# | 수치형 |  논리형  | >, <, >=, <=, ==, !=
# | 수치형 |  문자형  | ==, !=
==========================================
| 문자형 |  문자형  | >, <, >=, <=, ==, !=
# | 문자형 |  수치형  | ==, !=
# | 문자형 |  논리형  | ==, !=
==========================================

요구사항 정리
- 컬럼과 비교대상이 같을 때는 모두 사용 가능
- [수치형, 논리형]은 사실 동일, 문자형과 비교시는 ==, != 만 사용 가능
- 해당 컬럼 조건을 만족하는 행만 남기는 것 (행단위 연산으로 => 기존 컬럼에 반영)

EX) Condition
"X > 2"
"X >= 1 AND X < 5"
"X < 1 OR X >= 5"
"""

def parseOneExpr(df, columnName, col_dtype, flds):
    print("OneExpr", flds) # ['X', '>', '0']
    ## front-end에서 넘겨주는 flds는 모두 문자열 타입임
    if col_dtype == 'object':
        print('column이 object 입니다')
        if flds[1] not in ['==', '!=']:
            print('예외발생 - 연산자 ==, != 만 가능')
            raise filteringStringRangeException()
        val1 = str(flds[2])
    elif col_dtype == 'bool':
        print('column이 Bool 입니다')
        val1 = bool(flds[2])
    elif col_dtype == 'int64' or col_dtype=='float64':
        print('column이 numerical 입니다')
        try:
            val1 = float(flds[2]) # X > 0
        except:
            print('예외발생 - 숫자 float() 함수에서')
            raise filteringNumberException()        

    # OP : 연산자
    op = flds[1]
    if (op == ">"): 
        return df[columnName] > val1
    elif (op == ">="):  
        return df[columnName] >= val1
    elif (op == "=="): 
        return df[columnName] == val1
    elif (op == "!="):
        return df[columnName] != val1
    elif (op == "<"):
        return df[columnName] < val1
    elif (op == "<="):
        return df[columnName] <= val1
    else:
        return df

"""
문자열로 되어있는 수식을 파싱하여 DataFrame 리턴
"""
def parseExpression(df, columnName, col_dtype, exprStr):
    flds = exprStr.strip().split(' ')
    # 대소 비교 연산자만 사용
    if len(flds) == 3: # 4n-1
        func = parseOneExpr(df, columnName, col_dtype, flds)
        return df[func]

    # 대소 비교 연산자 + [AND, OR] 결합
    elif len(flds) == 7:
        boolOp = flds[3].upper()
        func1 = parseOneExpr(df, columnName, col_dtype, flds[:3])
        func2 = parseOneExpr(df, columnName, col_dtype, flds[4:])
        if (boolOp == "AND"):
            return df[func1 & func2]

        elif (boolOp == "OR"):
            return df[func1 | func2]
    else:
        print("ERROR in", exprStr, '맞지않는 필터 수식입니다')
        return df

def Filtering(df, columnName, newColumn, condition):
    col_dtype = df[columnName].dtypes
    meta = MyJsonObject({"name": "Filtering", "columnName": columnName, "isTest":True, "colDtype": str(col_dtype), "condition": condition})

    ## @TODO exception 발생시에 어떻게 처리할 것인가. 2022/07/20
    ## front-end에서는 예외 상황에 대한 UI 처리가 아직 안되고 있음. 
    ## 여기서 그냥 원본 df 그대로 return 하도록 해야 할까?
    df = parseExpression(df, columnName, col_dtype, condition)
    print(df.reset_index(drop=True))

    return [meta.__dict__, df]

# main
if __name__ == "__main__":
    # test data
    lines = """
        Name,Count,Price,is_n
        Apples,21,500,True
        Mango,5,NaN, True
        Banana,30,500, True
        Pear,10,40, True
        Mango,NaN,250, True
        Tomato,50,450, True
    """
    data = [line.strip().split(',') for line in lines.split("\n")]
    data = [d for d in data if len(d) == 4]
    df = pd.DataFrame(data=data[1:], columns=data[0])

    # df.replace("NaN", np.nan, inplace=True)
    df.replace("NaN", 0, inplace=True)
    df["Count"] = df["Count"].astype('int')
    df["Price"] = df["Price"].astype('int')
    df["is_n"] = df["is_n"].astype('bool')
    df['Price'][3:4]  = np.nan

    df = pd.read_csv('../dataset/Telecom_Customer_Churn.csv')
    condition = 'X == Female' # "X >= 60 AND X <= 150" # "X >= 5" 
    # result = Filtering(df, "Price", True, condition)
    result = Filtering(df, "gender", True, condition)

    print('meta정보3 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])
