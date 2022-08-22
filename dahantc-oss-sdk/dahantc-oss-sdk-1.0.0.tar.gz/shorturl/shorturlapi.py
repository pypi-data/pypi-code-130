"""
  模块描述：短链接api 模块
  @author 8526
  @date 2022-05-11 13:53:05
  版权所有 Copyright www.dahantc.com
"""
import json

import requests

import common.util as util
import shorturl.conf as conf
import shorturl.param as param
import shorturl.response as res


# 短链接调用客户端
class ShortUrlClient:
    def __init__(self, base_url):
        # 可配置的调用前缀
        if base_url is None:
            base_url = conf.BASE_URL
        self.base_url = base_url

    # 短链接获取方法
    def shortUrlGet(self, params):
        if type(params) != param.ShortUrlGetParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数ShortUrlGetParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.SHORT_URL_GET, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.shortUrlGetResponseDecoder(json.loads(result.content))

    # 微信小程序短链接获取方法
    def shortUrlGet4Applet(self, params):
        if type(params) != param.ShortUrlGet4WechatAppletParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数ShortUrlGet4WechatAppletParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.SHORT_URL_GET, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.shortUrlGet4AppletDecoder(json.loads(result.content))

    # 短链接发送方法
    def shortUrlSend(self, params):
        if type(params) != param.ShortUrlSendParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数ShortUrlSendParam")
        result = requests.post(self.base_url + conf.SHORT_URL_SEND,
                               headers={"Charset": "UTF-8", "Connection": "Keep-Alive"},
                               files=params.parseDict().get('phonesFile'), verify=False, data=params.parseDict())
        return res.shortUrlSendResponseDecoder(json.loads(result.content))


if __name__ == '__main__':
    pwdMd5 = util.md5Encode("456.com")
    account = "dhst8526"
    client = ShortUrlClient('http://180.168.192.126:16766')
    # shortUrlGetParam = param.ShortUrlGetParam(account, pwdMd5, 'http://www.baidu.com', '4', None)
    # res = client.shortUrlGet(shortUrlGetParam)
    # print(res.__dict__)
    files = {"phonesFile": ("p.zip", open("C:\\temp\\p.zip", "rb"), "application/zip")}
    shortUrlSendParam = param.ShortUrlSendParam(account, pwdMd5, 'https://www.baidu.com', 4, '【大汉三通】',
                                                '测试内容,点击https://www.baidu.com快', None, {"phonesFile": (
            "p.zip", open("C:\\temp\\p.zip", "rb"), "application/zip")})
    res1 = client.shortUrlSend(shortUrlSendParam)
    print(res1.__dict__)
