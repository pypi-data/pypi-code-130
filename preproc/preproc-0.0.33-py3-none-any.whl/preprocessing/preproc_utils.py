import json


# 전처리 Meta 정보 Json Object로 만들기
class MyJsonObject(object):
    def __init__(self, jsondict={}):
        for k, v in jsondict.items():
            # print(k, v)
            setattr(self, k, v)

    def set(self, key, value):
        setattr(self, key, value)

    def setMany(self, jsondict):
        for k, v in jsondict.items():
            setattr(self, k, v)

    def print(self):
        # print(self.)
        print(json.dumps(self.__dict__, indent=2))
    
    def get(self, key):
        getattr(self, key)

# NewColumn 인자 반영 함수, Column name 이름 변경 및 추가
def replaceOrAddColumn(df, newColVal, newColumn, meta):
    newColName = meta.columnName + "_" + meta.name
    if newColumn:
        df[newColName] = newColVal
        meta.set("newColumn", [newColName])
    else:
        df[meta.columnName] = newColVal