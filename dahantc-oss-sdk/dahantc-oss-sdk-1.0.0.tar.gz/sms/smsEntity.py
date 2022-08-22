"""
  模块描述：短信模块参数类
  @author 8522
  @date 2022-05-11 14:00:38
  版权所有 Copyright www.dahantc.com
"""
import common.entity as entity

# 短信下发参数
from common.util import EntityUtil


class BaseSendData:
    # 该批短信编号(32位UUID)，需保证唯一，不填的话响应里会给一个系统生成的
    msgid = ""

    # 接收手机号码，多个手机号码用英文逗号分隔，最多1000个，国际号码格式为+国别号手机号，
    # 号码示例：+85255441234（国际手机号前如果带0会去0后下发）
    phones = ""

    # 短信内容，最多1000个汉字，内容中不要出现【】[]这两种方括号，该字符为签名专用
    content = ""

    # 短信签名，该签名需要提前报备，生效后方可使用，不可修改，不填使用默认签名，示例如：【大汉三通】
    sign = ""

    # 短信签名对应子码(大汉三通提供)+自定义扩展子码(选填)，必须是数字，未填使用签名对应子码，
    # 无法前匹配签名对应子码则使用签名对应子码+所填子码，通常建议不填
    subcode = ""

    # 定时发送时间，格式yyyyMMddHHmm，为空或早于当前时间则立即发送
    sendtime = ""

    # 终端客户自定义参数params（总长度限制为1000），参数类型为Map，如果携带此参数会在状态报告里返回，
    # 示例：”params”:{“param1”:”aaa”,”param2”:”bbb”}（param1的位置如果写ctcTheme的话，
    # ctcTheme的值会额外作为短信主题统计在大汉平台的短信主题统计里）
    # 类型：Map <String, String>
    params = {}

    # 是否支持长链接替换下发，填true时内容中查找符合规则
    # （以http或https或ftp或weixin://开头，长度大于14位且长链接两头有空格或\t或换行）
    # 的第一个长链接进行替换（一个号码对应一个短链接）后下发。(若短信内容存在多个url地址,将会以第一个url替换)
    urlReplace = ""

    # 个性回调地址，该条短信的状态报告会推送到该回调地址，注意：
    # 1)使用该参数需提前在客户服务群告知使用账号，我司需对账号配置方生效。
    # 2)回调地址固定的客户不需要使用此参数，可以直接根据推送接口进行对接
    # 3)可以配置默认推送地址，不带callbackurl的情况下使用默认地址推送
    callbackurl = ""

    def __init__(self, msgid, phones, content, sign, subcode, sendtime, params, urlReplace, callbackurl):
        self.msgid = msgid
        self.phones = phones
        self.content = content
        self.sign = sign
        self.subcode = subcode
        self.sendtime = sendtime
        self.params = params
        self.urlReplace = urlReplace
        self.callbackurl = callbackurl

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return BaseSendData(EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "phones"),
                            EntityUtil.getValue(val, "content"), EntityUtil.getValue(val, "sign"),
                            EntityUtil.getValue(val, "subcode"), EntityUtil.getValue(val, "sendtime"),
                            EntityUtil.getValue(val, "params"), EntityUtil.getValue(val, "urlReplace"),
                            EntityUtil.getValue(val, "callbackurl"))


# 短信下发(不同内容多个号码)-入参
class SmsSendBatchParam(entity.BaseParam):
    # 短信数集合，最多1000个
    # 类型：List<BaseSendData>
    data = []

    def __init__(self, account, password, data):
        super().__init__(account, password)
        self.data = data

    # class转字典
    def parseDict(self):
        temp = self.data
        res = {"account": self.account, "password": self.password, "data": []}
        for baseSendData in temp:
            res["data"].append(baseSendData.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = SmsSendBatchParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"), [])
        if "data" in val.keys():
            for baseSendData in val["data"]:
                res.data.append(BaseSendData.parseObj(baseSendData))
        return res


# 短信下发(相同内容多个号码)-入参
class SmsSendParam(entity.BaseParam, BaseSendData):
    def __init__(self, account, password, msgid, phones, content, sign, subcode, sendtime, params, urlReplace,
                 callbackurl):
        super().__init__(account, password)
        self.msgid = msgid
        self.phones = phones
        self.content = content
        self.sign = sign
        self.subcode = subcode
        self.sendtime = sendtime
        self.params = params
        self.urlReplace = urlReplace
        self.callbackurl = callbackurl

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsSendParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                            EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "phones"),
                            EntityUtil.getValue(val, "content"), EntityUtil.getValue(val, "sign"),
                            EntityUtil.getValue(val, "subcode"), EntityUtil.getValue(val, "sendtime"),
                            EntityUtil.getValue(val, "params"), EntityUtil.getValue(val, "urlReplace"),
                            EntityUtil.getValue(val, "callbackurl"))


