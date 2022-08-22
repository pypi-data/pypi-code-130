"""
  模块描述：短信模板模块参数类
  @author 8522
  @date 2022-05-11 14:00:38
  版权所有 Copyright www.dahantc.com
"""
import common.entity as entity

# 短信模板参数
from common.util import EntityUtil


class SmsTemplateVariable:
    # name对应变量内容序号（序号从1开始，必填）
    name = ""

    # value对应具体内容；
    value = ""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsTemplateVariable(EntityUtil.getValue(val, "name"), EntityUtil.getValue(val, "value"))


# 短信模板参数
class SmsTemplateData:
    # 模板id
    id = ""

    # 对应模板内容的键值对集合
    # 类型：List<SmsTemplateVariable>
    variables = []

    def __init__(self, id, variables):
        self.id = id
        self.variables = variables

    # class转字典
    def parseDict(self):
        temp = self.variables
        res = {"account": self.id, "variables": []}
        for smsTemplateVariable in temp:
            res["variables"].append(smsTemplateVariable.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = SmsTemplateData(EntityUtil.getValue(val, "id"), [])
        if "variables" in val.keys():
            for smsTemplateVariable in val["variables"]:
                res.variables.append(SmsTemplateVariable.parseObj(smsTemplateVariable))
        return res

# 使用模板id下发-入参
class SmsTemplateSubmitParam(entity.BaseParam):
    # 必填	接收手机号码，多个手机号码用英文逗号分隔，最多1000个，国际号码格式为+国别号手机号，号码示例：+85255441234
    phones = ""

    # 必填	短信模板格式，id对应模板id，
    # variables对应模板内容的键值对集合，name对应变量内容序号（序号从1开始，必填），value对应具体内容；
    # 类型：SmsTemplateData
    template = {}

    # 选填	该批短信编号(32位UUID)，需保证唯一，不填的话响应里会给一个系统生成的
    msgid = ""

    # 选填	短信签名对应子码(大汉三通提供)+自定义扩展子码(选填)，
    # 必须是数字，未填使用签名对应子码，无法前匹配签名对应子码则使用签名对应子码+所填子码，通常建议不填
    subcode = ""

    # 选填	定时发送时间，格式yyyyMMddHHmm，为空或早于当前时间则立即发送
    sendtime = ""

    # 选填	终端客户自定义参数params（总长度限制为1000），参数类型为Map，
    # 如果携带此参数会在状态报告里返回，
    # 示例：”params”:{“param1”:”aaa”,”param2”:”bbb”}
    # （param1的位置如果写ctcTheme的话，ctcTheme的值会额外作为短信主题统计在大汉平台的短信主题统计里）
    # 类型：Map<String, String>
    params = ""

    # 选填	个性回调地址，该条短信的状态报告会推送到该回调地址，
    # 注意：1)使用该参数需提前在客户服务群告知使用账号，我司需对账号配置方生效。
    # 2)回调地址固定的客户不需要使用此参数，可以直接根据推送接口进行对接
    # 3)可以配置默认推送地址，不带callbackurl的情况下使用默认地址推送
    callbackurl = ""

    def __init__(self, account, password, phones, template, msgid, subcode, sendtime, params, callbackurl):
        super().__init__(account, password)
        self.phones = phones
        self.template = template
        self.msgid = msgid
        self.subcode = subcode
        self.sendtime = sendtime
        self.params = params
        self.callbackurl = callbackurl

    # class转字典
    def parseDict(self):
        res = {"account": self.account, "password": self.password, "phones": self.phones,
               "template": self.template.parseDict(), "msgid": self.msgid, "subcode": self.subcode,
               "sendtime": self.sendtime, "params": self.params, "callbackurl": self.callbackurl, }
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsTemplateSubmitParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                      EntityUtil.getValue(val, "phones"),
                                      SmsTemplateData.parseObj(EntityUtil.getValue(val, "template")),
                                      EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "subcode"),
                                      EntityUtil.getValue(val, "sendtime"), EntityUtil.getValue(val, "params"),
                                      EntityUtil.getValue(val, "callbackurl"))


# 短信模板上传-入参
class SmsTemplateUploadParam(entity.BaseParam):
    # 签名（必填）
    sign = ""

    # 变量采用：${n,m}的格式，匹配n到m个文字，n<m，必填
    content = ""

    # 备注。选填
    remark = ""

    def __init__(self, account, password, sign, content, remark):
        super().__init__(account, password)
        self.sign = sign
        self.content = content
        self.remark = remark

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsTemplateUploadParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                      EntityUtil.getValue(val, "sign"),EntityUtil.getValue(val, "content"),
                                      EntityUtil.getValue(val, "remark"))


