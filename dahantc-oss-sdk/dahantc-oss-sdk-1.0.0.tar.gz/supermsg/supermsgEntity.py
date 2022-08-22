"""
  模块描述：超级短信模块参数类
  @author 8522
  @date 2022-05-11 16:33:38
  版权所有 Copyright www.dahantc.com
"""
from common import entity
from common.util import EntityUtil


# 审核报告查询-入参
class ExamineReportParam(entity.BaseParam):
    # 命令ID，用来区分调用服务（不用传）
    cmdId = "003"
    # 模板编号
    templateNo = ""

    def __init__(self, account, password, templateNo):
        super().__init__(account, password)
        self.templateNo = templateNo

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return ExamineReportParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                  EntityUtil.getValue(val, "templateNo"))


# 获取超级短信状态报告-入参
class QrySendReportParam(entity.BaseParam):
    # 命令ID，用来区分调用服务（不用传）
    cmdId = "004"

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
        return QrySendReportParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"))


# 超级短信下发-入参
class SendSupermsgParam(entity.BaseParam):
    # 命令ID，用来区分调用服务（不用传）
    cmdId = "002"
    # 模板编号
    templateNo = ""
    # 必填	接收手机号码，多个手机号码用英文逗号分隔
    mobiles = ""
    # 选填	短信签名对应子码(大汉三通提供)+自定义扩展子码(选填)，必须是数字
    subcode = ""
    # 选填	模板变量内容，多个时用#####按顺序拼接，确保变量个数正确及各个变量值在限定范围内，无模板变量时该值不填
    templateParams = ""

    def __init__(self, account, password, templateNo, mobiles, subcode, templateParams):
        super().__init__(account, password)
        self.templateNo = templateNo
        self.mobiles = mobiles
        self.subcode = subcode
        self.templateParams = templateParams

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SendSupermsgParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                 EntityUtil.getValue(val, "templateNo"), EntityUtil.getValue(val, "mobiles"),
                                 EntityUtil.getValue(val, "subcode"), EntityUtil.getValue(val, "templateParams"))


# 超级短信模板参数类
class SupermsgTemp:
    # 文件名
    name = ""
    # 文件内容，字节码格式
    content = ""
    # 标识是第几帧，第几个素材，格式为： 帧数_素材数
    index = ""

    def __init__(self, name, content, index):
        self.name = name
        self.content = content
        self.index = index

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SupermsgTemp(EntityUtil.getValue(val, "name"), EntityUtil.getValue(val, "content"),
                            EntityUtil.getValue(val, "index"))


# 上传超级短信模板-入参
class UpSupermsgTempParam(entity.BaseParam):
    # 命令ID，用来区分调用服务（不用传）
    cmdId = "002"
    # 短信主题
    title = ""
    # 模板素材集
    # 图片规格：【格式】jpeg、jpg、gif、bmp、png（尽量不使用png格式，有些运营商不支持）
    # 视频规格：【格式】mp4、3gp
    # 音频规格：【格式】amr、mpeg、mp3、aac
    # 类型：List<SupermsgTemp>
    content = []

    def __init__(self, account, password, title, content):
        super().__init__(account, password)
        self.title = title
        self.content = content

    # class转字典
    def parseDict(self):
        temp = self.content
        res = {"account": self.account, "password": self.password, "content": []}
        for cont in temp:
            res["content"].append(cont.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = UpSupermsgTempParam(EntityUtil.getValue(val, "account"), EntityUtil.getValue(val, "password"),
                                  EntityUtil.getValue(val, "title"), [])
        if "content" in val.keys():
            for supermsgTemp in val["content"]:
                res.content.append(SupermsgTemp.parseObj(supermsgTemp))
        return res


# 超级短信审核状态查询-返参
class ExamineReportResponse(entity.BaseResult):
    def __init__(self, result, msg):
        super().__init__(result, "", msg)

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return ExamineReportResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "msg"))


# 超级短信下发状态报告参数
class SendReport:
    # 批次号Id
    msgId = ""
    # 手机号码,对应请求包中的一个手机号码
    mobile = ""
    # 短信发送结果：0—成功（如果配置了需要下载状态，status为0时errorCode为RECEIVD表示下载成功）；1—接口处理失败； 2—运营商网关失败
    status = ""
    # 当status为1时，可参考：处理失败错误码；当status为2时，表示运营商网关返回的原始值
    errorCode = ""
    # 错误码描述
    statusDesp = ""
    # 状态报告时间
    reportTime = ""

    def __init__(self, msgId, mobile, status, errorCode, statusDesp, reportTime):
        self.msgId = msgId
        self.mobile = mobile
        self.status = status
        self.errorCode = errorCode
        self.statusDesp = statusDesp
        self.reportTime = reportTime

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SendReport(EntityUtil.getValue(val, "msgId"), EntityUtil.getValue(val, "mobile"),
                          EntityUtil.getValue(val, "status"), EntityUtil.getValue(val, "errorCode"),
                          EntityUtil.getValue(val, "statusDesp"), EntityUtil.getValue(val, "reportTime"))


# 获取超级短信下发报告-返参
class QrySendReportResponse(entity.BaseResult):
    # 报告集
    # 类型：List<SendReport>
    reports = []

    def __init__(self, result, msg, reports):
        super().__init__(result, "", msg)
        self.reports = reports

    # class转字典
    def parseDict(self):
        temp = self.reports
        res = {"result": self.result, "msg": self.msg, "reports": []}
        for sendReport in temp:
            res["reports"].append(sendReport.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        res = QrySendReportResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "msg"), [])
        if "reports" in val.keys():
            for sendReport in val["reports"]:
                res.reports.append(SendReport.parseObj(sendReport))
        return res


# 超级短信下发-返参
class SendSupermsgResponse(entity.BaseResult):
    # 批次号Id
    msgId = ""
    # 报告集
    # 类型：List<SendSupermsgResult>
    reports = []

    def __init__(self, result, msg, msgId, reports):
        super().__init__(result, "", msg)
        self.msgId = msgId
        self.reports = reports

    # class转字典
    def parseDict(self):
        temp = self.reports
        res = {"result": self.result, "msg": self.msg, "reports": []}
        for sendSupermsgResult in temp:
            res["reports"].append(sendSupermsgResult.parseDict())
        return res

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        keys = val.keys()
        res = SendSupermsgResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "msg"),
                                   EntityUtil.getValue(val, "msgId"), [])
        if "reports" in keys:
            for sendSupermsgResult in val["reports"]:
                res.reports.append(SendSupermsgResult(sendSupermsgResult["status"], sendSupermsgResult["mobiles"]))
        return res


# 超级短信下发反馈参数
class SendSupermsgResult:
    # 状态
    status = ""
    # 号码集，多个逗号隔开
    mobiles = ""

    def __init__(self, status, mobiles):
        self.status = status
        self.mobiles = mobiles

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return SendSupermsgResult(EntityUtil.getValue(val, "status"), EntityUtil.getValue(val, "mobiles"))


# 上传超级短信模板-返参
class UpSupermsgTempResponse(entity.BaseResult):
    # 模板编号
    templateNo = ""

    def __init__(self, result, msg, templateNo):
        super().__init__(result, "", msg)
        self.templateNo = templateNo

    # class转字典
    def parseDict(self):
        return self.__dict__

    # 将字典转换成class
    @staticmethod
    def parseObj(val):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return UpSupermsgTempResponse(EntityUtil.getValue(val, "result"), EntityUtil.getValue(val, "msg"),
                                      EntityUtil.getValue(val, "templateNo"))
