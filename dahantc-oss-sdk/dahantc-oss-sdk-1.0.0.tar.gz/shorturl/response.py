"""
  模块描述：接口响应
  @author 8526
  @date 2022-05-11 14:15:33
  版权所有 Copyright www.dahantc.com
"""


# 短地址获取响应
class ShortUrlGetResponse:
    def __init__(self, result, desc, shortUrl):
        # 该次请求提交结果
        self.result = result
        # 描述
        self.desc = desc
        # 长地址对应的短地址，只有result为0时才有值
        self.shortUrl = shortUrl


# 微信小程序短地址获取响应
class ShortUrlGet4AppletResponse:
    def __init__(self, result, desc, shortUrl):
        # 该次请求提交结果
        self.result = result
        # 描述
        self.desc = desc
        # 长地址对应的短地址，只有result为0时才有值
        self.shortUrl = shortUrl


# 短地址发送响应
class ShortUrlSendResponse:
    def __init__(self, msgid, result, desc, failPhones):
        # 发送记录id
        self.msgid = msgid
        # 该次请求提交结果
        self.result = result
        # 描述
        self.desc = desc
        # 如果提交的号码中含有错误（格式）号码将在此显示
        self.failPhones = failPhones


def shortUrlGetResponseDecoder(obj):
    if obj is None:
        return None
    return ShortUrlGetResponse(obj.get('result'), obj.get('desc'), obj.get('shortUrl'))


def shortUrlGet4AppletDecoder(obj):
    if obj is None:
        return None
    return ShortUrlGet4AppletResponse(obj.get('result'), obj.get('desc'), obj.get('shortUrl'))


def shortUrlSendResponseDecoder(obj):
    if obj is None:
        return None
    return ShortUrlSendResponse(obj.get('msgid'), obj.get('result'), obj.get('desc'), obj.get('failPhones'))
