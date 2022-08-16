# =================================================
# 기능 1. 첫 데이터 로드
# - args : (url과 table_meta 정보 dict로)
#
# =================================================
# 기능 2. 전처리 진행 - 미리보기 ?
# - 미리보기 후 완료 : 미리보기, 완료 두번 전처리 됨
# - 같은 함수를 바라봄 / meta 를 Front에서 넣느냔 안넣느냐 차이
#
# 기능 3. 전처리 진행 - 완료
# - 진행한 전처리에 대한 결과 dataframe과 meta정보 넘김
# - args : (기존 Danfo 코드 처럼 - 전처리 마다 조금씩 상이)
#
# =================================================
# 기능 4. 전처리 내역 리스트 클릭 (view)
# - 누르는 순간 히스토리 읽어서 해당 전처리 까지 진행
# - history 넘겨주면 하나 이전 history(past_history), 현재 history (now_history)
# - 최종 주는 건 return 해당 전처리까지 된 df
# - args : (History)
#
# =================================================
# 기능 5. 전처리 내역 수정 (Edit, Delete)
# - args : (type) - edit, delete인지 여부만
#
# =================================================
# 기능 6. 기타 - 요약 탭
# def correlation
# def described
# def object_val_counts
#
# =================================================

# Front => Pyodide 함수 인자 Case
# 경우 1. Listview 클릭시 => 함수인자(is_listview = True, is_preview = False) => return dataframe
# 경우 2. 미리보기 클릭시 => 함수인자(is_listview = False, is_preview = True) => return [meta, dataframe]
# 경우 3. 확인 클릭시 => 함수인자(is_listview = False, is_preview = False) =>  return [meta, latest_df]

# from js import getObj
# import pyodide
import pandas as pd
from data_info.info import get_describe, get_corr, get_object_describe
from preproc_utils import MyJsonObject, replaceOrAddColumn
from groupby import GroupBy
from filtering import Filtering
from replace_value import ReplaceValue, ReplaceRangeValue
from missing_value import FillMissing
from categorical import LabelEncoder, OneHotEncoder
from outlier import Carling, Tukey, ESD
from scaler import StandardScaler, MinMaxScaler, RobustScaler, LogScaler, ExpScaler, BoxCoxTransform
from exception import *
import os
import sys
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
mypath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
mypath2 = os.path.join(mypath, 'preprocessing')
print(f"mypath: {mypath}")
print(f"mypath2: {mypath2}")
# sys.path.append(mypath)
sys.path.append(mypath2)


def df2js(df):
    dev = True
    if dev:
        return df
    else:
        return pyodide.to_js([df.columns.values.tolist(), df.values.tolist()])

# def csv2df(csv):
#  pass
# ==================================

# 전처리 Class


