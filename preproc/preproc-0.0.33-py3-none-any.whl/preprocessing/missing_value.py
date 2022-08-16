import pandas as pd
import numpy as np
from preproc_utils import MyJsonObject, replaceOrAddColumn
from exception import missingValueStringMeanException, missingValueStringMedianException, missingValueStringModeException, missingValueStringMinimumException, missingValueStringMaximumException

'''
https://github.com/Neuralworks-io/FE-neural-studio/blob/d2eed956ec711a365753bed697f251f8bb049d74/src/util/danfoUtil.js#L146-L177

결측치 처리 3가지
- 기본적으로 FillMissing(columnName, newColumn, nanVals, fillVal, descriptive) 함수 호출

1. 결측치 행 제거
- FillMissing(columnName, newColumn=False, nanVals=None, fillVal=None, descriptive=-1)

2. 결측치 값 지정 (수치함수, ['mean', 'median', 'mode', 'min', 'max'])
- FillMissing(columnName, newColumn=False, nanVals=None, fillVal=None, descriptive=0~4)

3. 결측치 값 지정 (특정값)
- FillMissing(columnName, newColumn=False, nanVals=None, fillVal=값, descriptive=-1)

'''


def FillMissing(df, columnName, newColumn, nanVals, fillVal, descriptive):
    # key - fillVal: NaN를 대체하는 값
    meta = MyJsonObject(
        {"name": "FillMissing", "columnName": columnName, "fillVal": fillVal, "nanVals": nanVals, "descriptive": descriptive})
    fillval_list = ['mean', 'median', 'mode', 'min', 'max']

    # 결측치 제거
    try:
        if (fillVal == None) and (descriptive == -1):
            print('=== 결측치 제거')
            pre_len = len(df)
            df = df[df[columnName].notna()]
            pro_len = len(df)
            meta.setMany({'isTest': False, 'treatedMissingN': int(
                pre_len - pro_len), "remainedMissingN": int(df[columnName].isna().sum())})
            df = df.reset_index(drop=True)
            return [meta.__dict__, df]

        # 결측치 값 채우기
        else:
            fillval_list_value = [df[columnName].mean(), df[columnName].median(
            ), df[columnName].mode().values[0], df[columnName].min(), df[columnName].max()]
            treatedMissingN = df[columnName].isna().sum()
            meta.set('treatedMissingN', treatedMissingN)
            # 결측치 값 채우기- 특정 값으로 채우기
            # history 기반 해석에서는
            if (fillVal != None) and (descriptive == -1):
                print('=== 결측치 값 채우기 - 특정값')
                newColVal = df[columnName].fillna(value=meta.fillVal)

            # 결측치 값 채우기- 함수를 이용한 값 채우기
            elif (fillVal == None) and (descriptive != -1):
                print('=== 결측치 값 채우기 - 함수 이용 값')
                newColVal = df[columnName].fillna(
                    value=fillval_list_value[meta.descriptive])
                meta.setMany({
                    "fillVal": fillval_list_value[meta.descriptive],
                    "method": fillval_list[meta.descriptive]
                })

            # 전처리 컬럼 및 메타 수정
            replaceOrAddColumn(df, newColVal, newColumn, meta)
            remainedMissingN = df[columnName].isna().sum()
            meta.setMany(
                {'isTest': True, 'remainedMissingN': int(remainedMissingN)})
            return [meta.__dict__, df]
    except TypeError:
        if descriptive == 0:
            raise missingValueStringMeanException()
        elif descriptive == 1:
            raise missingValueStringMedianException()
        elif descriptive == 2:
            raise missingValueStringModeException()
        elif descriptive == 3:
            raise missingValueStringMinimumException()
        elif descriptive == 4:
            raise missingValueStringMaximumException()


# main
if __name__ == "__main__":

    # # test data
    lines = """
        Name,Count,Price
        Apples,21,500
        Mango,5,NaN
        Banana,30,500
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
    df['Price'][3:4] = np.nan

    # 결측치 제거
    result = FillMissing(df=df, columnName='Price', newColumn=False,
                         nanVals=None, fillVal=None, descriptive=-1)
    print('meta정보1 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    # 결측치 값 채우기- 특정 값으로 채우기
    result = FillMissing(df=df, columnName='Price', newColumn=False,
                         nanVals=None, fillVal=10, descriptive=-1)
    print('meta정보2 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])

    # 결측치 값 채우기- 함수를 이용한 값 채우기
    result = FillMissing(df=df, columnName='Price', newColumn=False,
                         nanVals=None, fillVal=None, descriptive=2)
    print('meta정보3 : ', result[0])
    print('========')
    print('dataframe :\n', result[1])