# 短信下发(相同内容多个号码；签名在内容里)-入参
class SmsSendWSignParam(entity.BaseParam):
    # 该批短信编号(32位UUID)，需保证唯一，不填的话响应里会给一个系统生成的
    msgid = ""

    # 接收手机号码，多个手机号码用英文逗号分隔，最多1000个，国际号码格式为+国别号手机号，
    # 号码示例：+85255441234（国际手机号前如果带0会去0后下发）
    phones = ""

    # 短信内容，最多1000个汉字，内容中不要出现【】[]这两种方括号，该字符为签名专用
    content = ""

    # 短信签名对应子码(大汉三通提供)+自定义扩展子码(选填)，必须是数字，未填使用签名对应子码，
    # 无法前匹配签名对应子码则使用签名对应子码+所填子码，通常建议不填
    subcode = ""

    # 定时发送时间，格式yyyyMMddHHmm，为空或早于当前时间则立即发送
    sendtime = ""

    # 终端客户自定义参数params（总长度限制为1000），参数类型为Map，如果携带此参数会在状态报告里返回，
    # 示例：”params”:{“param1”:”aaa”,”param2”:”bbb”}（param1的位置如果写ctcTheme的话，
    # ctcTheme的值会额外作为短信主题统计在大汉平台的短信主题统计里）
    # 类型：Map <String, String>
    params = {}

    # 是否支持长链接替换下发，填true时内容中查找符合规则
    # （以http或https或ftp或weixin://开头，长度大于14位且长链接两头有空格或\t或换行）
    # 的第一个长链接进行替换（一个号码对应一个短链接）后下发。(若短信内容存在多个url地址,将会以第一个url替换)
    urlReplace = ""

    # 个性回调地址，该条短信的状态报告会推送到该回调地址，注意：
    # 1)使用该参数需提前在客户服务群告知使用账号，我司需对账号配置方生效。
    # 2)回调地址固定的客户不需要使用此参数，可以直接根据推送接口进行对接
    # 3)可以配置默认推送地址，不带callbackurl的情况下使用默认地址推送
    callbackurl = ""

    def __init__(self, account, password, msgid, phones, content, subcode, sendtime, params, urlReplace, callbackurl):
        super().__init__(account, password)
        self.msgid = msgid
        self.phones = phones
        self.content = content
        self.subcode = subcode
        self.sendtime = sendtime
        self.params = params
        self.urlReplace = urlReplace
        self.callbackurl = callbackurl

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsSendWSignParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                 EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "phones"),
                                 EntityUtil.getValue(val, "content"), EntityUtil.getValue(val, "subcode"),
                                 EntityUtil.getValue(val, "sendtime"), EntityUtil.getValue(val, "params"),
                                 EntityUtil.getValue(val, "urlReplace"), EntityUtil.getValue(val, "callbackurl"))


# 短信产品余额参数
class SmsBalance:
    # 短信剩余金额，保留3位小数，单位：元；
    amount = ""

    # 剩余短信条数
    number = ""

    # 短信冻结金额，保留3位小数，单位：元。
    freeze = ""

    def __init__(self, amount, number, freeze):
        self.amount = amount
        self.number = number
        self.freeze = freeze

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsBalance(EntityUtil.getValue(val, "amount"), EntityUtil.getValue(val, "number"),
                          EntityUtil.getValue(val, "freeze"))


# 彩信产品余额参数
class MmsBalance:
    # 彩信剩余金额，保留3位小数，单位：元；
    amount = ""

    # 剩余彩信条数；
    number = ""

    # 彩信冻结金额，保留3位小数，单位：元 = ""
    freeze = ""

    def __init__(self, amount, number, freeze):
        self.amount = amount
        self.number = number
        self.freeze = freeze

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return MmsBalance(EntityUtil.getValue(val, "amount"), EntityUtil.getValue(val, "number"),
                          EntityUtil.getValue(val, "freeze"))


