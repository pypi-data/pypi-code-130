"""
  模块描述：异常号码检测模块参数类
  @author 8522
  @date 2022-05-11 15:00:38
  版权所有 Copyright www.dahantc.com
"""
from common import entity
from common.util import EntityUtil


# 号码属性查询-入参
class QryPhonePropertyParam(entity.BaseParam):
    # 待查询手机号，必填(号码个数最大值:1000个)
    phones = ""

    def __init__(self, account, password, phones):
        super().__init__(account, password)
        self.phones = phones

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return QryPhonePropertyParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                     EntityUtil.getValue(val, "phones"))


# 号码状态查询-入参
class QryPhoneStatusParam(entity.BaseParam):
    # 待查询手机号，必填(号码个数最大值:1000个)
    phones = ""

    def __init__(self, account, password, phones):
        super().__init__(account, password)
        self.phones = phones

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return QryPhoneStatusParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                   EntityUtil.getValue(val, "phones"))


# 号码属性参数
class PhoneProperty:
    # 号码
    phone = ""
    # 接口响应码
    resp = 0
    # 运营商
    operatorText = ""
    # 属性码
    prop = ""
    # 手机属性验证结，说明请参照：号码属性描述
    propText = ""
    # 手机号状态
    stateText = ""
    # 权重，值越大危险系数越高
    weight = ""

    def __init__(self, phone, resp, operatorText, prop, propText, stateText, weight):
        self.phone = phone
        self.resp = resp
        self.operatorText = operatorText
        self.prop = prop
        self.propText = propText
        self.stateText = stateText
        self.weight = weight

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return PhoneProperty(EntityUtil.getValue(val, "phone"), EntityUtil.getValue(val, "resp"),
                             EntityUtil.getValue(val, "operatorText"), EntityUtil.getValue(val, "prop"),
                             EntityUtil.getValue(val, "propText"), EntityUtil.getValue(val, "stateText"),
                             EntityUtil.getValue(val, "weight"))


# 号码属性查询-返参
class QryPhonePropertyResponse(entity.BaseResult):
    # 号码属性集合
    # 类型：List<PhoneProperty>
    responses = []

    def __init__(self, result, desc, responses):
        super().__init__(result, desc, "")
        self.responses = responses

    # class转字典
    def parseDict(self):
        temp = self.responses
        res = {"account": self.result, "password": self.desc, "responses": []}
        for phoneProperty in temp:
            res["responses"].append(phoneProperty.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = QryPhonePropertyResponse(EntityUtil.getValue(val,"result"),EntityUtil.getValue(val,"desc"),[])
        if "responses" in val.keys():
            for phoneProperty in val["responses"]:
                res.responses.append(PhoneProperty.parseObj(phoneProperty))
        return res


# 电话号码状态参数
class PhoneStatus:
    # 号码
    phone = ""
    # 接口响应码
    resp = 0
    # 原网移动通信运营商（Mobile telecom carrier） 1：中国移动；2：中国联通；3：中国电信
    oldOperator = ""
    # 现移动通信运营商（Mobile telecom carrier）1：中国移动；2：中国联通；3：中国电信。当号码未转网时，oldOperator 和operator值相同
    operator = ""
    # 手机状态 1：正常号码；2：异常号码（空号，停机，欠费等）；3：未知状态（短信发送不成功的号码）；4：查询无结果
    stat = ""
    # 号码归属地:省
    region = ""
    # 号码归属地:市
    cityName = ""

    def __init__(self, phone, resp, oldOperator, operator, stat, region, cityName):
        self.phone = phone
        self.resp = resp
        self.oldOperator = oldOperator
        self.operator = operator
        self.stat = stat
        self.region = region
        self.cityName = cityName

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return PhoneStatus(EntityUtil.getValue(val, "phone"), EntityUtil.getValue(val, "resp"),
                           EntityUtil.getValue(val, "oldOperator"), EntityUtil.getValue(val, "operator"),
                           EntityUtil.getValue(val, "stat"), EntityUtil.getValue(val, "region"),
                           EntityUtil.getValue(val, "cityName"))


# 查询号码状态-返参
class QryPhoneStatusResponse(entity.BaseResult):
    # 号码状态信息集
    # 类型：List<PhoneStatus>
    responses = []

    def __init__(self, result, desc, responses):
        super().__init__(result, desc, "")
        self.responses = responses

    # class转字典
    def parseDict(self):
        temp = self.responses
        res = {"account": self.result, "password": self.desc, "responses": []}
        for phoneStatus in temp:
            res["responses"].append(phoneStatus.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = QryPhoneStatusResponse(EntityUtil.getValue(val,"result"),EntityUtil.getValue(val,"desc"),[])
        if "responses" in val.keys():
            for phoneStatus in val["responses"]:
                res.responses.append(PhoneStatus.parseObj(phoneStatus))
        return res