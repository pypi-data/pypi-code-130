import pandas as pd

# return 데이터기본통계_df
def get_describe(df):
    df_dict = dict(pd.Series(df.dtypes, dtype="string"))
    numeric_col, bool_col, object_col = [], [], []
    for col, ty in df_dict.items():
        if ty == 'int64' or ty =='float64':
            numeric_col.append(col)
        elif ty == 'bool':
            bool_col.append(col)
        elif ty == 'object':
            object_col.append(col)

    print(object_col)
    
    # 결측치, 왜도, 첨도
    null_df = pd.DataFrame(df[numeric_col].isna().sum()).T
    skew_df = pd.DataFrame(df[numeric_col].skew()).T
    kurt_df = pd.DataFrame(df[numeric_col].kurt()).T

    # 기술통계표 처리
    df_describe = df.describe().append([null_df, skew_df, kurt_df])
    df_describe.index = ['개수','평균','표준편차','최솟값','1분위 (25%)', '중앙값', '3분위 (75%)', '최댓값', '결측치 개수', '왜도', '첨도']
    return df_describe

# return list (dict) 
# 각 object column에 대한 빈도표 + 결측치 처리 구현
def get_object_describe(df):
    df_dict = dict(pd.Series(df.dtypes, dtype="string"))
    numeric_col, bool_col, object_col = [], [], []
    for col, ty in df_dict.items():
        if ty == 'int64' or ty =='float64':
            numeric_col.append(col)
        elif ty == 'bool':
            bool_col.append(col)
        elif ty == 'object':
            object_col.append(col)
            
    # 빈도표 처리
    result_list = []
    for o_col in object_col:
        # 빈도표 + 결측치 처리
        count_ob_df = pd.DataFrame(df[o_col].value_counts())
        null_ob_df = pd.DataFrame(pd.Series(df[o_col].isna().sum(), name=o_col, index=['결측치 갯수']))
        result_df = count_ob_df.append(null_ob_df)
        result_list.append(result_df.to_dict())
    return result_list

# return 상관계수표 df
def get_corr(df):
    return df.corr()

if __name__ == "__main__":
    df = pd.read_csv('../dataset/boston_housing.csv')
    result = get_describe(df)
    print(result)
    # result = get_object_describe(df)
    # print(result, type(result))
    # print(result[2])
    # result = get_corr(df)
    # result = result.to_dict()
    # print(result, type(result))    