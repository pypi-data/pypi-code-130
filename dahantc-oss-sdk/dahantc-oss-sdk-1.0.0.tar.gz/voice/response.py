"""
  模块描述：接口响应
  @author 8526
  @date 2022-05-12 14:15:33
  版权所有 Copyright www.dahantc.com
"""


# 语音提交响应
class VoiceSubmitResponse:
    def __init__(self, result, desc, data):
        # 该次请求提交结果
        self.result = result
        # 描述
        self.desc = desc
        # 响应数据集
        self.data = data


# 语音提交响应体
class VoiceResData:

    def __init__(self, status, desc, msgid, callee):
        # 状态码
        self.status = status
        # 描述
        self.desc = desc
        # 消息编号
        self.msgid = msgid
        # 被叫号码
        self.callee = callee


# 语音上传响应
class VocUploadResponse:
    def __init__(self, result, desc, mfid):
        # 该次请求提交结果
        self.result = result
        # 描述
        self.desc = desc
        # 上传成功后返回的语音文件id,当提交结果为DH:0000时有此值
        self.mfid = mfid


def voiceSubmitResponseDecoder(obj):
    if obj is None:
        return None
    return VoiceSubmitResponse(obj.get('result'), obj.get('desc'), voiceResDataDecoder(obj.get('data')))


def voiceResDataDecoder(obj):
    if obj is None:
        return None
    data = []
    for val in obj:
        data.append(VoiceResData(val.get('status'), val.get('desc'), val.get('msgid'), val.get('callee')))
    return data


def vocUploadResponseDecoder(obj):
    if obj is None:
        return None
    return VocUploadResponse(obj.get('result'), obj.get('desc'), obj.get('mfid'))


# 隐号AXB响应
class PhoneAXBResponse:
    def __init__(self, code, message, phone, msgid):
        # 提交结果状态码,0表示成功，其他代表失败
        self.code = code
        # 提交结果描述
        self.message = message
        # 小号，成功时返回
        self.phone = phone
        # 消息编号
        self.msgid = msgid


def phoneAXBResponseDecoder(obj):
    if obj is None:
        return None
    return PhoneAXBResponse(obj.get('code'), obj.get('message'), obj.get('phone'), obj.get('msgid'))


# 隐号AXN响应
class PhoneAXNResponse:
    def __init__(self, code, message, phone, msgid):
        # 提交结果状态码,0表示成功，其他代表失败
        self.code = code
        # 提交结果描述
        self.message = message
        # 小号，成功时返回
        self.phone = phone
        # 消息编号
        self.msgid = msgid


def phoneAXNResponseDecoder(obj):
    if obj is None:
        return None
    return PhoneAXNResponse(obj.get('code'), obj.get('message'), obj.get('phone'), obj.get('msgid'))


# 隐号AXxYB响应
class PhoneAXxYBResponse:
    def __init__(self, code, message, phoneX, phoneXx, msgid):
        # 提交结果状态码,0表示成功，其他代表失败
        self.code = code
        # 提交结果描述
        self.message = message
        # 小号，成功时返回
        self.phoneX = phoneX
        # 小号，成功时返回
        self.phoneXx = phoneXx
        # 消息编号
        self.msgid = msgid


def phoneAXxYBResponseDecoder(obj):
    if obj is None:
        return None
    return PhoneAXxYBResponse(obj.get('code'), obj.get('message'), obj.get('phoneX'), obj.get('phoneXx'),
                              obj.get('msgid'))


# 隐号AXYB响应
class PhoneAXYBResponse:
    def __init__(self, code, message, phoneX, phoneY, msgid):
        # 提交结果状态码,0表示成功，其他代表失败
        self.code = code
        # 提交结果描述
        self.message = message
        # 小号，成功时返回
        self.phoneX = phoneX
        # 小号，成功时返回
        self.phoneY = phoneY
        # 消息编号
        self.msgid = msgid


def phoneAXYBResponseDecoder(obj):
    if obj is None:
        return None
    return PhoneAXYBResponse(obj.get('code'), obj.get('message'), obj.get('phoneX'), obj.get('phoneY'),
                             obj.get('msgid'))


# 隐号释放响应
class PhoneReleaseResponse:
    def __init__(self, code, message, phone, msgid):
        # 提交结果状态码,0表示成功，其他代表失败
        self.code = code
        # 提交结果描述
        self.message = message
        # 已释放号码
        self.phone = phone
        # 消息编号
        self.msgid = msgid


def phoneReleaseResponseDecoder(obj):
    if obj is None:
        return None
    return PhoneReleaseResponse(obj.get('code'), obj.get('message'), obj.get('phone'), obj.get('msgid'))


# 隐号获取状态报告
class PhoneReportResponse:
    def __init__(self, result, desc, data):
        # 请求结果
        self.result = result
        # 提交结果描述
        self.desc = desc
        # 数据集
        self.data = data


# 隐号报告数据
class ReportData:
    def __init__(self, msgid, callid, callee, status, duration, phoneX, phoneXx, calltype, calledtimes, releasedir,
                 presskeys, starttime, answertime, reporttime, ringingtimeLong, recordurl, params):
        # 消息ID
        self.msgid = msgid
        # 隐号通话，话单唯一ID
        self.callid = callid
        # 被叫号码（如果是隐号通话此处为2个号码，以英文逗号分隔，例：A,B）
        self.callee = callee
        # 外呼状态码
        self.status = status
        # 通话时长。单位为秒
        self.duration = duration
        # 小号号码
        self.phoneX = phoneX
        #  AXxYB模式下的小号分机号
        self.phoneXx = phoneXx
        # 呼叫类型： 10：通话主叫 11：通话被叫 12：XYB-短信发送；AXxYB-收号呼叫
        # 13：短信接收 20：呼叫不允许 21: 未开户不允许 30：短信不允许 31：转接短信 126: 双呼
        self.calltype = calltype
        # 最终实际呼叫总次数。如果没有失败重呼，则值为1，表示只呼叫了一次
        self.calledtimes = calledtimes
        # 释放方向: 0 表示平台释放，1 表示主叫释放，2 表示被叫释放
        self.releasedir = releasedir
        # 用户的按键信息
        self.presskeys = presskeys
        # 发起呼叫时间。一般指实际呼叫发起的时间。"yyyy-MM-ddHH:mm:ss"
        self.starttime = starttime
        # 通话开始时间。一般指实际通话开始的时间。"yyyy-MM-ddHH:mm:ss"
        self.answertime = answertime
        # 状态报告时间。一般指实际呼叫结束的时间。"yyyy-MM-ddHH:mm:ss"
        self.reporttime = reporttime
        # 振铃时长(秒)
        self.ringingtimeLong = ringingtimeLong
        # 隐号通话录音文件下载路径，路径有效时间72小时
        self.recordurl = recordurl
        # 终端客户自定义参数params（总长度限制为1000）
        self.params = params


def phoneReportResponseDecoder(obj):
    if obj is None:
        return None
    return PhoneReportResponse(obj.get('result'), obj.get('desc'), reportDataDecoder(obj.get('data')))


def reportDataDecoder(obj):
    if obj is None:
        return None
    data = []
    for val in obj:
        data.append(ReportData(val.get('msgid'), val.get('callid'), val.get('callee'), val.get('status')
                               , val.get('duration'), val.get('phoneX'), val.get('phoneXx')
                               , val.get('calltype'), val.get('calledtimes'), val.get('releasedir')
                               , val.get('presskeys'), val.get('starttime'), val.get('answertime')
                               , val.get('reporttime'), val.get('ringingtimeLong'), val.get('recordurl'),
                               val.get('params')))
    return data