class PreProc:
    # 생성자 - 데이터 형 지정 로드
    def __init__(self, url, url2, table_meta):
        # tb_dtypes = {col : dtype for col, dtype in zip(table_meta.columns, table_meta.dtypes)}
        # self.origin_df = self.latest_df = self.temp_df = pd.read_csv(url, dtype=tb_dtypes)
        try:
            self.url = url
            self.origin_df = pd.read_csv(url, dtype=table_meta)  # 기본 데이터
            self.latest_df = self.origin_df.copy()  # 전처리 맨 마지막 단계까지 완료된 최종 데이터
            self.temp_df = self.origin_df.copy()  # list view 한단계 전 데이터
            self.view_df = self.origin_df.copy()  # 최종 list view 용 데이터
            if url2:
                url2.close()
            print('정상적으로 Load 되었습니다. Load 한 데이터 크기는 : ', self.origin_df.shape)
        except:
            print(
                '==Custom Warning : Colume별 type 지정(table_meta)의 충돌로 pandas 기준으로 자동 로드 됩니다')
            df = pd.read_csv(url2)
            for col, v in table_meta.items():
                if v == 'int64':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif v == 'float64':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif v == 'object':
                    try:
                        df[col] = df[col].astype('str')
                    except:
                        print('문자열로 변환 될 수 없는 열입니다')
                        pass
                elif v == 'bool':
                    try:
                        df[col] = df[col].astype('bool')
                    except:
                        print('논리형으로 변환 될 수 없는 열입니다')
                        pass
            # 최종 DataFrame
            self.origin_df = df.copy()
            self.latest_df = df.copy()
            self.temp_df = df.copy()

        self.MAP_HISTORY_PARSING_FUNC = {
            "FillMissing": self.FillMissing,

            "StandardScaler": self.StandardScaler,
            "MinMaxScaler": self.MinMaxScaler,
            "RobustScaler": self.RobustScaler,
            "LogScaler": self.LogScaler,
            "ExpScaler": self.ExpScaler,
            "BoxCoxTransform": self.BoxCoxTransform,

            "Carling": self.Carling,
            "Tukey": self.Tukey,
            "ESD": self.ESD,

            "LabelEncoder": self.LabelEncoder,
            "OneHotEncoder": self.OneHotEncoder,
            "ReplaceValue": self.ReplaceValue,  # 값 대체 : 단일값
            "ReplaceRangeValue": self.ReplaceRangeValue,  # 값 대체 : 범위값

            "Filtering": self.Filtering,
            "GroupBy": self.GroupBy,  # 2022/05/10, LG education
        }
    # ==================================
    #
    # 전처리 리스트 View 기능

    def parseHistory_view(self, history):
        # framework history parser
        if len(history) == 0:
            print('전처리를 진행하지 않았습니다.')
            return
        elif len(history) == 1:
            past_history, now_history = [], history[-1]
        elif len(history) >= 2:
            # 한단계 전 까지의 전처리 DF 저장
            past_history, now_history = history[:-1], history[-1]
        now_history = [now_history]  # 2차원 list로 만들어주기.

        # case 1) 히스토리 1개일 때, temp_df => None
        # case 2) 히스토리 2개일 때, temp_df => history[:-1]
        self.temp_df = self.process_history(
            self.origin_df.copy(), past_history)  # 한단계 전 까지의 전처리 DF 저장
        self.view_df = self.process_history(
            self.temp_df.copy(), now_history)  # View용 df
        return self.view_df

    def reset2origin(self):
        self.latest_df = self.origin_df.copy()


