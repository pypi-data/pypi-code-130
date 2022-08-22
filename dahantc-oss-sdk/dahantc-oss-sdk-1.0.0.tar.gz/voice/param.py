"""
  模块描述：语音接口参数
  @author 8526
  @date 2022-05-12 14:15:33
  版权所有 Copyright www.dahantc.com
"""

import common.entity as entity


class BaseJsonable(object):

    def parseDict(self):
        d = {}
        d.update(self.__dict__)
        return d


# 验证码语言发送参数
class CaptchaVoiceParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, needallresp, data):
        super().__init__(account, password)
        # 非必须（String）当值为字符串true时，响应中包含所有提交的msgid
        self.needallresp = needallresp
        # data
        self.data = data

    def parseDict(self):
        temp = self.data
        res = {"account": self.account, "password": self.password, "needallresp": self.needallresp, "data": []}
        for cont in temp:
            res["data"].append(cont.parseDict())
        return res


# 验证码语言发送data
class CaptchaVoiceData(BaseJsonable):
    def __init__(self, msgid, callee, text, playmode, calltype, params):
        # 消息编号ID，必须唯一，不可为空，最大长度64位
        self.msgid = msgid
        # 被叫号码。只能有一个号码。
        self.callee = callee
        # 验证码内容，只允许4~8位的数字验证码
        self.text = text
        # 放音模式： 0-只播放文本 1-只播放语音文件 ：2—先播放文本再文件，3—先播放文件再文本
        self.playmode = playmode
        # 外呼类型：1-验证码呼叫 2-语音文件呼叫  3-文本、文件混合呼叫
        self.calltype = calltype
        # 终端客户自定义参数params  {}
        self.params = params


# 文本外呼参数
class TextVoiceParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, needallresp, data):
        super().__init__(account, password)
        # 非必须（String）当值为字符串true时，响应中包含所有提交的msgid
        self.needallresp = needallresp
        # data
        self.data = data

    def parseDict(self):
        temp = self.data
        res = {"account": self.account, "password": self.password, "needallresp": self.needallresp, "data": []}
        for cont in temp:
            res["data"].append(cont.parseDict())
        return res

# 文本外呼发送data
class TextVoiceData(BaseJsonable):
    def __init__(self, msgid, callee, text, playmode, calltype, playtimes, speakper, params):
        # 消息编号ID，必须唯一，不可为空，最大长度64位
        self.msgid = msgid
        # 被叫号码。只能有一个号码。
        self.callee = callee
        # 验证码内容，只允许4~8位的数字验证码
        self.text = text
        # 放音模式： 0-只播放文本 1-只播放语音文件 ：2—先播放文本再文件，3—先播放文件再文本
        self.playmode = playmode
        # 外呼类型：1-验证码呼叫 2-语音文件呼叫  3-文本、文件混合呼叫
        self.calltype = calltype
        # 播放次数：1~2次
        self.playtimes = playtimes
        # 发声人类型（播放文本内容使用）汉小宇=B1, 汉小美=B0, 汉逍遥=B3, 汉丫丫=B4,不传使用默认发音人
        self.speaker = speakper
        # 终端客户自定义参数params  {}
        self.params = params


# 混合外呼参数
class MixVoiceParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, needallresp, data):
        super().__init__(account, password)
        # 非必须（String）当值为字符串true时，响应中包含所有提交的msgid
        self.needallresp = needallresp
        # data
        self.data = data

    def parseDict(self):
        temp = self.data
        res = {"account": self.account, "password": self.password, "needallresp": self.needallresp, "data": []}
        for cont in temp:
            res["data"].append(cont.parseDict())
        return res

# 混合外呼发送data
class MixVoiceData(BaseJsonable):
    def __init__(self, msgid, callee, medianame, text, playmode, calltype, params):
        # 消息编号ID，必须唯一，不可为空，最大长度64位
        self.msgid = msgid
        # 被叫号码。只能有一个号码。
        self.callee = callee
        # 待播放的语音文件名称，多个文件时用英文分号隔开（不带扩展名）。
        self.medianame = medianame
        # 待呼叫的文本内容
        self.text = text
        # 放音模式： 0-只播放文本 1-只播放语音文件 ：2—先播放文本再文件，3—先播放文件再文本
        self.playmode = playmode
        # 外呼类型：1-验证码呼叫 2-语音文件呼叫  3-文本、文件混合呼叫
        self.calltype = calltype
        # 终端客户自定义参数params  {}
        self.params = params


# 语音文件验证码外呼参数
class MediaCaptchaParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, needallresp, data):
        super().__init__(account, password)
        # 非必须（String）当值为字符串true时，响应中包含所有提交的msgid
        self.needallresp = needallresp
        # data
        self.data = data

    def parseDict(self):
        temp = self.data
        res = {"account": self.account, "password": self.password, "needallresp": self.needallresp, "data": []}
        for cont in temp:
            res["data"].append(cont.parseDict())
        return res