# 钱包余额参数
class WalletBalance:
    # 钱包剩余金额，保留3位小数，单位：元；
    amount = ""

    # 语音冻结金额，保留3位小数，单位：元；
    voiceFreeze = ""

    # 钱包冻结金额，保留3位小数，单位：元；
    freeze = ""

    def __init__(self, amount, voiceFreeze, freeze):
        self.amount = amount
        self.voiceFreeze = voiceFreeze
        self.freeze = freeze

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return WalletBalance(EntityUtil.getValue(val, "amount"), EntityUtil.getValue(val, "voiceFreeze"),
                             EntityUtil.getValue(val, "freeze"))


# 获取上行回复短信(接收手机回复的短信)-入参
class DeliverParam(entity.BaseParam):
    def __init__(self, account, password):
        super().__init__(account, password)

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return DeliverParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"))


# 获取状态报告(确认手机接收情况)-入参
class ReportParam(entity.BaseParam):
    def __init__(self, account, password):
        super().__init__(account, password)

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return DeliverParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"))


# 查询余额(也包括彩信,语音,国际短信余额)-入参
class BalanceParam(entity.BaseParam):
    def __init__(self, account, password):
        super().__init__(account, password)

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return DeliverParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"))


# 查询余额(也包括彩信,语音,国际短信余额)
class BalanceResponse(entity.BaseResult):
    # 短信产品余额
    # 类型：SmsBalance
    smsBalance = {}

    # 彩信产品余额
    # 类型：MmsBalance
    mmsBalance = {}

    # 钱包余额
    # 类型：WalletBalance
    walletBalance = {}

    def __init__(self, result, desc, smsBalance, mmsBalance, walletBalance):
        super().__init__(result, desc, "")
        self.smsBalance = smsBalance
        self.mmsBalance = mmsBalance
        self.walletBalance = walletBalance

    # class转字典
    def parseDict(self):
        res = {"result": self.result, "desc": self.desc, "smsBalance": self.smsBalance.parseDict(),
               "mmsBalance": self.smsBalance.parseDict(), "walletBalance": self.smsBalance.parseDict()}
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = BalanceResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "desc"), {}, {}, {})
        keys = val.keys()
        if "smsBalance" in keys:
            res.smsBalance = SmsBalance.parseObj(val["smsBalance"])
        if "mmsBalance" in keys:
            res.mmsBalance = MmsBalance.parseObj(val["mmsBalance"])
        if "walletBalance" in keys:
            res.walletBalance = WalletBalance.parseObj(val["walletBalance"])
        return res


# 短信下发(相同内容多个号码)-返参
class SmsSendResponse(entity.BaseResult):
    # 该批短信编号
    msgid = ""

    # 如果提交的号码中含有错误（格式）号码将在此显示
    failPhones = ""

    # 有长链接地址替换时返回该参数，短链接的任务编号
    taskid = ""

    def __init__(self, result, desc, msgid, failPhones, taskid):
        super().__init__(result, desc, "")
        self.msgid = msgid
        self.failPhones = failPhones
        self.taskid = taskid

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsSendResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "desc"),
                               EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "failPhones"),
                               EntityUtil.getValue(val, "taskid"))


# 短信下发(相同内容多个号码)-返参
class SmsSendWSignResponse(entity.BaseResult):
    # 该批短信编号
    msgid = ""

    # 如果提交的号码中含有错误（格式）号码将在此显示
    failPhones = ""

    # 有长链接地址替换时返回该参数，短链接的任务编号
    taskid = ""

    def __init__(self, result, desc, msgid, failPhones, taskid):
        super().__init__(result, desc, "")
        self.msgid = msgid
        self.failPhones = failPhones
        self.taskid = taskid

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SmsSendWSignResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "desc"),
                                    EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "failPhones"),
                                    EntityUtil.getValue(val, "taskid"))


# 短信下发(不同内容多个号码)参数
class BatchSend:
    # 该批短信编号
    msgid = ""

    # 该批短信提交结果；说明请参照：提交响应错误码
    status = ""

    # 如果提交的号码中含有错误（格式）号码将在此显示
    failPhones = ""

    # 有长链接地址替换时返回该参数，短链接的任务编号
    taskid = ""

    def __init__(self, msgid, status, failPhones, taskid):
        self.msgid = msgid
        self.status = status
        self.failPhones = failPhones
        self.taskid = taskid

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return BatchSend(EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "status"),
                         EntityUtil.getValue(val, "failPhones"), EntityUtil.getValue(val, "taskid"))


