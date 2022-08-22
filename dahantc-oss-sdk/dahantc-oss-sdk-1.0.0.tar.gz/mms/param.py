"""
  模块描述：彩信接口参数
  @author 8526
  @date 2022-05-12 10:45:33
  版权所有 Copyright www.dahantc.com
"""


class BaseJsonable(object):

    def parseDict(self):
        d = {}
        d.update(self.__dict__)
        return d


# 彩信参数
class MmsSendParam(BaseJsonable):
    def __init__(self, head, body):
        # 消息集合
        self.head = head
        self.body = body

    def parseDict(self):
        res = {"head": self.head.parseDict(), "body": self.body.parseDict()}
        return res


# 请求参数Head
class MmsHead(BaseJsonable):
    def __init__(self, cmdId, account, password):
        # 命令ID
        self.cmdId = cmdId
        # 用户账号
        self.account = account
        # 用户密码
        self.password = password


# 请求参数Body
class MmsSendBody(BaseJsonable):
    submitMsg = []

    def __init__(self, submitMsg):
        # 消息集合
        self.submitMsg = submitMsg

    def parseDict(self):
        res = []
        for cont in self.submitMsg:
            res.append({"submitMsg": cont.parseDict()})
        return res


# 彩信提交消息内容
class SubmitMsg(BaseJsonable):
    def __init__(self, phone, title, content, msgid, subcode):
        # 一个或多个接收该彩信消息的手机号；手机号之间用英文逗号(,)隔开，不能有重复的手机号码；
        self.phone = phone
        # 彩信标题(发彩信时有效，不能含有特殊字符),必填
        self.title = title
        # 彩信内容：彩信文件压缩成zip文件（zip文件小于90k），
        # 再对该文件进行BASE64编码（zip模板在相关示例的java彩信示例的resource文件有），必填
        self.content = content
        # 本MT彩信包的唯一标识，32位UUID，可选
        self.msgid = msgid
        # 扩展子码，可选
        self.subcode = subcode


# 彩信报告
class MmsReportParam(BaseJsonable):
    def __init__(self, head):
        self.head = head

    def parseDict(self):
        res = {"head": self.head.parseDict()}
        return res