# 语音文件验证码外呼发送data
class MediaCaptchaData(BaseJsonable):
    def __init__(self, msgid, callee, medianame, text, playmode, calltype):
        # 消息编号ID，必须唯一，不可为空，最大长度64位
        self.msgid = msgid
        # 被叫号码。只能有一个号码。
        self.callee = callee
        # 待播放的语音文件名称，多个文件时用英文分号隔开（不带扩展名）。
        self.medianame = medianame
        # 验证码内容，只允许4~8位的数字验证码
        self.text = text
        # 放音模式： 0-只播放文本 1-只播放语音文件 ：2—先播放文本再文件，3—先播放文件再文本
        self.playmode = playmode
        # 外呼类型：1-验证码呼叫 2-语音文件呼叫  3-文本、文件混合呼叫
        self.calltype = calltype


# 语音文件外呼参数
class MediaVoiceParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, needallresp, data):
        super().__init__(account, password)
        # 非必须（String）当值为字符串true时，响应中包含所有提交的msgid
        self.needallresp = needallresp
        # data
        self.data = data

    def parseDict(self):
        temp = self.data
        res = {"account": self.account, "password": self.password, "needallresp": self.needallresp, "data": []}
        for cont in temp:
            res["data"].append(cont.parseDict())
        return res

# 语音文件外呼发送data
class MediaVoiceData(BaseJsonable):
    def __init__(self, msgid, callee, medianame, playmode, calltype, params):
        # 消息编号ID，必须唯一，不可为空，最大长度64位
        self.msgid = msgid
        # 被叫号码。只能有一个号码。
        self.callee = callee
        # 待播放的语音文件名称，多个文件时用英文分号隔开（不带扩展名）。
        self.medianame = medianame
        # 放音模式： 0-只播放文本 1-只播放语音文件 ：2—先播放文本再文件，3—先播放文件再文本
        self.playmode = playmode
        # 外呼类型：1-验证码呼叫 2-语音文件呼叫  3-文本、文件混合呼叫
        self.calltype = calltype
        # 终端客户自定义参数params  {}
        self.params = params


# 语音文件上传参数
class VocMediaUploadParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, filename, filedata):
        super().__init__(account, password)
        # 语音文件名称，包含文件后缀，长度不超过32位
        self.filename = filename
        # 文件格式要求：wav格式的文件，位速 128kbps，音频采样大小16位，频道 1(单声道)，音频采样级别 8 kHz，音频格式 PCM
        # 语音文件二进制数据base64编码后的字符串，文件大小建议不超过2M
        self.filedata = filedata


# 隐号AXB参数
class PhoneAXBParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, msgid, phoneA, phoneB, expiration):
        super().__init__(account, password)
        # 消息编号ID，必须唯一，不可为空，最大长度64位
        self.msgid = msgid
        # 真实号码A
        self.phoneA = phoneA
        # 真实号码B
        self.phoneB = phoneB
        # 过期时间，单位秒(最大不超过15天)
        self.expiration = expiration


# 隐号AXN参数
class PhoneAXNParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, msgid, phoneA, expiration):
        super().__init__(account, password)
        # 消息编号ID，必须唯一，不可为空，最大长度64位
        self.msgid = msgid
        # 真实号码A
        self.phoneA = phoneA
        # 过期时间，单位秒(最大不超过15天)
        self.expiration = expiration


# 隐号AXxYB参数
class PhoneAXxYBParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, msgid, phoneA, phoneX, phoneXx, calldisplay, expiration):
        super().__init__(account, password)
        # 消息编号ID，必须唯一，不可为空，最大长度64位
        self.msgid = msgid
        # 真实号码A
        self.phoneA = phoneA
        # 客户可以指定隐号也可以为空
        self.phoneX = phoneX
        # 隐号的分机号，指定隐号后才必填该参数，分机号规则：4位数，0000到9999共10000个
        self.phoneXx = phoneXx
        # 来显控制,当其他号码为主叫时，是否在被叫 A 上显示其他号码的真实号码。
        # 0：不显示真实号码；1：显示真实号码。默认是 0不显示真实号码
        self.calldisplay = calldisplay
        # 过期时间，单位秒(最大不超过15天)
        self.expiration = expiration


# 隐号AXYB参数
class PhoneAXYBParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, msgid, phoneA, phoneB, phoneX, servicetype, expiration):
        super().__init__(account, password)
        # 消息编号ID，必须唯一，不可为空，最大长度64位
        self.msgid = msgid
        # 真实号码A
        self.phoneA = phoneA
        # 真实号码B
        self.phoneB = phoneB
        # XYB模式下必填
        self.phoneX = phoneX
        # 0为AX模式（自动分配Y）、1为XYB模式（已使用AX或AXYB模式的情况下再分配一个Y）、2为AXYB模式
        self.servicetype = servicetype
        # 过期时间，单位秒(最大不超过15天)
        self.expiration = expiration


# 释放隐号参数
class PhoneReleaseParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, msgid, phone, deletetype, phoneXx):
        super().__init__(account, password)
        # 对应请求隐号时msgid
        self.msgid = msgid
        # 需要解绑号码,只能释放X号码
        self.phone = phone
        # 0为AXB模式、1为AXN模式、2为AXYB模式、3为AXxYB模式
        self.deletetype = deletetype
        # AXxYB类型时必填，X号码的分机号
        self.phoneXx = phoneXx


# 隐号报告参数
class PhoneReportParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password):
        super().__init__(account, password)
