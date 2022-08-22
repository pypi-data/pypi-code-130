"""
  模块描述：隐号 模块
  @author 8526
  @date 2022-05-12 13:53:05
  版权所有 Copyright www.dahantc.com
"""

import json

import requests

import common.util as util
import voice.conf as conf
import voice.param as param
import voice.response as res


# 隐号呼叫client
class HiddenNumberSmsClient:
    def __init__(self, base_url):
        if base_url is None:
            base_url = conf.BASE_URL
        self.base_url = base_url

    # 提供一个号码，让A手机可以通过X号码和B进行呼叫,B手机可以通过X号码和A进行呼叫。
    def getPhoneAXB(self, params):
        if type(params) != param.PhoneAXBParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数PhoneAXBParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_AXB, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.phoneAXBResponseDecoder(json.loads(result.content))

    # 提供一个号码，让任意号码可以通过X号码和A手机进行呼叫。
    def getPhoneAXN(self, params):
        if type(params) != param.PhoneAXNParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数PhoneAXNParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_AXN, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.phoneAXNResponseDecoder(json.loads(result.content))

    # 提供一个Y号码，A手机可以通过Y号码和B进行呼叫，同时提供一个X号码，让B手机可以通过X号码和A进行呼叫
    def getPhoneAXYB(self, params):
        if type(params) != param.PhoneAXYBParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数PhoneAXYBParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_AXYB, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.phoneAXYBResponseDecoder(json.loads(result.content))

    # 提供一个Y号码，A手机可以通过Y号码和B进行呼叫，同时提供一个X号码，让B手机可以通过X号码和A进行呼叫
    def getPhoneAXxYB(self, params):
        if type(params) != param.PhoneAXxYBParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数PhoneAXxYBParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_AXxYB, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.phoneAXxYBResponseDecoder(json.loads(result.content))

    # 隐号释放
    def numberDelete(self, params):
        if type(params) != param.PhoneReleaseParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数PhoneReleaseParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_H_DELETE, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.phoneReleaseResponseDecoder(json.loads(result.content))

    # 隐号状态报告获取
    def getReport(self, params):
        if type(params) != param.PhoneReportParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数PhoneReportParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_H_REPORT, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.phoneReportResponseDecoder(json.loads(result.content))


if __name__ == '__main__':
    pwdMd5 = util.md5Encode("456.com")
    account = "dhst8526"

    hclient = HiddenNumberSmsClient('http://voice.3tong.net')
    axb = param.PhoneAXBParam(account, pwdMd5, None, '162292292', '162292292', 200202)
    # print(hclient.getPhoneAXB(axb))

    axn = param.PhoneAXNParam(account, pwdMd5, None, '162292292', 200202)
    # print(hclient.getPhoneAXB(axn))

    axyb = param.PhoneAXYBParam(account, pwdMd5, None, '162292292', '162292292', '162292292', 0, 200202)
    # print(hclient.getPhoneAXYB(axyb))

    axxyb = param.PhoneAXxYBParam(account, pwdMd5, None, '162292292', '162292292', '162292292', 0, 200202)
    # print(hclient.getPhoneAXxYB(axxyb))

    numrelease = param.PhoneReleaseParam(account, pwdMd5, None, '162292292', 0, None)
    # print(hclient.numberDelete(numrelease))

    report = param.PhoneReportParam(account, pwdMd5)
    print(hclient.getReport(report))