# 短信下发(不同内容多个号码)-返参
class BatchSendResponse(entity.BaseResult):
    # 短信发送响应集
    # 类型：List<BatchSend>
    data = []

    def __init__(self, result, desc, data):
        super().__init__(result, desc, "")
        self.data = data

    # class转字典
    def parseDict(self):
        temp = self.data
        res = {"result": self.result, "desc": self.desc, "data": []}
        for batchSend in temp:
            res["data"].append(batchSend.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = BatchSendResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "desc"), [])
        if "data" in val.keys():
            for batchSend in val["data"]:
                res.data.append(BatchSend.parseObj(batchSend))
        return res


# 上行数据
class DeliverData:
    # 上行手机号码
    phone = ""

    # 上行短信内容
    content = ""

    # 子号码
    subcode = ""

    # 上行接收时间，格式yyyy-MM-dd HH:mm:ss
    delivertime = ""

    def __init__(self, phone, content, subcode, delivertime):
        self.phone = phone
        self.content = content
        self.subcode = subcode
        self.delivertime = delivertime

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return DeliverData(EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "status"),
                           EntityUtil.getValue(val, "failPhones"), EntityUtil.getValue(val, "taskid"))


# 获取上行回复短信(接收手机回复的短信)-返参
class DeliverResponse(entity.BaseResult):
    # 回复短信集
    # 格式：List<DeliverData>
    delivers = []

    def __init__(self, result, desc, delivers):
        super().__init__(result, desc, "")
        self.delivers = delivers

    # class转字典
    def parseDict(self):
        temp = self.delivers
        res = {"result": self.result, "desc": self.desc, "delivers": []}
        for deliverData in temp:
            res["delivers"].append(deliverData.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = DeliverResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "desc"), [])
        if "delivers" in val.keys():
            for deliverData in val["delivers"]:
                res.delivers.append(DeliverData.parseObj(deliverData))
        return res


# 短信下发状态报告
class ReportData:
    # 短信编号
    msgid = ""

    # 下行手机号码
    phone = ""

    # 短信发送结果：0——成功；1——接口处理失败；2——运营商网关失败
    status = ""

    # 状态报告描述
    desc = ""

    # 当status为1时,表示平台返回错误码，参考:状态报告错误码。当status为0或2时，表示运营商网关返回的原始值
    wgcode = ""

    # 客户提交时间格式为yyyy-MM-dd HH:mm:ss
    submitTime = ""

    # 大汉三通发送时间格式为yyyy-MM-dd HH:mm:ss
    sendTime = ""

    # 状态报告接收时间格式为yyyy-MM-dd HH:mm:ss
    time = ""

    # 长短信条数（接口处理失败只给一条）
    smsCount = 0

    # 长短信第几条标示
    smsIndex = 0

    def __init__(self, msgid, phone, status, desc, wgcode, submitTime, sendTime, time, smsCount, smsIndex):
        self.msgid = msgid
        self.phone = phone
        self.status = status
        self.desc = desc
        self.wgcode = wgcode
        self.submitTime = submitTime
        self.sendTime = sendTime
        self.time = time
        self.smsCount = smsCount
        self.smsIndex = smsIndex

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return ReportData(EntityUtil.getValue(val, "msgid"), EntityUtil.getValue(val, "phone"),
                          EntityUtil.getValue(val, "status"), EntityUtil.getValue(val, "desc"),
                          EntityUtil.getValue(val, "wgcode"), EntityUtil.getValue(val, "submitTime"),
                          EntityUtil.getValue(val, "sendTime"), EntityUtil.getValue(val, "time"),
                          EntityUtil.getValue(val, "smsCount"), EntityUtil.getValue(val, "smsIndex"))


# 获取状态报告(确认手机接收情况)-返参
class ReportResponse(entity.BaseResult):
    # 报告集
    # 类型：List<ReportData>
    reports = []

    def __init__(self, result, desc, reports):
        super().__init__(result, desc, "")
        self.reports = reports

    # class转字典
    def parseDict(self):
        temp = self.reports
        res = {"result": self.result, "desc": self.desc, "reports": []}
        for reportData in temp:
            res["reports"].append(reportData.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = ReportResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "desc"), [])
        if "reports" in val.keys():
            for reportData in val["reports"]:
                res.reports.append(ReportData.parseObj(reportData))
        return res