# 模板删除-入参
class SmsTemplateShowParam(entity.BaseParam):
    # 模板编号，可以多个，用逗号分隔，必填
    templateIds = ""

    def __init__(self, account, password, templateIds):
        super().__init__(account, password)
        self.templateIds = templateIds

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsTemplateShowParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                      EntityUtil.getValue(val, "templateIds"))

# 模板删除-入参
class SmsTemplateDelParam(entity.BaseParam):
    # 模板编号，可以多个，用逗号分隔，必填
    templateIds = ""

    def __init__(self, account, password, templateIds):
        super().__init__(account, password)
        self.templateIds = templateIds

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsTemplateDelParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                    EntityUtil.getValue(val, "templateIds"))


# 模板删除详情
class SmsTemplateDelRes:
    # 模板id
    templateid = ""

    # 1删除成功；2删除失败（无效id）
    state = ""

    def __init__(self, templateid, state):
        self.templateid = templateid
        self.state = state

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsTemplateDelRes(EntityUtil.getValue(val, "templateid"), EntityUtil.getValue(val, "state"))


# 模板删除-返参
class SmsTemplateDelResponse(entity.BaseResult):
    # 模板信息集合
    # 类型：List<SmsTemplateDelRes>
    templateIds = []

    def __init__(self, result, desc, templateIds):
        super().__init__(result, desc, "")
        self.templateIds = templateIds

    # class转字典
    def parseDict(self):
        temp = self.templateIds
        res = {"result": self.result, "desc": self.desc, "templateIds": []}
        for smsTemplateDelRes in temp:
            res["templateIds"].append(smsTemplateDelRes.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = SmsTemplateDelResponse(EntityUtil.getValue(val,"result"),EntityUtil.getValue(val,"desc"),[])
        if "templateIds" in val.keys():
            for smsTemplateDelRes in val["templateIds"]:
                res.templateIds.append(SmsTemplateDelRes.parseObj(smsTemplateDelRes))
        return res


# 短信模板详情
class SmsTemplateDetailRes:
    # 模板id
    templateid = ""

    # 模板状态 0：待审核；1：审核通过；2：无效id/审核不通过
    state = ""

    # 驳回原因备注
    desc = ""

    def __init__(self, templateid, state, desc):
        self.templateid = templateid
        self.state = state
        self.desc = desc

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsTemplateDetailRes(EntityUtil.getValue(val, "templateid"), EntityUtil.getValue(val, "state"), EntityUtil.getValue(val, "desc"))


# 模板查询-返参
class SmsTemplateShowResponse(entity.BaseResult):
    # 模板信息集合
    # 类型：List<SmsTemplateDetailRes>
    templateIds = []

    def __init__(self, result, desc, templateIds):
        super().__init__(result, desc, "")
        self.templateIds = templateIds

    # class转字典
    def parseDict(self):
        temp = self.templateIds
        res = {"result": self.result, "desc": self.desc, "templateIds": []}
        for smsTemplateDetailRes in temp:
            res["templateIds"].append(smsTemplateDetailRes.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = SmsTemplateShowResponse(EntityUtil.getValue(val,"result"),EntityUtil.getValue(val,"desc"),[])
        if "templateIds" in val.keys():
            for smsTemplateDetailRes in val["templateIds"]:
                    res.templateIds.append(SmsTemplateDetailRes.parseObj(smsTemplateDetailRes))
        return res


# 模板下发-返参
class SmsTemplateSubmitResponse(entity.BaseResult):
    # 该批短信编号
    msgid = ""

    # 如果提交的号码中含有错误（格式）号码将在此显示，多个英文逗号隔开
    failPhones = ""

    def __init__(self, result, desc, msgid, failPhones):
        super().__init__(result, desc, "")
        self.msgid = msgid
        self.failPhones = failPhones

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsTemplateSubmitResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "desc"),
                                         EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "failPhones"))


# 短信模板上传-返参
class SmsTemplateUploadResponse(entity.BaseResult):
    # 上传模板返回的编号
    templateId = ""

    def __init__(self, result, desc, templateId):
        super().__init__(result, desc, "")
        self.templateId = templateId

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsTemplateUploadResponse(EntityUtil.getValue(val,"result"), EntityUtil.getValue(val,"desc"), EntityUtil.getValue(val,"templateId"))