# 주어진 dataframe에 주어진 history 진행


    def process_history(self, dataframe, history):
        # 1) 기능 A,B,C,D 전처리
        for i, step in enumerate(history):
            # print(f'=== 전처리 history ', len(history), i+1, step)
            # 2) 기능 A 전처리의 a,b 컬럼
            for j, prep in enumerate(step):
                # print(f'=== 전처리 각각 history ', len(step), j+1, prep)
                # 3) 각 전처리 history meta 정보
                p = MyJsonObject(prep)
                func = self.MAP_HISTORY_PARSING_FUNC.get(p.name)
                if func is None:
                    print("UNKNOWN preprocess:", p.name)
                    continue
                # 4) 실제 전처리 parse 및 진행
                dataframe = self.get_preproc_df(func, dataframe, p)
                print('=== 전처리:', p.name, '적용 완료',
                      dataframe.shape, list(dataframe.columns))
        return dataframe

    def get_preproc_df(self, func, dataframe, p):
        # scaler
        if p.name == 'StandardScaler' or p.name == 'MinMaxScaler' or p.name == 'RobustScaler' or \
                p.name == 'LogScaler' or p.name == 'ExpScaler' or p.name == 'BoxCoxTransform':
            dataframe = func(columnName=p.columnName,
                             newColumn=False, is_listview=True, is_preview=False)

        # outlier
        elif p.name == 'Carling' or p.name == 'Tukey' or p.name == 'ESD':
            try:  # newColumn이 있을 떄만
                p_newColumn = p.newColumn
                dataframe = func(
                    columnName=p.columnName, newColumn=True, is_listview=True, is_preview=False)
            except:
                dataframe = func(
                    columnName=p.columnName, newColumn=False, is_listview=True, is_preview=False)

        # Categorical
        elif p.name == 'LabelEncoder' or p.name == 'OneHotEncoder':
            dataframe = func(columnName=p.columnName,
                             newColumn=True, is_listview=True, is_preview=False)

        # FillMissing
        elif p.name == 'FillMissing':
            dataframe = func(columnName=p.columnName, newColumn=True, nanVals=p.nanVals,
                             fillVal=p.fillVal, descriptive=p.descriptive, is_listview=True, is_preview=False)

        # Filtering
        elif p.name == 'Filtering':
            dataframe = func(columnName=p.columnName, newColumn=True,
                             condition=p.condition, is_listview=True, is_preview=False)

        # ReplaceValue
        elif p.name == 'ReplaceValue':
            dataframe = func(columnName=p.columnName, newColumn=True,
                             mapping=p.mapping, is_listview=True, is_preview=False)

        # ReplaceRangeValue
        elif p.name == 'ReplaceRangeValue':
            dataframe = func(columnName=p.columnName, newColumn=True,
                             rangeList=p.rangeList, is_listview=True, is_preview=False)

        # GroupBy
        elif p.name == 'GroupBy':
            dataframe = func(columnName=p.columnName,
                             method=p.method, is_listview=True, is_preview=False)

        return dataframe

    # Edit, Delete 기능
    # type : edit, delete
    def parseHistory_edit_delete(self, type='edit'):
        if type == 'edit':  # 수정 완료 버튼 (수정버튼 아님x)
            self.latest_df = self.temp_df.copy()
            self.temp_df = self.origin_df.copy()

        elif type == 'delete':  # 삭제 완료 버튼
            # history 삭제 => FE에서
            self.latest_df = self.temp_df.copy()  # 한 단계 전 temp_df
            self.temp_df = self.origin_df.copy()

            # history = self.past_history
            # return history

    # ==============================================================
    # Standard Scaler => [meta, self.latest_df]
    def StandardScaler(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능

        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = StandardScaler(
                self.temp_df, columnName, newColumn)  # columnName 한개
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                # 미리 보기 버튼
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = StandardScaler(
                            preview_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min(
                    ).values, preview_df[columnName].min().values, '\n')
                    return [metas, preview_df, None]
                # 확인 버튼
                else:  # is_preview == False
                    metas = []
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = StandardScaler(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min().values)
                    return [metas, self.latest_df, None]
            except TypeError:
                return [None, None, 'preproc.scaler.string']

    # MinMaxScaler => [meta, self.latest_df]
    def MinMaxScaler(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = MinMaxScaler(self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = MinMaxScaler(
                            preview_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min(
                    ).values, preview_df[columnName].min().values, '\n')
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = MinMaxScaler(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min().values)
                    return [metas, self.latest_df, None]
            except TypeError:
                return [None, None, 'preproc.scaler.string']

    # RobustScaler => [meta, self.latest_df]
    def RobustScaler(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = RobustScaler(self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = RobustScaler(
                            preview_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min(
                    ).values, preview_df[columnName].min().values, '\n')
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = RobustScaler(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min().values)
                    return [metas, self.latest_df, None]
            except TypeError:
                return [None, None, 'preproc.scaler.string']

    # LogScaler => [meta, self.latest_df]
    def LogScaler(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = LogScaler(self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = LogScaler(
                            preview_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min(
                    ).values, preview_df[columnName].min().values, '\n')
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = LogScaler(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min().values)
                    return [metas, self.latest_df, None]
            except TypeError:
                return [None, None, 'preproc.scaler.string']

    # ExpScaler => [meta, self.latest_df]
    def ExpScaler(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = ExpScaler(self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = ExpScaler(
                            preview_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min(
                    ).values, preview_df[columnName].min().values, '\n')
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = ExpScaler(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min().values)
                    return [metas, self.latest_df, None]
            except TypeError:
                return [None, None, 'preproc.scaler.string']

    # BoxCoxTransform => [meta, self.latest_df]
    def BoxCoxTransform(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = BoxCoxTransform(
                self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    preview_df = self.latest_df.copy()
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = BoxCoxTransform(
                            preview_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min(
                    ).values, preview_df[columnName].min().values, '\n')
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    print('전처리 전 : ', self.latest_df[columnName].min().values)
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = BoxCoxTransform(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                    print('전처리 후 : ', self.latest_df[columnName].min().values)
                    return [metas, self.latest_df, None]
            except TypeError:
                return [None, None, 'preproc.scaler.string']

    # ==============================================================
    # Carling => [meta, self.latest_df]
    def Carling(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = Carling(self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    preview_df = self.latest_df.copy()
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = Carling(preview_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape, preview_df.shape)
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = Carling(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape)
                    return [metas, self.latest_df, None]
            except TypeError:
                return [None, None, 'preproc.outlier.string']

    # Tukey => [meta, self.latest_df]
    def Tukey(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = Tukey(self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    preview_df = self.latest_df.copy()
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = Tukey(preview_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape, preview_df.shape)
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = Tukey(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape)
                    return [metas, self.latest_df, None]
            except TypeError:
                return [None, None, 'preproc.outlier.string']

    # ESD => [meta, self.latest_df]
    def ESD(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = ESD(self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    preview_df = self.latest_df.copy()
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = ESD(preview_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape, preview_df.shape)
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = ESD(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape)
                    return [metas, self.latest_df, None]
            except TypeError:
                return [None, None, 'preproc.outlier.string']

    # ==============================================================
    # LabelEncoder => [meta, self.latest_df]
    def LabelEncoder(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = LabelEncoder(self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = LabelEncoder(
                            preview_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape, preview_df.shape)
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = LabelEncoder(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape)
                    return [metas, self.latest_df, None]
            except CategoricalNoneException:
                return [None, None, 'preproc.categorical.none']

    # OneHotEncoder => [meta, self.latest_df]
    def OneHotEncoder(self, columnName, newColumn, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = OneHotEncoder(
                self.temp_df, columnName, newColumn)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = OneHotEncoder(
                            preview_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape, preview_df.shape)
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = OneHotEncoder(
                            self.latest_df, col, newColumn)
                        metas.append(meta)
                        print(self.latest_df.shape)
                    return [metas, self.latest_df, None]
            except CategoricalNoneException:
                return [None, None, 'preproc.categorical.none']

    # ==============================================================
    # FillMissing => [meta, self.latest_df]
    def FillMissing(self, columnName, newColumn, nanVals, fillVal, descriptive, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            _, self.temp_df = FillMissing(
                self.temp_df, columnName, newColumn, nanVals, fillVal, descriptive)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = FillMissing(
                            preview_df, col, newColumn, nanVals, fillVal, descriptive)
                        metas.append(meta)
                        print(self.latest_df.shape, preview_df.shape)
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = FillMissing(
                            self.latest_df, col, newColumn, nanVals, fillVal, descriptive)
                        metas.append(meta)
                        print(self.latest_df.shape)
                    return [metas, self.latest_df, None]
            except missingValueStringMeanException:
                return [None, None, 'preproc.missingValue.string.mean']
            except missingValueStringMedianException:
                return [None, None, 'preproc.missingValue.string.median']
            except missingValueStringModeException:
                return [None, None, 'preproc.missingValue.string.mode']
            except missingValueStringMinimumException:
                return [None, None, 'preproc.missingValue.string.minimum']
            except missingValueStringMaximumException:
                return [None, None, 'preproc.missingValue.string.maximum']

    # ==============================================================
    # Filtering => [meta, self.latest_df]
    def Filtering(self, columnName, newColumn, condition, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            meta, self.temp_df = Filtering(
                self.temp_df, columnName, newColumn, condition)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = Filtering(
                            preview_df, col, newColumn, condition)
                        if preview_df.empty:
                            raise filteringNoneException()
                        metas.append(meta)
                        print(self.latest_df.shape, preview_df.shape)
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = Filtering(
                            self.latest_df, col, newColumn, condition)
                        metas.append(meta)
                        print(self.latest_df.shape)
                    if self.latest_df.empty:
                        raise filteringNoneException()
                    return [metas, self.latest_df, None]
            except filteringNoneException:
                return [None, None, 'preproc.fiter.none']
            except filteringNumberException:
                return [None, None, 'preproc.fiter.number']
            except filteringStringRangeException:
                return [None, None, 'preproc.fiter.stringRange']

    # ==============================================================
    # ReplaceValue => [meta, self.latest_df]
    def ReplaceValue(self, columnName, newColumn, mapping, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            meta, self.temp_df = ReplaceValue(
                self.temp_df, columnName, newColumn, mapping)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            if is_preview == True:  # 미리보기 버튼
                metas = []
                preview_df = self.latest_df.copy()
                for col in columnName:
                    print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                    meta, preview_df = ReplaceValue(
                        preview_df, col, newColumn, mapping)
                    metas.append(meta)
                    print(self.latest_df.shape, preview_df.shape)
                return [metas, preview_df, None]
            else:  # is_preview == False
                metas = []
                for col in columnName:
                    print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                    meta, self.latest_df = ReplaceValue(
                        self.latest_df, col, newColumn, mapping)
                    metas.append(meta)
                    print(self.latest_df.shape)
                return [metas, self.latest_df, None]

    # ReplaceRangeValue => [meta, self.latest_df]
    def ReplaceRangeValue(self, columnName, newColumn, rangeList, is_listview, is_preview):
        # Listview 기능
        if is_listview == True:
            print(columnName+'에 대한 연산입니다')
            meta, self.temp_df = ReplaceRangeValue(
                self.temp_df, columnName, newColumn, rangeList)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = ReplaceRangeValue(
                            preview_df, col, newColumn, rangeList)
                        metas.append(meta)
                        print(self.latest_df.shape, preview_df.shape)
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = ReplaceRangeValue(
                            self.latest_df, col, newColumn, rangeList)
                        metas.append(meta)
                        print(self.latest_df.shape)
                    return [metas, self.latest_df, None]
            except replaceStringRangeException:
                return [None, None, 'preproc.replace.stringRange']

    # ==============================================================
    # GroupBy => [meta, self.latest_df] -- 2022/05/10
    def GroupBy(self, columnName, method, is_listview, is_preview):
        """
        columnName: groupby할 컬럼명. string or [string, string]
        method: "MIN", "MAX", "SUM", "AVG", "COUNT"
        """
        # Listview 기능
        if is_listview == True:
            print(f'GroupBy by {columnName}')
            meta, self.temp_df = GroupBy(self.temp_df, columnName, method)
            return self.temp_df

        # 전처리 기능 - return [meta , dataframe]
        else:  # is_listview == False
            try:
                if len(columnName) > 1:
                    raise groupbyInputException()
                if is_preview == True:  # 미리보기 버튼
                    metas = []
                    preview_df = self.latest_df.copy()
                    for col in columnName:
                        print(col+'에 대한 미리보기 연산 입니다', self.latest_df.shape)
                        meta, preview_df = GroupBy(preview_df, col, method)
                        metas.append(meta)
                        print(self.latest_df.shape, preview_df.shape)
                    return [metas, preview_df, None]
                else:  # is_preview == False
                    metas = []
                    for col in columnName:
                        print(col+'에 대한 전처리 확인 버튼 연산입니다', self.latest_df.shape)
                        meta, self.latest_df = GroupBy(self.latest_df, col, method)
                        metas.append(meta)
                        print(self.latest_df.shape)
                    return [metas, self.latest_df, None]
            except groupbyInputException:
                return [None, None, 'preproc.groupby.input']


    # ==============================================================
    # 데이터 요약 페이지
    # return list [기술통계표 df 1개, 빈도표 df 여러개]
    # upgrade version - 향후 기획대로 제대로 된다면.. 아래 두 함수를 쓰면 됩니다.
    # ==========================
    # def getDescribe(self):
    #   return get_describe(self.view_df)

    # return dataframe (correlation)
    # def getCorrelation(self):
    #   return self.view_df.corr()
    # ==========================

    def getDescribe(self, df):
        return get_describe(df)

    def getCorrelation(self, df):
        return get_corr(df)

    def getObjectDescribe(self, df):
        return get_object_describe(df)


if __name__ == "__main__":
    url = '../dataset/Telecom_Customer_Churn.csv'
    # url = '../dataset/nan.csv'
    url = '../dataset/WA_Fn-UseC_-Telco-Customer-Churn.csv'
    # table_meta = \
    #   {
    #   'customerID': object, 'gender': object,
    #   'tenure': int, 'SeniorCitizen': int, 'Partner':int, 'Dependents': int, 'OnlineSecurity': int,'OnlineBackup': int, 'StreamingTV': int, 'StreamingMovies': int,
    #   'Contract': object, 'PaperlessBilling': int, 'PaymentMethod': object, 'MonthlyCharges': float, 'TotalCharges': float, 'Churn': float
    #   }
    table_meta = {
        'customerID': 'object', 'gender': 'object', 'SeniorCitizen': 'int64', 'Partner': 'object',
        'Dependents': 'object', 'tenure': 'int64', 'PhoneService': 'object', 'MultipleLines': 'object',
        'InternetService': 'object', 'OnlineSecurity': 'object', 'OnlineBackup': 'object', 'DeviceProtection': 'object',
        'TechSupport': 'object', 'StreamingTV': 'object', 'StreamingMovies': 'object', 'Contract': 'object',
        'PaperlessBilling': 'object', 'PaymentMethod': 'object', 'MonthlyCharges': 'float64', 'TotalCharges': 'float64',
        'Churn': 'object'
    }
    preproc = PreProc(url=url, url2=url, table_meta=table_meta)

    # 전처리 View Test
    from test import history_example
    # scaler_history_ex = history_example.scaler_history_ex
    # outlier_history_ex = history_example.outlier_history_ex
    # categorical_history_ex = history_example.categorical_history_ex
    # fillmissing_history_ex = history_example.fillmissing_history_ex

    # result = preproc.parseHistory_view(scaler_history_ex)
    # print(result)

    ##########################################################################
    # 전처리 스케일러 기능 테스트 (StandardScaler, MinMaxScaler, RobustScaler, LogScaler, ExpScaler, BoxCoxTransform)
    # func_result = preproc.StandardScaler(columnName = ["customerID"], newColumn = False, is_listview = False, is_preview=True) #

    # 전처리 이상치 기능 테스트 (Carling, Tukey, ESD)
    # 이상치 제거 newColumn = False / 이상치 판단 newColumn = True
    # func_result = preproc.Tukey(columnName = ["MonthlyCharges","tenure"], newColumn = True, is_listview = False, is_preview=True) #

    # 전처리 범주형 기능 테스트 (LabelEncoder, OneHotEncoder)
    # func_result = preproc.LabelEncoder(columnName = ["gender"], newColumn = True, is_listview = False, is_preview=True) #
    # func_result = preproc.OneHotEncoder(columnName=["gender"], newColumn=True, is_listview=False, is_preview=True)

    # 전처리 결측치 기능 테스트 (FillMissing)
    # 결측치 제거
    #func_result = preproc.FillMissing(columnName = ['gender'], newColumn = False, nanVals=None, fillVal=None, descriptive=3, is_listview=False, is_preview=False)

    # # 결측치 값 채우기- 특정 값으로 채우기
    # func_result = preproc.FillMissing(columnName = ['tenure', 'SeniorCitizen'], newColumn = False, nanVals=None, fillVal=10, descriptive=-1, is_listview=False, is_preview=False)

    # # 결측치 값 채우기- 함수를 이용한 값 채우기
    # func_result = preproc.FillMissing(columnName = ['tenure', 'SeniorCitizen'], newColumn = False, nanVals=None, fillVal=None, descriptive=2, is_listview=False, is_preview=False)

    # 전처리 필터링 기능 테스트 (Filtering)
    ### tenure - "X >= 5" / "X >= 5 AND X <= 20" / "X <= 3 OR X >= 20"
    ### gender - "X == Female"
    ### Contract - "X == One year OR X == Two year"
    # condition = "X > 0"
    # func_result = preproc.Filtering(columnName = ['gender'], newColumn = True, condition = condition, is_listview=False, is_preview=False)

    # 전처리 값 대체 기능 테스트 (Replace)
    # func_result = preproc.ReplaceValue(columnName = ['Partner', 'Dependents'], newColumn = False, mapping = {'0':'False', '1':'True'}, is_listview=False, is_preview=True)
    # func_result = preproc.ReplaceValue(columnName = ['tenure'], newColumn = False, mapping = {'2':'99999', '10':'99999'}, is_listview=False, is_preview=True)
    #func_result = preproc.ReplaceValue(columnName = ['Partner'], newColumn = False, mapping = {'Yes':'1', 'No':'0'}, is_listview=False, is_preview=True)

    # func_result = preproc.ReplaceRangeValue(columnName = ['gender'], newColumn = True, rangeList = [['0','20','F'],['21','40','D'], ['41','60','C'], ['61','80','B'], ['81','100','A']], is_listview=False, is_preview=False)

    # func_result = preproc.GroupBy(columnName = ['gender', 'tenure'], method='MAX', is_listview=False, is_preview=False)
    print('========')
    print('meta정보3 : ', func_result[0])
    print('dataframe :\n', func_result[1])
    print('error massage :', func_result[2])
    # 데이터 기술통계표, 빈도표, 상관계수 테스트
    # result = preproc.getDescribe()
    # print('기술통계표: ', result[0])
    # print('========')
    # print('빈도표 :\n', result[1])
    # print('========')
    # print('상관계수표: ', preproc.getCorrelation())
