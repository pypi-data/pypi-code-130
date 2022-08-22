"""
  模块描述：shorturl接口参数
  @author 8526
  @date 2022-05-11 14:15:33
  版权所有 Copyright www.dahantc.com
"""

import common.entity as entity


class BaseJsonable(object):

    def parseDict(self):
        d = {}
        d.update(self.__dict__)
        return d


class ShortUrlGetParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, url, days):
        super().__init__(account, password)
        # 用户的长地址
        self.url = url
        # 短地址有效天数，默认值5，最大值60，参数无效时使用默认值，选填
        self.days = days


class ShortUrlGet4WechatAppletParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, url, days, wxImgUrl):
        super().__init__(account, password)
        # 用户的长地址
        # 如果想要获取微信的短地址则
        # 微信openlink，weixin: // 开头，微信小程序跳转地址需客户提前用微信api获取openlink，
        # 获取方式参考：
        # https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/url-scheme/urlscheme.generate.html
        self.url = url
        # 短地址有效天数，默认值5，最大值60，参数无效时使用默认值，选填
        self.days = days
        # 跳转小程序H5页面图片地址，如不填则直接跳转至小程序，建议大小(750*1100) 。
        # 跳转的时候会先显示H5页面，然后跳转之微信小程序。
        self.wxImgUrl = wxImgUrl


class ShortUrlSendParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, url, days, sign, content, sendtime, phonesFile):
        super().__init__(account, password)
        # 用户的长地址，需要在内容中出现，确保与内容中的地址一致，
        self.url = url
        # 短地址有效天数，默认值5，最大值60，参数无效时使用默认值，选填
        self.days = days
        # 短信签名，该签名需要提前报备，生效后方可使用，不可修改，示例如：【大汉三通】，必填（可为空，为空时需将sign放在content开头）
        self.sign = sign
        # 短信内容，最多1000个汉字，内容中不要出现【】[]这两种方括号，该字符为签名专用，必填
        self.content = content
        # 短信定时发送时间，不填则为立即发送，格式：yyyy-MM-dd HH:mm:ss,选填
        self.sendtime = sendtime
        # 号码文件，格式为zip，大小不超过20M，解压之后为1个或多个txt文本文件，文本文件每行一个号码，必填
        self.phonesFile = phonesFile
