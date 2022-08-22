"""
  模块描述：彩信接口响应
  @author 8526
  @date 2022-05-12 10:15:33
  版权所有 Copyright www.dahantc.com
"""


# 彩信提交响应
class MmsSendResponse:
    def __init__(self, head, body):
        # 返回头
        self.head = head
        # 返回体
        self.body = body


# 彩信提交响应头
class MmsHeadRes:
    def __init__(self, result, cmdId):
        # 命令是否成功接收。0：接收成功
        self.result = result
        # 命令id
        self.cmdId = cmdId


# 彩信提交响应body
class MmsSubmitBodyRes:
    def __init__(self, submitResult):
        self.submitResult = submitResult


# 彩信提交结果集
class SubmitResult:
    def __init__(self, response):
        # 命令是否成功接收。0：接收成功
        self.response = response


# 彩信具体结果
class SubmitResponse:
    def __init__(self, status, phone, msgid):
        # 彩信提交响应码
        self.status = status
        # 手机号码,对应请求包中的一个手机号码
        self.phone = phone
        # 当result等于0时，该值有效， 本MT彩信包的唯一标识，32位UUID，
        self.msgid = msgid


def mmsSendResponseDecoder(obj):
    if obj is None:
        return None
    return MmsSendResponse(mmsHeadResDecoder(obj.get('root').get('head')),
                           mmsSubmitBodyResDecoder(obj.get('root').get('body')))


def mmsHeadResDecoder(obj):
    if obj is None:
        return None
    return MmsHeadRes(obj.get('cmdId'), obj.get('result'))


def mmsSubmitBodyResDecoder(obj):
    if obj is None:
        return None
    return MmsSubmitBodyRes(submitResultDecoder(obj.get('submitResult')))


def submitResultDecoder(obj):
    if obj is None:
        return None
    data = []
    for val in obj:
        data.append(submitResponseDecoder(val.get('response')))
    return data


def submitResponseDecoder(obj):
    if obj is None:
        return None
    data = []
    for val in obj:
        data.append(SubmitResponse(val.get('status'), val.get('phone'), val.get('msgid')))
    return data


# 彩信报告响应
class MmsReportResponse:
    def __init__(self, head, body):
        self.head = head
        self.body = body


# 彩信报告响应body
class MmsReportBodyRes:
    def __init__(self, reportMsg):
        self.reportMsg = reportMsg


# 报告体
class ReportMsg:
    def __init__(self, phone, msgid, status, statusDesp, reportTime):
        # 手机号码
        self.phone = phone
        # msgid
        self.msgid = msgid
        # 彩信发送结果：0—成功；1—接口处理失败； 2—运营商网关失败
        self.status = status
        # 发送状态描述
        self.statusDesp = statusDesp
        # 状态报告时间
        self.reporttime = reportTime


def mmsReportResponseDecoder(obj):
    if obj is None:
        return None
    return MmsReportResponse(mmsHeadResDecoder(obj.get('root').get('head')),
                             mmsReportBodyResDecoder(obj.get('root').get('body')))


def mmsReportBodyResDecoder(obj):
    if obj is None:
        return None
    data = []
    if type(obj.get('reportMsg')) is dict:
        data.append(reportMsgDecoder(obj.get('reportMsg')))
    else:
        for val in obj.get('reportMsg'):
            data.append(reportMsgDecoder(val))
    return data


def reportMsgDecoder(obj):
    if obj is None:
        return None
    return ReportMsg(obj.get('phone'), obj.get('msgid'), obj.get('status'), obj.get('statusDesp'),
                              obj.get('reporttime'))
